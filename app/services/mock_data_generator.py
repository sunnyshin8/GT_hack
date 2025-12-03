"""
Mock data generation script for Indian users and diverse food establishments.
Generates realistic data for cafes, restaurants, fast food, bakeries and more using Faker library with Indian locale.
"""
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
from uuid import uuid4

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import Customer, Store, Document, Interaction
from app.core.database import get_db
from app.core.logging import get_logger
from app.services.rag_service import rag_service

# Initialize Faker with Indian locale
fake = Faker('en_IN')
logger = get_logger(__name__)

# Indian city coordinates for food establishments
INDIAN_CITIES = [
    {"name": "Delhi", "lat": 28.6139, "lng": 77.2090},
    {"name": "Mumbai", "lat": 19.0760, "lng": 72.8777},
    {"name": "Bangalore", "lat": 12.9716, "lng": 77.5946},
    {"name": "Hyderabad", "lat": 17.3850, "lng": 78.4867},
    {"name": "Pune", "lat": 18.5204, "lng": 73.8567}
]

# Common Indian first and last names for more realistic data
INDIAN_FIRST_NAMES = [
    "Rajesh", "Priya", "Amit", "Sneha", "Vikram", "Pooja", "Arjun", "Kavya",
    "Rohit", "Anita", "Suresh", "Meera", "Kiran", "Divya", "Anil", "Riya",
    "Manoj", "Sita", "Deepak", "Nisha", "Rahul", "Lakshmi", "Ajay", "Sunita",
    "Prakash", "Geeta", "Vinod", "Radha", "Ashok", "Shanti", "Ravi", "Indira",
    "Mohan", "Parvati", "Krishna", "Saraswati", "Ganesh", "Durga", "Shiva", "Kali"
]

INDIAN_LAST_NAMES = [
    "Sharma", "Kumar", "Singh", "Gupta", "Patel", "Agarwal", "Jain", "Yadav",
    "Shah", "Verma", "Mishra", "Tiwari", "Pandey", "Srivastava", "Chopra", "Malhotra",
    "Bansal", "Mittal", "Agrawal", "Joshi", "Mehta", "Kapoor", "Bhatia", "Saxena",
    "Goyal", "Arora", "Sethi", "Goel", "Khanna", "Tandon", "Sinha", "Chandra"
]

# Store types and their characteristics
STORE_TYPES = {
    "cafe": {
        "names": ["Starbucks", "Cafe Coffee Day", "Barista", "Third Wave Coffee", "Blue Tokai", "Tata Starbucks"],
        "cuisines": ["american", "continental"],
        "inventory_categories": ["hot_coffee", "cold_coffee", "tea", "pastries", "sandwiches", "cookies"]
    },
    "restaurant": {
        "names": ["Punjabi Dhaba", "South Indian Express", "Maharaja Restaurant", "Spice Route", "Royal Palace"],
        "cuisines": ["indian", "south_indian", "north_indian", "punjabi"],
        "inventory_categories": ["dal", "rice", "roti", "curries", "biryani", "desserts"]
    },
    "fast_food": {
        "names": ["McDonald's", "KFC", "Burger King", "Domino's Pizza", "Pizza Hut", "Subway"],
        "cuisines": ["american", "italian"],
        "inventory_categories": ["burgers", "fries", "pizza", "chicken", "soft_drinks", "desserts"]
    },
    "bakery": {
        "names": ["Monginis", "Cake Studio", "Bread & More", "Sweet Treats", "Golden Bakery"],
        "cuisines": ["continental", "indian"],
        "inventory_categories": ["breads", "cakes", "pastries", "cookies", "donuts", "custom_cakes"]
    },
    "pizza": {
        "names": ["Domino's", "Pizza Hut", "Papa John's", "La Pinoz", "Oven Story"],
        "cuisines": ["italian", "american"],
        "inventory_categories": ["pizza", "garlic_bread", "pasta", "soft_drinks", "desserts"]
    },
    "juice_bar": {
        "names": ["Fresh Junction", "Juice World", "Healthy Bytes", "Fruit Express", "Green Smoothie"],
        "cuisines": ["healthy", "continental"],
        "inventory_categories": ["fresh_juices", "smoothies", "salads", "healthy_snacks", "protein_shakes"]
    }
}

