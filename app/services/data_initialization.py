"""
Service for initializing the database with mock data.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Customer, Store, Document, Interaction
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)


class DataInitializationService:
    """Service to initialize database with sample data."""
    
    @staticmethod
    async def create_mock_customers(db: AsyncSession) -> List[str]:
        """Create mock customers and return their IDs."""
        customers_data = [
            {
                "name": "Alice Johnson",
                "masked_phone": "***-***-1234",
                "masked_email": "a***@email.com",
                "preferences": {
                    "communication_channel": "email",
                    "product_categories": ["electronics", "books"],
                    "notification_frequency": "weekly"
                },
                "purchase_history": [
                    {
                        "date": "2024-11-15",
                        "amount": 299.99,
                        "category": "electronics",
                        "product": "Bluetooth Headphones"
                    },
                    {
                        "date": "2024-10-22", 
                        "amount": 45.50,
                        "category": "books",
                        "product": "Programming Guide"
                    }
                ],
                "loyalty_tier": "gold"
            },
            {
                "name": "Bob Smith",
                "masked_phone": "***-***-5678",
                "masked_email": "b***@email.com",
                "preferences": {
                    "communication_channel": "sms",
                    "product_categories": ["clothing", "sports"],
                    "notification_frequency": "monthly"
                },
                "purchase_history": [
                    {
                        "date": "2024-11-20",
                        "amount": 89.99,
                        "category": "clothing",
                        "product": "Winter Jacket"
                    }
                ],
                "loyalty_tier": "silver"
            },
            {
                "name": "Carol Davis",
                "masked_phone": "***-***-9012",
                "masked_email": "c***@email.com",
                "preferences": {
                    "communication_channel": "email",
                    "product_categories": ["home", "garden"],
                    "notification_frequency": "daily"
                },
                "purchase_history": [
                    {
                        "date": "2024-11-25",
                        "amount": 156.75,
                        "category": "home",
                        "product": "Smart Thermostat"
                    },
                    {
                        "date": "2024-11-10",
                        "amount": 34.99,
                        "category": "garden",
                        "product": "Plant Fertilizer"
                    }
                ],
                "loyalty_tier": "platinum"
            }
        ]
        
        customer_ids = []
        for customer_data in customers_data:
            customer = Customer(**customer_data)
            db.add(customer)
            customer_ids.append(customer.id)
        
        await db.commit()
        logger.info(f"Created {len(customer_ids)} mock customers")
        return customer_ids
    
    @staticmethod
    async def create_mock_stores(db: AsyncSession) -> List[str]:
        """Create mock stores and return their IDs."""
        stores_data = [
            {
                "name": "Downtown Tech Store",
                "latitude": 40.7589,
                "longitude": -73.9851,
                "open_hours": {
                    "monday": "9:00-21:00",
                    "tuesday": "9:00-21:00",
                    "wednesday": "9:00-21:00",
                    "thursday": "9:00-21:00",
                    "friday": "9:00-22:00",
                    "saturday": "10:00-22:00",
                    "sunday": "11:00-20:00"
                },
                "current_promotions": [
                    {
                        "title": "Black Friday Sale",
                        "description": "30% off all electronics",
                        "valid_until": "2024-12-01",
                        "category": "electronics"
                    },
                    {
                        "title": "Free Shipping",
                        "description": "Free shipping on orders over $50",
                        "valid_until": "2024-12-31",
                        "category": "all"
                    }
                ],
                "inventory": {
                    "electronics": {
                        "laptops": 15,
                        "phones": 25,
                        "headphones": 40
                    },
                    "accessories": {
                        "cases": 100,
                        "cables": 200,
                        "chargers": 75
                    }
                }
            },
            {
                "name": "Midtown Fashion Outlet",
                "latitude": 40.7505,
                "longitude": -73.9934,
                "open_hours": {
                    "monday": "10:00-20:00",
                    "tuesday": "10:00-20:00",
                    "wednesday": "10:00-20:00",
                    "thursday": "10:00-21:00",
                    "friday": "10:00-21:00",
                    "saturday": "9:00-22:00",
                    "sunday": "11:00-19:00"
                },
                "current_promotions": [
                    {
                        "title": "Winter Collection",
                        "description": "New winter arrivals - 20% off",
                        "valid_until": "2024-12-15",
                        "category": "clothing"
                    }
                ],
                "inventory": {
                    "clothing": {
                        "shirts": 200,
                        "pants": 150,
                        "jackets": 80,
                        "dresses": 120
                    },
                    "shoes": {
                        "sneakers": 100,
                        "boots": 60,
                        "dress_shoes": 40
                    }
                }
            },
            {
                "name": "Brooklyn Home & Garden",
                "latitude": 40.6892,
                "longitude": -73.9442,
                "open_hours": {
                    "monday": "8:00-19:00",
                    "tuesday": "8:00-19:00",
                    "wednesday": "8:00-19:00",
                    "thursday": "8:00-19:00",
                    "friday": "8:00-20:00",
                    "saturday": "8:00-20:00",
                    "sunday": "9:00-18:00"
                },
                "current_promotions": [
                    {
                        "title": "Holiday Plants",
                        "description": "15% off all holiday decorations",
                        "valid_until": "2024-12-25",
                        "category": "garden"
                    }
                ],
                "inventory": {
                    "home": {
                        "furniture": 50,
                        "appliances": 30,
                        "decor": 200
                    },
                    "garden": {
                        "plants": 300,
                        "tools": 100,
                        "fertilizers": 80
                    }
                }
            }
        ]
        
        store_ids = []
        for store_data in stores_data:
            store = Store(**store_data)
            db.add(store)
            store_ids.append(store.id)
        
        await db.commit()
        logger.info(f"Created {len(store_ids)} mock stores")
        return store_ids
    
    @staticmethod
    async def create_mock_documents(db: AsyncSession, store_ids: List[str]) -> List[str]:
        """Create mock documents for stores and return their IDs."""
        documents_data = []
        
        # Documents for Downtown Tech Store
        if store_ids:
            documents_data.extend([
                {
                    "store_id": store_ids[0],
                    "doc_type": "faq",
                    "content": "Q: What is your return policy? A: We offer 30-day returns on all electronics with original receipt. Items must be in original condition and packaging.",
                    "metadata": {"category": "returns", "priority": "high"}
                },
                {
                    "store_id": store_ids[0], 
                    "doc_type": "product_info",
                    "content": "Our latest laptops feature Intel i7 processors, 16GB RAM, and 512GB SSD storage. Perfect for gaming and professional work. Starting at $999.",
                    "metadata": {"category": "laptops", "price_range": "999-2000"}
                },
                {
                    "store_id": store_ids[0],
                    "doc_type": "promotion",
                    "content": "Black Friday Special: 30% off all electronics including laptops, phones, and headphones. Plus free shipping on orders over $50. Limited time offer!",
                    "metadata": {"category": "electronics", "discount": "30%"}
                }
            ])
        
        # Documents for Midtown Fashion Outlet
        if len(store_ids) > 1:
            documents_data.extend([
                {
                    "store_id": store_ids[1],
                    "doc_type": "sizing_guide",
                    "content": "Size Guide: Small (S) fits chest 34-36 inches, Medium (M) fits 38-40 inches, Large (L) fits 42-44 inches. For best fit, measure around the fullest part of your chest.",
                    "metadata": {"category": "sizing", "gender": "unisex"}
                },
                {
                    "store_id": store_ids[1],
                    "doc_type": "care_instructions",
                    "content": "Care Instructions: Machine wash cold, tumble dry low heat, do not bleach. For wool items, dry clean only. Iron on low temperature if needed.",
                    "metadata": {"category": "care", "material": "various"}
                }
            ])
        
        # Documents for Brooklyn Home & Garden
        if len(store_ids) > 2:
            documents_data.extend([
                {
                    "store_id": store_ids[2],
                    "doc_type": "plant_care",
                    "content": "Winter Plant Care: Reduce watering frequency as plants enter dormancy. Provide adequate humidity and avoid cold drafts. Fertilize sparingly during winter months.",
                    "metadata": {"category": "plants", "season": "winter"}
                },
                {
                    "store_id": store_ids[2],
                    "doc_type": "delivery_info", 
                    "content": "Free delivery available for orders over $100 within 10 miles. Large furniture items require scheduled delivery appointment. Same-day delivery available for small items.",
                    "metadata": {"category": "delivery", "minimum_order": "100"}
                }
            ])
        
        document_ids = []
        for doc_data in documents_data:
            # Generate embedding for the document content
            if rag_service.model:
                embedding = rag_service.embed_text(doc_data["content"])
                doc_data["embedding"] = embedding
            
            document = Document(**doc_data)
            db.add(document)
            document_ids.append(document.id)
        
        await db.commit()
        logger.info(f"Created {len(document_ids)} mock documents")
        return document_ids
    
    @staticmethod
    async def create_mock_interactions(
        db: AsyncSession, 
        customer_ids: List[str], 
        store_ids: List[str]
    ) -> List[str]:
        """Create mock customer interactions and return their IDs."""
        if not customer_ids or not store_ids:
            return []
        
        interactions_data = [
            {
                "customer_id": customer_ids[0],
                "store_id": store_ids[0],
                "interaction_type": "chat",
                "context": {
                    "message": "I'm looking for a gaming laptop under $1500",
                    "response": "I'd recommend our Intel i7 model with RTX graphics for $1299. It's perfect for gaming and currently on sale!",
                    "satisfaction_rating": 5
                }
            },
            {
                "customer_id": customer_ids[1],
                "store_id": store_ids[1],
                "interaction_type": "purchase_inquiry",
                "context": {
                    "message": "Do you have winter jackets in size Large?",
                    "response": "Yes, we have several winter jackets in Large. Our new collection has 20% off this week!",
                    "products_shown": ["winter_jacket_1", "winter_jacket_2"]
                }
            },
            {
                "customer_id": customer_ids[2],
                "store_id": store_ids[2],
                "interaction_type": "support",
                "context": {
                    "message": "My smart thermostat isn't connecting to WiFi",
                    "response": "Let me help you troubleshoot. First, ensure your WiFi password is correct and the device is within range of your router.",
                    "issue_resolved": True
                }
            }
        ]
        
        interaction_ids = []
        for interaction_data in interactions_data:
            interaction = Interaction(**interaction_data)
            db.add(interaction)
            interaction_ids.append(interaction.id)
        
        await db.commit()
        logger.info(f"Created {len(interaction_ids)} mock interactions")
        return interaction_ids
    
    @staticmethod
    async def initialize_all_mock_data(db: AsyncSession) -> Dict[str, List[str]]:
        """Initialize all mock data and return IDs for reference."""
        logger.info("Starting mock data initialization")
        
        try:
            # Create customers first
            customer_ids = await DataInitializationService.create_mock_customers(db)
            
            # Create stores
            store_ids = await DataInitializationService.create_mock_stores(db)
            
            # Create documents (requires store IDs)
            document_ids = await DataInitializationService.create_mock_documents(db, store_ids)
            
            # Create interactions (requires customer and store IDs)
            interaction_ids = await DataInitializationService.create_mock_interactions(
                db, customer_ids, store_ids
            )
            
            result = {
                "customers": customer_ids,
                "stores": store_ids,
                "documents": document_ids,
                "interactions": interaction_ids
            }
            
            logger.info("Mock data initialization completed successfully", extra=result)
            return result
            
        except Exception as e:
            logger.error(f"Failed to initialize mock data: {e}")
            await db.rollback()
            raise


# Global instance
data_init_service = DataInitializationService()