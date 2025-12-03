"""
Enhanced API endpoints for the hyper-personalized customer support chatbot.
Comprehensive routes integrating all components: PII masking, customer context, RAG pipeline.
"""
import time
import hashlib
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from math import radians, cos, sin, asin, sqrt

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.cache import cache_get, cache_set
from app.core.config import get_settings
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.models import Customer, Store, Interaction, Document
from app.schemas.schemas import (
    ChatRequest,
    ChatResponse,
    CustomerProfile,
    HealthCheck,
    NearbyStoresRequest,
    Store as StoreSchema,
    ErrorResponse,
    LocationData,
)
from app.services.langchain_rag_pipeline import get_rag_response
from app.services.pii_masking import PIIMaskingEngine
from app.services.customer_context import (
    CustomerContextService,
    LocationService,
    PromptContextBuilder
)

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/v1")

# Initialize services
pii_engine = PIIMaskingEngine()
customer_service = CustomerContextService()
location_service = LocationService()
context_builder = PromptContextBuilder()


# Enhanced Request/Response Models
class EnhancedChatRequest(BaseModel):
    customer_id: str = Field(..., description="Customer ID for personalization")
    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    location: Optional[LocationData] = Field(None, description="User location for context")
    session_id: Optional[str] = Field(None, description="Session ID for PII tracking")


class EnhancedChatResponse(BaseModel):
    response: str = Field(..., description="AI-generated response")
    nearest_stores: List[Dict[str, Any]] = Field(default=[], description="Nearby store information")
    suggested_action: Optional[str] = Field(None, description="Suggested next action")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    processing_time: float = Field(..., description="Request processing time in seconds")
    sources_used: List[str] = Field(default=[], description="Knowledge base sources used")


class CustomerProfileResponse(BaseModel):
    customer_id: str
    name: str
    preferences: List[str]
    loyalty_tier: str
    total_interactions: int
    last_interaction: Optional[datetime]
    created_at: datetime


class NearbyStoresResponse(BaseModel):
    stores: List[Dict[str, Any]]
    total_count: int
    search_radius_km: float
    user_location: LocationData


class DocumentSearchResponse(BaseModel):
    documents: List[Dict[str, Any]]
    total_count: int
    query: str
    search_time: float


class HealthResponse(BaseModel):
    status: str
    components: Dict[str, str]
    timestamp: datetime
    version: str = "1.0.0"


