"""
Pydantic schemas for request/response models and data validation.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


# Base schemas
class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    class Config:
        from_attributes = True
        use_enum_values = True
        validate_assignment = True


class LocationData(BaseModel):
    """Location data for geospatial queries."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")


# Chat schemas
class ChatMessage(BaseModel):
    """Individual chat message."""
    role: str = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = None


class ChatRequest(BaseSchema):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    customer_id: Optional[str] = Field(None, description="Customer ID for personalization")
    store_id: Optional[str] = Field(None, description="Store ID for context")
    conversation_history: List[ChatMessage] = Field(default_factory=list, description="Previous messages")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context (can include latitude, longitude)")
    
    @validator("conversation_history")
    def validate_history_length(cls, v):
        if len(v) > 50:  # Limit conversation history
            return v[-50:]
        return v
    
    @validator("metadata")
    def validate_location_data(cls, v):
        """Validate location data if provided."""
        if 'latitude' in v and 'longitude' in v:
            lat = v['latitude']
            lon = v['longitude']
            if not (-90 <= lat <= 90):
                raise ValueError("Latitude must be between -90 and 90")
            if not (-180 <= lon <= 180):
                raise ValueError("Longitude must be between -180 and 180")
        return v


class ChatResponse(BaseSchema):
    """Response model for chat endpoint."""
    response: str = Field(..., description="Chatbot response")
    customer_id: Optional[str] = Field(None, description="Customer ID used")
    store_id: Optional[str] = Field(None, description="Store ID used")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="RAG sources used")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Response confidence")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    session_id: Optional[str] = Field(None, description="Session identifier")


# Customer schemas
class CustomerProfile(BaseSchema):
    """Customer profile response schema."""
    id: str
    name: str
    masked_phone: str
    masked_email: str
    preferences: Dict[str, Any] = Field(default_factory=dict)
    purchase_history: List[Dict[str, Any]] = Field(default_factory=list)
    loyalty_tier: str
    created_at: datetime
    updated_at: datetime
    interaction_count: Optional[int] = Field(None, description="Total interactions")
    last_interaction: Optional[datetime] = Field(None, description="Last interaction timestamp")


class CustomerCreate(BaseSchema):
    """Schema for creating a new customer."""
    name: str = Field(..., min_length=1, max_length=255)
    masked_phone: str = Field(..., min_length=1, max_length=50)
    masked_email: str = Field(..., min_length=1, max_length=255)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    purchase_history: List[Dict[str, Any]] = Field(default_factory=list)
    loyalty_tier: str = Field(default="bronze")


class CustomerUpdate(BaseSchema):
    """Schema for updating customer information."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    preferences: Optional[Dict[str, Any]] = None
    purchase_history: Optional[List[Dict[str, Any]]] = None
    loyalty_tier: Optional[str] = None


# Store schemas
class Store(BaseSchema):
    """Store response schema."""
    id: str
    name: str
    store_type: str = Field(..., description="Type of establishment (cafe, restaurant, fast_food, bakery, etc.)")
    cuisine_type: Optional[str] = Field(None, description="Cuisine type (indian, italian, chinese, american, etc.)")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    open_hours: Dict[str, Any] = Field(default_factory=dict)
    current_promotions: List[Dict[str, Any]] = Field(default_factory=list)
    inventory: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    distance_km: Optional[float] = Field(None, description="Distance from query point")


class StoreCreate(BaseSchema):
    """Schema for creating a new store."""
    name: str = Field(..., min_length=1, max_length=255)
    store_type: str = Field("cafe", description="Type of establishment")
    cuisine_type: Optional[str] = Field(None, description="Cuisine type")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    open_hours: Dict[str, Any] = Field(default_factory=dict)
    current_promotions: List[Dict[str, Any]] = Field(default_factory=list)
    inventory: Dict[str, Any] = Field(default_factory=dict)


class NearbyStoresRequest(BaseSchema):
    """Request model for nearby stores search."""
    latitude: float = Field(..., ge=-90, le=90, description="User latitude")
    longitude: float = Field(..., ge=-180, le=180, description="User longitude")
    radius_km: float = Field(default=10.0, ge=0.1, le=100.0, description="Search radius in kilometers")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum number of stores to return")
    store_types: Optional[List[str]] = Field(None, description="Filter by store types (cafe, restaurant, fast_food, bakery)")
    cuisine_types: Optional[List[str]] = Field(None, description="Filter by cuisine types (indian, italian, chinese, american)")
    
    @validator("store_types")
    def validate_store_types(cls, v):
        if v is not None:
            valid_types = ["cafe", "restaurant", "fast_food", "bakery", "pizza", "dessert", "juice_bar", "food_truck"]
            for store_type in v:
                if store_type not in valid_types:
                    raise ValueError(f"Invalid store type: {store_type}. Valid types: {valid_types}")
        return v
    
    @validator("cuisine_types")
    def validate_cuisine_types(cls, v):
        if v is not None:
            valid_cuisines = ["indian", "italian", "chinese", "american", "mexican", "thai", "japanese", "mediterranean", "continental"]
            for cuisine_type in v:
                if cuisine_type not in valid_cuisines:
                    raise ValueError(f"Invalid cuisine type: {cuisine_type}. Valid cuisines: {valid_cuisines}")
        return v


# Document schemas
class DocumentCreate(BaseSchema):
    """Schema for creating a document."""
    store_id: str
    doc_type: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Document(BaseSchema):
    """Document response schema."""
    id: str
    store_id: str
    doc_type: str
    content: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


# Interaction schemas
class InteractionCreate(BaseSchema):
    """Schema for creating an interaction."""
    customer_id: str
    store_id: Optional[str] = None
    interaction_type: str = Field(..., min_length=1, max_length=100)
    context: Dict[str, Any] = Field(default_factory=dict)


class Interaction(BaseSchema):
    """Interaction response schema."""
    id: str
    customer_id: str
    store_id: Optional[str]
    interaction_type: str
    context: Dict[str, Any]
    created_at: datetime


# Health check schema
class HealthCheck(BaseSchema):
    """Health check response schema."""
    status: str = Field(default="healthy")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="1.0.0")
    database: str = Field(default="unknown")
    redis: str = Field(default="unknown")
    uptime_seconds: Optional[float] = None


# Error schemas
class ErrorDetail(BaseSchema):
    """Error detail schema."""
    message: str
    error_code: Optional[str] = None
    field: Optional[str] = None


class ErrorResponse(BaseSchema):
    """Standard error response schema."""
    detail: str
    errors: Optional[List[ErrorDetail]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None