# Comprehensive inventory items for different store types
INVENTORY_ITEMS = {
    "hot_coffee": ["cappuccino", "latte", "americano", "espresso", "macchiato"],
    "cold_coffee": ["iced_coffee", "cold_brew", "frappuccino", "iced_latte"],
    "tea": ["chai", "green_tea", "herbal_tea", "masala_chai", "earl_grey"],
    "pastries": ["croissant", "danish", "muffin", "scone", "eclair"],
    "sandwiches": ["club_sandwich", "grilled_chicken", "veg_sandwich", "paneer_sandwich"],
    "dal": ["dal_tadka", "dal_makhani", "sambar", "rasam", "dal_fry"],
    "rice": ["biryani", "pulao", "jeera_rice", "coconut_rice", "lemon_rice"],
    "curries": ["butter_chicken", "paneer_makhani", "chole", "rajma", "palak_paneer"],
    "pizza": ["margherita", "pepperoni", "veg_supreme", "chicken_tikka", "paneer_pizza"],
    "burgers": ["chicken_burger", "veg_burger", "cheese_burger", "maharaja_mac"],
    "breads": ["white_bread", "brown_bread", "multigrain", "pav", "buns"],
    "fresh_juices": ["orange_juice", "apple_juice", "mixed_fruit", "pomegranate", "watermelon"]
}


def generate_masked_phone() -> str:
    """Generate Indian masked phone number format."""
    visible_digits = f"{random.randint(1000, 9999)}"
    return f"+91-XXXX-XXXX-{visible_digits}"


def generate_masked_email(name: str) -> str:
    """Generate masked email from name."""
    first_initial = name.split()[0][0].lower()
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "rediffmail.com"]
    domain = random.choice(domains)
    asterisks_count = random.randint(4, 8)
    return f"{first_initial}{'*' * asterisks_count}@{domain}"


def generate_purchase_history() -> List[Dict[str, Any]]:
    """Generate realistic purchase history for last 90 days."""
    purchases = []
    num_purchases = random.randint(5, 15)
    
    for _ in range(num_purchases):
        purchase_date = fake.date_time_between(
            start_date=datetime.now() - timedelta(days=90),
            end_date=datetime.now()
        )
        
        # Random beverage and snack combinations
        items = []
        total_amount = 0
        
        # Always include a beverage
        beverage = random.choice([
            {"item": "Cappuccino", "price": 280, "category": "hot_coffee"},
            {"item": "Latte", "price": 320, "category": "hot_coffee"},
            {"item": "Americano", "price": 240, "category": "hot_coffee"},
            {"item": "Cold Brew", "price": 300, "category": "cold_coffee"},
            {"item": "Frappuccino", "price": 380, "category": "frappuccino"},
            {"item": "Green Tea", "price": 200, "category": "tea"},
            {"item": "Hot Chocolate", "price": 290, "category": "hot_chocolate"},
        ])
        items.append(beverage)
        total_amount += beverage["price"]
        
        # Sometimes add snacks
        if random.random() > 0.4:
            snack = random.choice([
                {"item": "Chicken Sandwich", "price": 450, "category": "sandwiches"},
                {"item": "Blueberry Muffin", "price": 180, "category": "muffins"},
                {"item": "Chocolate Croissant", "price": 220, "category": "pastries"},
                {"item": "Caesar Salad", "price": 380, "category": "salads"},
                {"item": "Chocolate Chip Cookie", "price": 120, "category": "cookies"},
            ])
            items.append(snack)
            total_amount += snack["price"]
        
        # Sometimes add merchandise
        if random.random() > 0.8:
            merch = random.choice([
                {"item": "Starbucks Mug", "price": 800, "category": "mugs"},
                {"item": "Tumbler", "price": 1200, "category": "tumblers"},
                {"item": "Coffee Beans", "price": 950, "category": "coffee_beans"},
            ])
            items.append(merch)
            total_amount += merch["price"]
        
        purchase = {
            "date": purchase_date.isoformat(),
            "amount": total_amount,
            "items": items,
            "store_location": random.choice([city["name"] for city in INDIAN_CITIES]),
            "payment_method": random.choice(["card", "upi", "cash", "wallet"])
        }
        purchases.append(purchase)
    
    return sorted(purchases, key=lambda x: x["date"], reverse=True)