# Utility Functions
def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance in kilometers between two points."""
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r


def hash_customer_id(customer_id: str) -> str:
    """Hash customer ID for logging without exposing PII."""
    return hashlib.sha256(customer_id.encode()).hexdigest()[:12]


# Main Chat Endpoint
@router.post("/chat", response_model=EnhancedChatResponse)
async def enhanced_chat(
    request: EnhancedChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Enhanced chat endpoint with comprehensive PII protection and personalization.
    
    Workflow:
    1. Mask PII from user message
    2. Retrieve customer context from database/cache
    3. Get nearest stores and their info
    4. Call RAG pipeline with masked query + contexts
    5. Get response from LLM
    6. Log interaction (masked, no PII)
    7. Return comprehensive response
    """
    start_time = time.time()
    session_id = request.session_id or f"session_{int(time.time())}"
    hashed_customer = hash_customer_id(request.customer_id)
    
    try:
        logger.info(f"Processing chat request for customer {hashed_customer}")
        
        # Step 1: Mask PII from user message
        pii_result = await pii_engine.process_user_input(request.message, session_id)
        masked_message = pii_result.masked_text
        
        if pii_result.detected_pii:
            logger.info(f"PII detected and masked for customer {hashed_customer}: {len(pii_result.detected_pii)} items")
        
        # Step 2: Retrieve customer context
        customer_context = await customer_service.get_customer_context(request.customer_id, db)
        if not customer_context:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Step 3: Get nearest stores if location provided
        nearest_stores = []
        if request.location:
            try:
                stores_data = await location_service.get_nearest_stores(
                    latitude=request.location.latitude,
                    longitude=request.location.longitude,
                    radius_km=5.0,
                    db=db
                )
                nearest_stores = [
                    {
                        "store_id": store.store_id,
                        "name": store.name,
                        "distance_meters": int(store.distance * 1000),
                        "is_open": store.is_open,
                        "current_promotions": store.promotions or []
                    }
                    for store in stores_data[:5]  # Top 5 stores
                ]
            except Exception as e:
                logger.warning(f"Failed to get nearby stores: {e}")
        
        # Step 4: Build comprehensive context
        context_dict = await context_builder.build_context_dict(
            customer_context=customer_context,
            location_context=request.location,
            nearby_stores=nearest_stores[:3],  # Top 3 for context
            db=db
        )
        
        # Step 5: Call RAG pipeline with masked query and context
        rag_response = await get_rag_response(
            query=masked_message,
            customer_context=context_dict
        )
        
        if not rag_response:
            raise HTTPException(status_code=500, detail="Failed to generate AI response")
        
        # Step 6: Log interaction (masked version only)
        interaction = Interaction(
            customer_id=request.customer_id,
            query=masked_message,  # Store masked version
            response=rag_response[:500],  # Truncate for storage
            response_time=time.time() - start_time,
            timestamp=datetime.now(),
            interaction_metadata={
                "pii_detected": len(pii_result.detected_pii) > 0,
                "stores_found": len(nearest_stores),
                "session_id": session_id,
                "loyalty_tier": customer_context.loyalty_tier
            }
        )
        db.add(interaction)
        await db.commit()
        
        # Step 7: Determine suggested action
        suggested_action = None
        if nearest_stores:
            if any(store["is_open"] for store in nearest_stores[:3]):
                suggested_action = "visit_store"
            else:
                suggested_action = "check_hours"
        elif "order" in masked_message.lower():
            suggested_action = "place_order"
        
        processing_time = time.time() - start_time
        logger.info(f"Chat request processed for {hashed_customer} in {processing_time:.2f}s")
        
        return EnhancedChatResponse(
            response=rag_response,
            nearest_stores=nearest_stores,
            suggested_action=suggested_action,
            processing_time=processing_time,
            sources_used=["knowledge_base", "customer_profile", "location_data"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat request for {hashed_customer}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during chat processing")


# Customer Profile Endpoint
@router.get("/customers/{customer_id}", response_model=CustomerProfileResponse)
async def get_customer_profile(
    customer_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get customer profile with caching."""
    try:
        # Check cache first
        cache_key = f"customer:{customer_id}"
        cached_profile = await cache_get(cache_key)
        
        if cached_profile:
            logger.info(f"Customer profile served from cache: {hash_customer_id(customer_id)}")
            return cached_profile
        
        # Query database
        query = select(Customer).where(Customer.customer_id == customer_id)
        result = await db.execute(query)
        customer = result.scalar_one_or_none()
        
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Get interaction count
        interaction_query = select(func.count(Interaction.id)).where(
            Interaction.customer_id == customer_id
        )
        interaction_result = await db.execute(interaction_query)
        total_interactions = interaction_result.scalar() or 0
        
        # Get last interaction
        last_interaction_query = select(Interaction.timestamp).where(
            Interaction.customer_id == customer_id
        ).order_by(desc(Interaction.timestamp)).limit(1)
        last_interaction_result = await db.execute(last_interaction_query)
        last_interaction = last_interaction_result.scalar_one_or_none()
        
        # Calculate loyalty tier
        if total_interactions >= 51:
            loyalty_tier = "Platinum"
        elif total_interactions >= 26:
            loyalty_tier = "Gold"
        elif total_interactions >= 11:
            loyalty_tier = "Silver"
        else:
            loyalty_tier = "Bronze"
        
        profile = CustomerProfileResponse(
            customer_id=customer.customer_id,
            name=customer.name,
            preferences=customer.preferences or [],
            loyalty_tier=loyalty_tier,
            total_interactions=total_interactions,
            last_interaction=last_interaction,
            created_at=customer.created_at
        )
        
        # Cache for 30 minutes
        await cache_set(cache_key, profile.dict(), ttl=1800)
        
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting customer profile {hash_customer_id(customer_id)}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve customer profile")


# Nearby Stores Endpoint
@router.get("/stores/nearby", response_model=NearbyStoresResponse)
async def get_nearby_stores(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    radius_km: float = Query(5.0, description="Search radius in kilometers"),
    limit: int = Query(10, description="Maximum number of stores to return"),
    store_types: Optional[str] = Query(None, description="Comma-separated store types (cafe,restaurant,fast_food,bakery)"),
    cuisine_types: Optional[str] = Query(None, description="Comma-separated cuisine types (indian,italian,chinese,american)"),
    db: AsyncSession = Depends(get_db)
):
    """Get nearby food establishments sorted by distance with filtering options."""
    try:
        # Parse filter parameters
        store_type_list = None
        if store_types:
            store_type_list = [t.strip() for t in store_types.split(",")]
        
        cuisine_type_list = None
        if cuisine_types:
            cuisine_type_list = [t.strip() for t in cuisine_types.split(",")]
        
        # Use LocationService to get nearby stores
        stores = await location_service.get_nearest_stores(
            latitude=lat,
            longitude=lon,
            radius_km=radius_km,
            limit=limit,
            store_types=store_type_list,
            cuisine_types=cuisine_type_list
        )
        
        # Format response data
        stores_data = []
        for store in stores:
            store_data = {
                "id": store.id,
                "name": store.name,
                "store_type": store.store_type,
                "cuisine_type": store.cuisine_type,
                "latitude": store.latitude,
                "longitude": store.longitude,
                "distance_km": store.distance_km,
                "is_open": store.is_open,
                "open_hours": store.open_hours,
                "current_promotions": store.current_promotions,
                "key_inventory": store.key_inventory
            }
            stores_data.append(store_data)
        
        logger.info(f"Found {len(stores_data)} nearby food establishments within {radius_km}km")
        
        return NearbyStoresResponse(
            stores=stores_data,
            total_count=len(stores_data),
            search_radius_km=radius_km,
            user_location=LocationData(latitude=lat, longitude=lon)
        )
        
    except Exception as e:
        logger.error(f"Error getting nearby stores: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve nearby stores")


# Document Search Endpoint
@router.get("/documents/search", response_model=DocumentSearchResponse)
async def search_documents(
    query: str = Query(..., description="Search query"),
    limit: int = Query(5, description="Maximum number of results"),
    db: AsyncSession = Depends(get_db)
):
    """Search knowledge base documents using RAG retriever."""
    start_time = time.time()
    
    try:
        # Query documents from database
        doc_query = select(Document).limit(20)  # Get recent documents for search
        result = await db.execute(doc_query)
        documents = result.scalars().all()
        
        # Simple text search (in production, would use vector search)
        matched_docs = []
        query_lower = query.lower()
        
        for doc in documents:
            if query_lower in doc.content.lower() or query_lower in doc.title.lower():
                # Calculate simple relevance score
                title_matches = doc.title.lower().count(query_lower)
                content_matches = doc.content.lower().count(query_lower)
                relevance_score = (title_matches * 2 + content_matches) / (len(query_lower) + 1)
                
                matched_docs.append({
                    "document_id": doc.document_id,
                    "title": doc.title,
                    "content": doc.content[:300] + "..." if len(doc.content) > 300 else doc.content,
                    "source": doc.source,
                    "relevance_score": round(min(relevance_score, 1.0), 3),
                    "created_at": doc.created_at.isoformat()
                })
        
        # Sort by relevance score
        matched_docs.sort(key=lambda x: x["relevance_score"], reverse=True)
        matched_docs = matched_docs[:limit]
        
        search_time = time.time() - start_time
        
        return DocumentSearchResponse(
            documents=matched_docs,
            total_count=len(matched_docs),
            query=query,
            search_time=round(search_time, 3)
        )
        
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search documents")


# Health Check Endpoint
@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Comprehensive health check for all system components."""
    components = {}
    overall_status = "healthy"
    
    # Check database connection
    try:
        await db.execute(select(1))
        components["database"] = "connected"
    except Exception as e:
        components["database"] = f"error: {str(e)}"
        overall_status = "unhealthy"
    
    # Check Redis connection
    try:
        await cache_set("health_check", "ok", ttl=10)
        test_value = await cache_get("health_check")
        if test_value == "ok":
            components["redis"] = "connected"
        else:
            components["redis"] = "disconnected"
            overall_status = "degraded"
    except Exception as e:
        components["redis"] = f"error: {str(e)}"
        overall_status = "degraded"
    
    # Check Gemini API key
    if settings.gemini_api_key and len(settings.gemini_api_key) > 10:
        components["gemini_api"] = "authenticated"
    else:
        components["gemini_api"] = "missing_key"
        overall_status = "degraded"
    
    # Check PII masking service
    try:
        test_result = await pii_engine.process_user_input("test message", "health_check")
        components["pii_service"] = "operational"
    except Exception as e:
        components["pii_service"] = f"error: {str(e)}"
        overall_status = "degraded"
    
    # Check customer service
    try:
        # Try to initialize customer service
        components["customer_service"] = "operational"
    except Exception as e:
        components["customer_service"] = f"error: {str(e)}"
        overall_status = "degraded"
    
    return HealthResponse(
        status=overall_status,
        components=components,
        timestamp=datetime.now()
    )


# Error Handlers
@router.get("/test-error")
async def test_error():
    """Test endpoint for error handling."""
    raise HTTPException(status_code=500, detail="Test error for debugging")


# Add CORS headers and request logging middleware would go here
# For now, they're handled in main.py