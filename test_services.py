"""
Comprehensive test script for PII masking and customer context services.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from app.services.pii_masking import pii_engine, mask_user_input
from app.services.customer_context import (
    build_prompt_context, 
    get_customer_context,
    get_nearest_stores,
    customer_context_service
)

async def test_pii_masking():
    """Test PII masking functionality."""
    print("🔐 Testing PII Masking Engine...")
    print("=" * 50)
    
    test_cases = [
        "Hi, I'm Rajesh and my phone number is +91-9876543210",
        "Please contact me at priya.sharma@gmail.com or call 9123456789",
        "My Aadhar number is 1234-5678-9012 and email is amit123@yahoo.com",
        "Call Suresh at +91-8765432109, his credit card is 4111-1111-1111-1111",
        "I'm Kavya from Mumbai, phone: 9876543210, PAN: ABCDE1234F"
    ]
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{test_text}'")
        
        try:
            # Test PII detection
            detected_pii = pii_engine.detect_pii(test_text)
            print(f"   📊 Detected {len(detected_pii)} PII entities:")
            
            for pii in detected_pii:
                print(f"      - {pii.pii_type} ({pii.detection_method}): {pii.masked_value}")
            
            # Test full processing
            result = await mask_user_input(test_text)
            
            print(f"   ✅ Original: {result['original_text']}")
            print(f"   🎭 Masked:   {result['masked_text']}")
            print(f"   🆔 Session:  {result['session_id']}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n🎉 PII Masking tests completed!")

async def test_customer_context():
    """Test customer context retrieval."""
    print("\n👤 Testing Customer Context Service...")
    print("=" * 50)
    
    try:
        # Test with a mock customer ID (this would need actual data)
        test_customer_id = "test-customer-123"
        
        context = await get_customer_context(test_customer_id)
        
        if context:
            print(f"✅ Customer context retrieved:")
            print(f"   Name: {context.basic_info['name']}")
            print(f"   Loyalty Tier: {context.preferences['loyalty_tier']}")
            print(f"   Favorite Categories: {context.preferences['favorite_categories']}")
            print(f"   Purchase History: {len(context.purchase_history)} items")
            print(f"   Total Interactions: {context.interaction_count}")
        else:
            print("⚠️  No customer context found (expected for test)")
            
    except Exception as e:
        print(f"❌ Customer context error: {e}")

async def test_location_services():
    """Test location and store services."""
    print("\n📍 Testing Location Services...")
    print("=" * 50)
    
    # Test coordinates for Delhi
    test_latitude = 28.6139
    test_longitude = 77.2090
    
    try:
        # Test nearest stores
        stores = await get_nearest_stores(test_latitude, test_longitude, radius_km=10.0)
        
        print(f"✅ Found {len(stores)} nearby stores:")
        for store in stores[:3]:  # Show first 3
            print(f"   📍 {store.name}")
            print(f"      Distance: {store.distance_km} km")
            print(f"      Open: {'Yes' if store.is_open else 'No'}")
            print(f"      Promotions: {len(store.current_promotions)}")
        
    except Exception as e:
        print(f"❌ Location services error: {e}")

async def test_prompt_context_builder():
    """Test comprehensive prompt context building."""
    print("\n🎯 Testing Prompt Context Builder...")
    print("=" * 50)
    
    try:
        # Test with location only
        context = await build_prompt_context(
            latitude=28.6139,  # Delhi
            longitude=77.2090
        )
        
        print("✅ Generated context:")
        print(f"   Customer Name: {context['customer_name']}")
        print(f"   Loyalty Tier: {context['loyalty_tier']}")
        print(f"   Weather: {context['weather']}")
        print(f"   Store: {context['store_name']}")
        print(f"   Distance: {context['distance_to_store']}")
        print(f"   Current Time: {context['current_time']}")
        
        if 'weather_recommendations' in context:
            print(f"   Weather Recommendations: {context['weather_recommendations']}")
        
        if 'store_promotions' in context:
            print(f"   Store Promotions: {context['store_promotions']}")
            
    except Exception as e:
        print(f"❌ Prompt context error: {e}")

async def test_integrated_workflow():
    """Test complete integrated workflow."""
    print("\n🔄 Testing Integrated Workflow...")
    print("=" * 50)
    
    # Simulate user input with PII
    user_message = "Hi, I'm Priya from Delhi at +91-9876543210. What coffee do you recommend?"
    
    try:
        print(f"📝 User Input: '{user_message}'")
        
        # Step 1: Mask PII
        pii_result = await mask_user_input(user_message)
        print(f"🎭 Masked Input: '{pii_result['masked_text']}'")
        print(f"🆔 Session ID: {pii_result['session_id']}")
        print(f"🔍 PII Detected: {pii_result['pii_count']} items")
        
        # Step 2: Build context
        context = await build_prompt_context(
            latitude=28.6139,  # Delhi coordinates
            longitude=77.2090
        )
        
        print(f"🌍 Context Built:")
        print(f"   Location: {context['weather']}")
        print(f"   Nearest Store: {context['store_name']} ({context['distance_to_store']})")
        
        # Step 3: Simulate RAG processing (would normally use masked input)
        print(f"🤖 Ready for RAG processing with:")
        print(f"   - Masked input: {pii_result['masked_text']}")
        print(f"   - Rich context: {len(context)} context fields")
        print(f"   - Session tracking: {pii_result['session_id']}")
        
        print("✅ Integrated workflow test completed!")
        
    except Exception as e:
        print(f"❌ Integrated workflow error: {e}")

async def main():
    """Run all tests."""
    print("🚀 Starting Comprehensive Service Tests")
    print("=" * 60)
    
    # Initialize any required services
    try:
        # Test PII masking
        await test_pii_masking()
        
        # Test customer context
        await test_customer_context()
        
        # Test location services
        await test_location_services()
        
        # Test prompt context builder
        await test_prompt_context_builder()
        
        # Test integrated workflow
        await test_integrated_workflow()
        
        print("\n" + "=" * 60)
        print("🎉 All service tests completed!")
        print("\n💡 Next Steps:")
        print("   1. Install packages: pip install -r requirements.txt")
        print("   2. Run the application: python run.py")
        print("   3. Test the enhanced /chat endpoint with PII protection")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())