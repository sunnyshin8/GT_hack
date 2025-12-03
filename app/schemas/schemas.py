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
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    
    @validator("conversation_history")
    def validate_history_length(cls, v):
        if len(v) > 50:  # Limit conversation history
            return v[-50:]
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