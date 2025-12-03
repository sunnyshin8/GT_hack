"""
Test script for Gemini RAG pipeline integration.
"""
import asyncio
import os
from app.services.langchain_rag_pipeline import get_rag_response
from app.services.knowledge_base_generator import generate_starbucks_knowledge_base

async def test_rag_pipeline():
    """Test the RAG pipeline with sample queries."""
    print("🚀 Testing Gemini RAG Pipeline...")
    
    # First generate knowledge base
    print("\n📚 Generating knowledge base...")
    try:
        knowledge_base = generate_starbucks_knowledge_base()
        print(f"✅ Generated {len(knowledge_base)} knowledge documents")
    except Exception as e:
        print(f"❌ Failed to generate knowledge base: {e}")
        return
    
    # Test customer context
    customer_context = {
        "customer_name": "Priya Sharma",
        "loyalty_tier": "gold",
        "favorite_categories": ["coffee", "pastries"]
    }
    
    # Test location context  
    location_context = {
        "distance_to_store": "1.5 km",
        "store_name": "Starbucks Phoenix MarketCity",
        "weather": "pleasant"
    }
    
    # Test queries
    test_queries = [
        "What are your store hours?",
        "Do you have any coffee recommendations for me?",
        "What promotions are available today?",
        "I want to know about your loyalty program",
        "Can I get my drink customized?"
    ]
    
    print("\n🧪 Testing queries...")
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: '{query}'")
        try:
            response = await get_rag_response(
                query, 
                customer_context, 
                location_context
            )
            
            print(f"   ✅ Response: {response.get('response', 'No response')[:150]}...")
            print(f"   📊 Confidence: {response.get('confidence', 'N/A')}")
            print(f"   📚 Sources: {len(response.get('sources', []))}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n🎉 RAG Pipeline testing completed!")

if __name__ == "__main__":
    # Check if API key is available
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("Please make sure the .env file is properly configured")
    else:
        print(f"✅ Found Google API key: {api_key[:10]}...")
        asyncio.run(test_rag_pipeline())