def determine_loyalty_tier(purchase_history: List[Dict[str, Any]]) -> str:
    """Determine loyalty tier based on purchase history."""
    total_spent = sum(purchase["amount"] for purchase in purchase_history)
    purchase_count = len(purchase_history)
    
    if total_spent >= 15000 or purchase_count >= 12:
        return "platinum"
    elif total_spent >= 8000 or purchase_count >= 8:
        return "gold"
    elif total_spent >= 3000 or purchase_count >= 5:
        return "silver"
    else:
        return "bronze"


def generate_customer_preferences() -> Dict[str, Any]:
    """Generate realistic customer preferences."""
    return {
        "store_format": random.choice(["casual", "formal"]),
        "favorite_categories": random.sample(BEVERAGE_CATEGORIES + SNACK_CATEGORIES, k=random.randint(2, 4)),
        "preferred_time_slots": random.choice([
            ["morning", "afternoon"], ["evening"], ["morning"], ["afternoon", "evening"]
        ]),
        "dietary_restrictions": random.choice([[], ["vegetarian"], ["vegan"], ["gluten_free"]]),
        "notification_preferences": {
            "email": random.choice([True, False]),
            "sms": random.choice([True, False]),
            "push": random.choice([True, False])
        },
        "language_preference": random.choice(["english", "hindi", "regional"])
    }


def generate_mock_customers(count: int = 100) -> List[Dict[str, Any]]:
    """Generate mock Indian customers."""
    customers = []
    
    for _ in range(count):
        # Generate realistic Indian name
        first_name = random.choice(INDIAN_FIRST_NAMES)
        last_name = random.choice(INDIAN_LAST_NAMES)
        full_name = f"{first_name} {last_name}"
        
        purchase_history = generate_purchase_history()
        loyalty_tier = determine_loyalty_tier(purchase_history)
        
        customer = {
            "id": str(uuid4()),
            "name": full_name,
            "masked_phone": generate_masked_phone(),
            "masked_email": generate_masked_email(full_name),
            "preferences": generate_customer_preferences(),
            "purchase_history": purchase_history,
            "loyalty_tier": loyalty_tier,
            "created_at": fake.date_time_between(
                start_date=datetime.now() - timedelta(days=180),
                end_date=datetime.now() - timedelta(days=30)
            ),
            "updated_at": fake.date_time_between(
                start_date=datetime.now() - timedelta(days=30),
                end_date=datetime.now()
            )
        }
        customers.append(customer)
    
    logger.info(f"Generated {len(customers)} mock customers")
    return customers


def generate_store_inventory() -> Dict[str, Any]:
    """Generate realistic Starbucks inventory."""
    return {
        "beverages": {
            "hot_cocoa": random.randint(50, 150),
            "coffee_beans": random.randint(20, 80),
            "cold_brew": random.randint(30, 100),
            "espresso_shots": random.randint(100, 300),
            "syrups": random.randint(40, 120),
            "milk_alternatives": random.randint(25, 75)
        },
        "food": {
            "sandwiches": random.randint(20, 60),
            "pastries": random.randint(30, 90),
            "cookies": random.randint(40, 120),
            "muffins": random.randint(25, 75),
            "salads": random.randint(15, 45)
        },
        "merchandise": {
            "mugs": random.randint(20, 60),
            "tumblers": random.randint(15, 45),
            "t_shirts": random.randint(25, 75),
            "bags": random.randint(10, 30),
            "coffee_beans_retail": random.randint(30, 90)
        }
    }


