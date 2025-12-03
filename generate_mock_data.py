"""
Standalone script to generate mock data for the chatbot application.
Run this script to populate the database with Indian users and Starbucks stores.
"""
import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from app.services.mock_data_generator import (
    generate_mock_customers,
    generate_mock_stores,
    seed_database,
    save_to_json,
    create_sample_data
)
from app.services.rag_service import rag_service
from app.core.logging import configure_logging, get_logger

# Configure logging
configure_logging()
logger = get_logger(__name__)


async def main():
    """Main function to generate and seed mock data."""
    print("🚀 Starting Mock Data Generation for Indian Starbucks Chatbot")
    print("=" * 60)
    
    try:
        # Initialize RAG service for document embeddings
        print("📚 Initializing RAG service for document embeddings...")
        try:
            await rag_service.initialize()
            print("✅ RAG service initialized successfully")
        except Exception as e:
            print(f"⚠️  RAG service initialization failed: {e}")
            print("📝 Continuing without embeddings...")
        
        # Generate mock data
        print("\n👥 Generating 100 Indian customers...")
        customers = generate_mock_customers(100)
        print(f"✅ Generated {len(customers)} customers")
        
        print("🏪 Generating 5 Starbucks stores in Indian cities...")
        stores = generate_mock_stores()
        print(f"✅ Generated {len(stores)} stores")
        
        # Display summary statistics
        loyalty_stats = {}
        for customer in customers:
            tier = customer["loyalty_tier"]
            loyalty_stats[tier] = loyalty_stats.get(tier, 0) + 1
        
        print(f"\n📊 Customer Loyalty Distribution:")
        for tier, count in loyalty_stats.items():
            print(f"   {tier.title()}: {count} customers")
        
        print(f"\n🌍 Store Locations:")
        for store in stores:
            city = store["name"].split()[1]
            print(f"   📍 {city}: {store['name']}")
        
        # Save to JSON files
        print(f"\n💾 Saving data to JSON files...")
        save_to_json(customers, stores, "mock_data")
        print("✅ Data saved to mock_data_users.json and mock_data_stores.json")
        
        # Seed database
        print(f"\n🗄️  Seeding SQLite database...")
        counts = await seed_database(customers, stores)
        print("✅ Database seeded successfully!")
        print(f"   📊 Inserted Records:")
        for key, value in counts.items():
            print(f"      {key.title()}: {value}")
        
        # Create sample data for quick testing
        print(f"\n🧪 Creating sample data for testing...")
        sample = create_sample_data()
        
        with open("sample_data.json", "w", encoding="utf-8") as f:
            import json
            from datetime import datetime
            
            def serialize_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            
            json.dump(sample, f, indent=2, ensure_ascii=False, default=serialize_datetime)
        
        print("✅ Sample data saved to sample_data.json")
        
        print(f"\n🎉 Mock Data Generation Complete!")
        print("=" * 60)
        print("📋 Summary:")
        print(f"   • {counts['customers']} customers added")
        print(f"   • {counts['stores']} stores added")
        print(f"   • {counts['documents']} documents added")
        print(f"   • {counts['interactions']} interactions added")
        print(f"\n🚀 You can now start the FastAPI server with: python run.py")
        
    except Exception as e:
        logger.error(f"Mock data generation failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())