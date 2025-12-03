"""
API endpoints for the hyper-personalized customer support chatbot.
"""
import time
from datetime import datetime
from math import radians, cos, sin, asin, sqrt
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache_get, cache_set
from app.core.config import get_settings
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.models import Customer, Store, Interaction
from app.schemas.schemas import (
    ChatRequest,
    ChatResponse,
    CustomerProfile,
    HealthCheck,
    NearbyStoresRequest,
    Store as StoreSchema,
    ErrorResponse,
)
from app.services.langchain_rag_pipeline import get_rag_response
from app.services.pii_masking import mask_user_input, unmask_response
from app.services.customer_context import build_prompt_context

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter(prefix=settings.api_v1_prefix)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees).
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
) -> ChatResponse:
    """
    Main chat endpoint for customer support interactions.
    
    This is a placeholder implementation that will be expanded with:
    - RAG (Retrieval Augmented Generation) functionality
    - Customer personalization based on history
    - Store-specific context integration
    - Intent recognition and routing
    """
    start_time = time.time()
    
    logger.info(
        "Chat request received",
        customer_id=request.customer_id,
        store_id=request.store_id,
        message_length=len(request.message)
    )
    
    try:
        # Step 1: Process and mask PII in user input
        pii_result = await mask_user_input(request.message)
        masked_message = pii_result['masked_text']
        session_id = pii_result['session_id']
        
        # Log PII detection for security audit
        if pii_result['pii_count'] > 0:
            logger.info("PII detected in user input", 
                       extra={
                           "session_id": session_id,
                           "pii_count": pii_result['pii_count'],
                           "pii_types": [p['type'] for p in pii_result['pii_detected']]
                       })
        
        # Step 2: Build comprehensive context using location and customer data
        latitude = request.metadata.get('latitude')
        longitude = request.metadata.get('longitude')
        
        context = await build_prompt_context(
            customer_id=request.customer_id,
            latitude=latitude,
            longitude=longitude,
            store_id=request.store_id
        )
        
        # Step 3: Extract contexts for RAG pipeline
        customer_context = {
            "customer_name": context['customer_name'],
            "loyalty_tier": context['loyalty_tier'],
            "favorite_categories": context['favorite_categories']
        }
        
        location_context = {
            "distance_to_store": context['distance_to_store'],
            "store_name": context['store_name'],
            "weather": context['weather']
        }
        
        # Step 4: Generate response using RAG pipeline with masked input
        rag_response = await get_rag_response(
            masked_message,  # Use masked message for AI processing
            customer_context,
            location_context
        )
        
        response_text = rag_response.get("response", "I'm here to help! How can I assist you today?")
        sources = rag_response.get("sources", [])
        confidence = rag_response.get("confidence", 0.8)
        
        # Step 5: Unmask response if needed (for development - in production, keep masked)
        # For now, we'll keep the response as-is since it shouldn't contain user PII
        final_response = response_text
        
        # Step 6: Record interaction with masked data for privacy
        if request.customer_id:
            interaction = Interaction(
                customer_id=request.customer_id,
                store_id=request.store_id,
                interaction_type="chat",
                context={
                    "message_hash": pii_result.get('session_id'),  # Store session ID instead of actual message
                    "response": final_response[:500],  # Response should be safe
                    "pii_detected": pii_result['pii_count'] > 0,
                    "metadata": request.metadata,
                    "context_used": {
                        "weather": context.get('weather'),
                        "store": context.get('store_name'),
                        "loyalty_tier": context.get('loyalty_tier')
                    }
                }
            )
            db.add(interaction)
            await db.commit()
        
        processing_time = int((time.time() - start_time) * 1000)
        
        logger.info(
            "Chat response generated with PII protection",
            extra={
                "customer_id": request.customer_id,
                "store_id": request.store_id,
                "session_id": session_id,
                "processing_time_ms": processing_time,
                "pii_protected": pii_result['pii_count'] > 0,
                "context_enhanced": bool(latitude and longitude)
            }
        )
        
        return ChatResponse(
            response=final_response,
            customer_id=request.customer_id,
            store_id=request.store_id,
            sources=sources,  # RAG sources from knowledge base
            confidence_score=confidence,  # AI confidence score
            processing_time_ms=processing_time,
            session_id=session_id  # Return session ID for PII tracking
        )
        
    except Exception as e:
        logger.error("Chat processing error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request."
        )