def generate_current_promotions() -> List[Dict[str, Any]]:
    """Generate current promotions for stores."""
    promotions = [
        {
            "code": "WELCOME10",
            "title": "Welcome Offer",
            "description": "10% off on your first order",
            "discount": 10,
            "discount_type": "percentage",
            "valid_until": "2025-12-31",
            "minimum_order": 200,
            "applicable_categories": ["all"]
        },
        {
            "code": "FESTIVE20",
            "title": "Festive Special",
            "description": "20% off on beverages during festival season",
            "discount": 20,
            "discount_type": "percentage",
            "valid_until": "2025-01-15",
            "minimum_order": 300,
            "applicable_categories": ["beverages"]
        },
        {
            "code": "STUDENT15",
            "title": "Student Discount",
            "description": "15% off for students with valid ID",
            "discount": 15,
            "discount_type": "percentage",
            "valid_until": "2025-06-30",
            "minimum_order": 150,
            "applicable_categories": ["beverages", "snacks"]
        }
    ]
    
    # Return 1-3 random promotions
    return random.sample(promotions, k=random.randint(1, 3))


def generate_store_hours() -> Dict[str, str]:
    """Generate store operating hours."""
    return {
        "monday": "07:00-22:00",
        "tuesday": "07:00-22:00", 
        "wednesday": "07:00-22:00",
        "thursday": "07:00-22:00",
        "friday": "07:00-23:00",  # Extended hours on Friday
        "saturday": "07:00-23:00",  # Extended hours on Saturday
        "sunday": "08:00-22:00"  # Late start on Sunday
    }


def generate_store_hours_by_type(store_type: str) -> Dict[str, str]:
    """Generate store operating hours based on store type."""
    if store_type == "cafe":
        return {
            "monday": "07:00-22:00",
            "tuesday": "07:00-22:00", 
            "wednesday": "07:00-22:00",
            "thursday": "07:00-22:00",
            "friday": "07:00-23:00",
            "saturday": "07:00-23:00",
            "sunday": "08:00-22:00"
        }
    elif store_type == "restaurant":
        return {
            "monday": "11:00-23:00",
            "tuesday": "11:00-23:00", 
            "wednesday": "11:00-23:00",
            "thursday": "11:00-23:00",
            "friday": "11:00-01:00",  # Late nights on Friday
            "saturday": "11:00-01:00",
            "sunday": "11:00-23:00"
        }
    elif store_type == "fast_food":
        return {
            "monday": "10:00-23:00",
            "tuesday": "10:00-23:00", 
            "wednesday": "10:00-23:00",
            "thursday": "10:00-23:00",
            "friday": "10:00-01:00",
            "saturday": "10:00-01:00",
            "sunday": "10:00-23:00"
        }
    elif store_type == "bakery":
        return {
            "monday": "06:00-21:00",
            "tuesday": "06:00-21:00", 
            "wednesday": "06:00-21:00",
            "thursday": "06:00-21:00",
            "friday": "06:00-21:00",
            "saturday": "06:00-22:00",
            "sunday": "07:00-21:00"
        }
    else:
        # Default hours
        return generate_store_hours()


