"""
Database models for the hyper-personalized customer support chatbot.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


def generate_uuid() -> str:
    """Generate a UUID string for SQLite compatibility."""
    return str(uuid4())


class Customer(Base):
    """Customer model with personalization data."""
    
    __tablename__ = "customers"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    name = Column(String(255), nullable=False)
    masked_phone = Column(String(50), nullable=False, index=True)
    masked_email = Column(String(255), nullable=False, index=True)
    preferences = Column(JSON, default=lambda: {})
    purchase_history = Column(JSON, default=lambda: [])
    loyalty_tier = Column(String(50), default="bronze", nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    interactions = relationship("Interaction", back_populates="customer", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Customer(id={self.id}, name={self.name}, loyalty_tier={self.loyalty_tier})>"


class Store(Base):
    """Store model with location and operational data."""
    
    __tablename__ = "stores"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    name = Column(String(255), nullable=False)
    store_type = Column(String(50), nullable=False, default="cafe")  # cafe, restaurant, fast_food, bakery, etc.
    cuisine_type = Column(String(50), nullable=True)  # indian, italian, chinese, american, etc.
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    open_hours = Column(JSON, default=lambda: {})
    current_promotions = Column(JSON, default=lambda: [])
    inventory = Column(JSON, default=lambda: {})
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    documents = relationship("Document", back_populates="store", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="store")
    
    def __repr__(self) -> str:
        return f"<Store(id={self.id}, name={self.name}, lat={self.latitude}, lon={self.longitude})>"


class Document(Base):
    """Document model for RAG system with embeddings stored as JSON."""
    
    __tablename__ = "documents"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    document_id = Column(String(36), unique=True, default=generate_uuid, index=True)
    store_id = Column(String(36), ForeignKey("stores.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)
    embedding = Column(JSON, nullable=True)  # Store embeddings as JSON array
    doc_metadata = Column(JSON, default=lambda: {})  # Renamed from metadata to avoid conflict
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    store = relationship("Store", back_populates="documents")
    
    def __repr__(self) -> str:
        return f"<Document(id={self.id}, title={self.title}, store_id={self.store_id})>"


class Interaction(Base):
    """Customer interaction tracking for personalization."""
    
    __tablename__ = "interactions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    store_id = Column(String(36), ForeignKey("stores.id"), nullable=True, index=True)  # Optional store reference
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    response_time = Column(Float, default=0.0)
    timestamp = Column(DateTime, server_default=func.now())
    interaction_metadata = Column(JSON, default=lambda: {})  # Renamed to avoid conflict
    
    # Relationships
    customer = relationship("Customer", back_populates="interactions")
    store = relationship("Store", back_populates="interactions")
    
    def __repr__(self) -> str:
        return f"<Interaction(id={self.id}, customer_id={self.customer_id}, store_id={self.store_id})>"