@router.get("/health", response_model=HealthCheck)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthCheck:
    """
    Health check endpoint to verify system status.
    """
    try:
        # Test database connection
        await db.execute(select(1))
        db_status = "healthy"
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        db_status = "unhealthy"
    
    # Test Redis connection
    try:
        redis_status = "healthy"  # Will implement actual Redis check
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
        redis_status = "unhealthy"
    
    overall_status = "healthy" if db_status == "healthy" and redis_status == "healthy" else "degraded"
    
    return HealthCheck(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version="1.0.0",
        database=db_status,
        redis=redis_status
    )


@router.get("/customers/{customer_id}", response_model=CustomerProfile)
async def get_customer_profile(
    customer_id: str,
    db: AsyncSession = Depends(get_db)
) -> CustomerProfile:
    """
    Get customer profile with personalization data.
    """
    logger.info("Customer profile requested", customer_id=customer_id)
    
    # Try cache first
    cache_key = f"customer_profile:{customer_id}"
    cached_profile = await cache_get(cache_key)
    
    if cached_profile:
        logger.info("Customer profile served from cache", customer_id=customer_id)
        return CustomerProfile(**cached_profile)
    
    # Fetch from database
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id)
    )
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(
            status_code=404,
            detail=f"Customer with ID {customer_id} not found"
        )
    
    # Get interaction count and last interaction
    interaction_result = await db.execute(
        select(
            func.count(Interaction.id).label('interaction_count'),
            func.max(Interaction.created_at).label('last_interaction')
        ).where(Interaction.customer_id == customer_id)
    )
    interaction_data = interaction_result.first()
    
    profile = CustomerProfile(
        id=customer.id,
        name=customer.name,
        masked_phone=customer.masked_phone,
        masked_email=customer.masked_email,
        preferences=customer.preferences,
        purchase_history=customer.purchase_history,
        loyalty_tier=customer.loyalty_tier,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
        interaction_count=interaction_data.interaction_count or 0,
        last_interaction=interaction_data.last_interaction
    )
    
    # Cache the profile
    await cache_set(cache_key, profile.dict(), settings.customer_cache_ttl)
    
    logger.info("Customer profile fetched", customer_id=customer_id)
    return profile


@router.get("/stores/nearby", response_model=List[StoreSchema])
async def get_nearby_stores(
    latitude: float = Query(..., ge=-90, le=90, description="User latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="User longitude"), 
    radius_km: float = Query(10.0, ge=0.1, le=100.0, description="Search radius in kilometers"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of stores"),
    db: AsyncSession = Depends(get_db)
) -> List[StoreSchema]:
    """
    Find nearby stores based on location.
    
    Uses Haversine formula to calculate distances and returns stores within the specified radius.
    """
    logger.info(
        "Nearby stores requested",
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        limit=limit
    )
    
    # Create cache key for this location query
    cache_key = f"nearby_stores:{latitude:.4f}:{longitude:.4f}:{radius_km}:{limit}"
    cached_stores = await cache_get(cache_key)
    
    if cached_stores:
        logger.info("Nearby stores served from cache")
        return [StoreSchema(**store) for store in cached_stores]
    
    # Fetch all stores from database
    result = await db.execute(select(Store))
    all_stores = result.scalars().all()
    
    # Calculate distances and filter
    nearby_stores = []
    for store in all_stores:
        distance = haversine_distance(latitude, longitude, store.latitude, store.longitude)
        
        if distance <= radius_km:
            store_dict = {
                "id": store.id,
                "name": store.name,
                "latitude": store.latitude,
                "longitude": store.longitude,
                "open_hours": store.open_hours,
                "current_promotions": store.current_promotions,
                "inventory": store.inventory,
                "created_at": store.created_at,
                "updated_at": store.updated_at,
                "distance_km": round(distance, 2)
            }
            nearby_stores.append(store_dict)
    
    # Sort by distance and apply limit
    nearby_stores.sort(key=lambda x: x["distance_km"])
    nearby_stores = nearby_stores[:limit]
    
    # Cache results for a shorter time since location data can be dynamic
    await cache_set(cache_key, nearby_stores, settings.cache_ttl)
    
    logger.info("Nearby stores fetched", count=len(nearby_stores))
    return [StoreSchema(**store) for store in nearby_stores]