def generate_current_promotions_by_type(store_type: str) -> List[Dict[str, Any]]:
    """Generate promotions specific to store type."""
    if store_type == "cafe":
        promotions = [
            {
                "code": "COFFEE20",
                "title": "Coffee Lover's Deal",
                "description": "20% off on all coffee beverages",
                "discount": 20,
                "discount_type": "percentage",
                "valid_until": "2025-01-15",
                "minimum_order": 200,
                "applicable_categories": ["hot_coffee", "cold_coffee"]
            },
            {
                "code": "COMBO15",
                "title": "Coffee & Pastry Combo",
                "description": "15% off when you buy coffee with pastry",
                "discount": 15,
                "discount_type": "percentage",
                "valid_until": "2025-12-31",
                "minimum_order": 300,
                "applicable_categories": ["hot_coffee", "pastries"]
            }
        ]
    elif store_type == "restaurant":
        promotions = [
            {
                "code": "FAMILY25",
                "title": "Family Feast",
                "description": "25% off on orders above ₹1000",
                "discount": 25,
                "discount_type": "percentage",
                "valid_until": "2025-01-31",
                "minimum_order": 1000,
                "applicable_categories": ["all"]
            },
            {
                "code": "LUNCH10",
                "title": "Lunch Special",
                "description": "10% off on lunch orders (12 PM - 4 PM)",
                "discount": 10,
                "discount_type": "percentage",
                "valid_until": "2025-06-30",
                "minimum_order": 400,
                "applicable_categories": ["dal", "rice", "curries"]
            }
        ]
    elif store_type == "fast_food":
        promotions = [
            {
                "code": "BURGER30",
                "title": "Burger Bonanza",
                "description": "30% off on all burgers",
                "discount": 30,
                "discount_type": "percentage",
                "valid_until": "2025-01-20",
                "minimum_order": 200,
                "applicable_categories": ["burgers"]
            }
        ]
    else:
        promotions = [
            {
                "code": "FRESH20",
                "title": "Fresh & Healthy",
                "description": "20% off on fresh items",
                "discount": 20,
                "discount_type": "percentage",
                "valid_until": "2025-12-31",
                "minimum_order": 250,
                "applicable_categories": ["all"]
            }
        ]
    
    return random.sample(promotions, k=random.randint(1, min(2, len(promotions))))


def generate_store_inventory_by_type(store_type: str, categories: List[str]) -> Dict[str, Any]:
    """Generate inventory based on store type and categories."""
    inventory = {}
    
    for category in categories:
        if category in INVENTORY_ITEMS:
            items = {}
            for item in INVENTORY_ITEMS[category]:
                items[item] = {
                    "available": random.choice([True, False, True, True]),  # 75% chance available
                    "price": random.randint(150, 800),  # Prices in INR
                    "description": f"Fresh {item.replace('_', ' ').title()}",
                    "popularity": random.randint(1, 5)
                }
            inventory[category] = items
    
    return inventory


def generate_mock_stores() -> List[Dict[str, Any]]:
    """Generate diverse food establishments in Indian cities."""
    stores = []
    
    # Generate 3-5 stores per city with diverse types
    for city in INDIAN_CITIES:
        num_stores_in_city = random.randint(3, 5)
        
        for i in range(num_stores_in_city):
            # Select random store type
            store_type = random.choice(list(STORE_TYPES.keys()))
            store_config = STORE_TYPES[store_type]
            
            # Add variation to coordinates for realistic placement
            lat_variation = random.uniform(-0.05, 0.05)
            lng_variation = random.uniform(-0.05, 0.05)
            
            # Generate store name
            base_name = random.choice(store_config["names"])
            area_suffix = random.choice(["Central", "Mall", "Express", "Deluxe", "Plaza", "Junction"])
            store_name = f"{base_name} {city['name']} {area_suffix}"
            
            # Select cuisine type
            cuisine_type = random.choice(store_config["cuisines"])
            
            store = {
                "id": str(uuid4()),
                "name": store_name,
                "store_type": store_type,
                "cuisine_type": cuisine_type,
                "latitude": city["lat"] + lat_variation,
                "longitude": city["lng"] + lng_variation,
                "open_hours": generate_store_hours_by_type(store_type),
                "current_promotions": generate_current_promotions_by_type(store_type),
                "inventory": generate_store_inventory_by_type(store_type, store_config["inventory_categories"]),
                "created_at": fake.date_time_between(
                    start_date=datetime.now() - timedelta(days=365),
                    end_date=datetime.now() - timedelta(days=180)
                ),
                "updated_at": fake.date_time_between(
                    start_date=datetime.now() - timedelta(days=7),
                    end_date=datetime.now()
                )
            }
            stores.append(store)
    
    logger.info(f"Generated {len(stores)} diverse food establishments across {len(INDIAN_CITIES)} cities")
    return stores


def generate_store_documents(stores: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate documents for each store for RAG functionality."""
    documents = []
    
    faq_templates = [
        "Q: What are your store hours? A: We are open {hours} daily. Hours may vary on holidays.",
        "Q: Do you accept UPI payments? A: Yes, we accept UPI, cards, cash, and digital wallets.",
        "Q: Do you have WiFi? A: Yes, free WiFi is available for all customers. Ask staff for password.",
        "Q: Can I customize my drink? A: Absolutely! We offer various syrups, milk alternatives, and sizes.",
        "Q: Do you have vegan options? A: Yes, we have soy milk, almond milk, and oat milk alternatives.",
    ]
    
    menu_templates = [
        "Our signature beverages include Cappuccino (₹280), Latte (₹320), Americano (₹240), and Cold Brew (₹300). All prices include taxes.",
        "Fresh food options: Chicken Sandwich (₹450), Blueberry Muffin (₹180), Caesar Salad (₹380), Chocolate Croissant (₹220).",
        "Seasonal specials: Pumpkin Spice Latte, Iced Caramel Macchiato, and limited-time holiday beverages available.",
        "Merchandise collection: Branded mugs starting at ₹800, Tumblers at ₹1200, Fresh coffee beans at ₹950.",
    ]
    
    for store in stores:
        store_id = store["id"]
        city_name = store["name"].split()[1]  # Extract city name
        
        # FAQ documents
        for i, faq in enumerate(faq_templates):
            if "{hours}" in faq:
                hours = f"7 AM to 10 PM"  # Simplified format
                faq = faq.format(hours=hours)
            
            doc = {
                "id": str(uuid4()),
                "store_id": store_id,
                "doc_type": "faq",
                "content": faq,
                "metadata": {
                    "category": "customer_service",
                    "priority": "high",
                    "city": city_name,
                    "language": "english"
                },
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            documents.append(doc)
        
        # Menu documents
        for i, menu in enumerate(menu_templates):
            doc = {
                "id": str(uuid4()),
                "store_id": store_id,
                "doc_type": "menu",
                "content": menu,
                "metadata": {
                    "category": "menu_information",
                    "priority": "medium",
                    "city": city_name,
                    "language": "english"
                },
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            documents.append(doc)
        
        # Store-specific promotion document
        promotions_text = f"Current promotions at Starbucks {city_name}: " + \
                         ", ".join([f"{promo['title']} - {promo['description']}" 
                                  for promo in store["current_promotions"]])
        
        doc = {
            "id": str(uuid4()),
            "store_id": store_id,
            "doc_type": "promotion",
            "content": promotions_text,
            "metadata": {
                "category": "promotions",
                "priority": "high",
                "city": city_name,
                "valid_until": "2025-12-31"
            },
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        documents.append(doc)
    
    logger.info(f"Generated {len(documents)} store documents")
    return documents


async def seed_database(customers: List[Dict[str, Any]] = None, 
                       stores: List[Dict[str, Any]] = None) -> Dict[str, int]:
    """
    Seed the SQLite database with mock data.
    
    Args:
        customers: List of customer dictionaries. If None, generates 100 customers.
        stores: List of store dictionaries. If None, generates 5 stores.
    
    Returns:
        Dictionary with counts of inserted records.
    """
    logger.info("Starting database seeding process")
    
    # Generate data if not provided
    if customers is None:
        customers = generate_mock_customers(100)
    if stores is None:
        stores = generate_mock_stores()
    
    # Generate documents for stores
    documents = generate_store_documents(stores)
    
    counts = {"customers": 0, "stores": 0, "documents": 0, "interactions": 0}
    
    async for db in get_db():
        try:
            # Insert customers
            for customer_data in customers:
                # Check if customer already exists
                result = await db.execute(
                    select(Customer).where(Customer.id == customer_data["id"])
                )
                if not result.scalar_one_or_none():
                    customer = Customer(**customer_data)
                    db.add(customer)
                    counts["customers"] += 1
            
            # Insert stores
            for store_data in stores:
                # Check if store already exists
                result = await db.execute(
                    select(Store).where(Store.id == store_data["id"])
                )
                if not result.scalar_one_or_none():
                    store = Store(**store_data)
                    db.add(store)
                    counts["stores"] += 1
            
            # Commit stores and customers first
            await db.commit()
            
            # Insert documents with embeddings
            for doc_data in documents:
                # Generate embedding if RAG service is available
                if rag_service.model:
                    try:
                        embedding = rag_service.embed_text(doc_data["content"])
                        doc_data["embedding"] = embedding
                    except Exception as e:
                        logger.warning(f"Failed to generate embedding: {e}")
                        doc_data["embedding"] = None
                
                document = Document(**doc_data)
                db.add(document)
                counts["documents"] += 1
            
            # Generate some sample interactions
            customer_ids = [c["id"] for c in customers]
            store_ids = [s["id"] for s in stores]
            
            for _ in range(min(50, len(customer_ids) * 2)):  # Generate some interactions
                interaction_data = {
                    "id": str(uuid4()),
                    "customer_id": random.choice(customer_ids),
                    "store_id": random.choice(store_ids),
                    "interaction_type": random.choice(["chat", "purchase_inquiry", "support", "feedback"]),
                    "context": {
                        "channel": random.choice(["web", "mobile", "in_store"]),
                        "session_duration": random.randint(60, 600),
                        "resolved": random.choice([True, False])
                    },
                    "created_at": fake.date_time_between(
                        start_date=datetime.now() - timedelta(days=30),
                        end_date=datetime.now()
                    )
                }
                
                interaction = Interaction(**interaction_data)
                db.add(interaction)
                counts["interactions"] += 1
            
            await db.commit()
            logger.info("Database seeding completed successfully", extra=counts)
            return counts
            
        except Exception as e:
            logger.error(f"Database seeding failed: {e}")
            await db.rollback()
            raise
        finally:
            break  # Exit the async generator loop


def save_to_json(customers: List[Dict[str, Any]], stores: List[Dict[str, Any]], 
                filepath_prefix: str = "mock_data") -> None:
    """Save generated data to JSON files."""
    
    # Convert datetime objects to strings for JSON serialization
    def serialize_datetime(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    # Save customers
    customers_file = f"{filepath_prefix}_users.json"
    with open(customers_file, 'w', encoding='utf-8') as f:
        json.dump(customers, f, indent=2, ensure_ascii=False, default=serialize_datetime)
    
    # Save stores
    stores_file = f"{filepath_prefix}_stores.json"
    with open(stores_file, 'w', encoding='utf-8') as f:
        json.dump(stores, f, indent=2, ensure_ascii=False, default=serialize_datetime)
    
    logger.info(f"Data saved to {customers_file} and {stores_file}")


def create_sample_data() -> Dict[str, Any]:
    """Quick function to create sample data for testing."""
    logger.info("Creating sample data for testing")
    
    customers = generate_mock_customers(10)  # Small sample
    stores = generate_mock_stores()
    
    return {
        "customers": customers,
        "stores": stores,
        "summary": {
            "total_customers": len(customers),
            "total_stores": len(stores),
            "loyalty_tiers": {tier: sum(1 for c in customers if c["loyalty_tier"] == tier) 
                            for tier in ["bronze", "silver", "gold", "platinum"]},
            "cities": [store["name"].split()[1] for store in stores]
        }
    }


if __name__ == "__main__":
    # Example usage
    import asyncio
    
    async def main():
        # Initialize RAG service for embeddings
        try:
            await rag_service.initialize()
        except Exception as e:
            logger.warning(f"RAG service initialization failed: {e}")
        
        # Generate and save data
        customers = generate_mock_customers(100)
        stores = generate_mock_stores()
        
        # Save to JSON files
        save_to_json(customers, stores)
        
        # Seed database
        counts = await seed_database(customers, stores)
        print(f"Database seeded with: {counts}")
        
        # Create sample data
        sample = create_sample_data()
        print(f"Sample data summary: {sample['summary']}")
    
    asyncio.run(main())