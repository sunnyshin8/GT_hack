"""
Comprehensive JSON knowledge base for Starbucks customer support.
Contains 20 documents covering all aspects of customer service.
"""
import json
from datetime import datetime, timedelta
from uuid import uuid4

def generate_starbucks_knowledge_base():
    """Generate comprehensive knowledge base for Starbucks customer support."""
    
    # Helper function to create valid_until date
    def get_valid_until(months_from_now=12):
        return (datetime.now() + timedelta(days=30*months_from_now)).strftime("%Y-%m-%dT23:59:59Z")
    
    knowledge_base = []
    
    # 1. Store Information (3 docs)
    knowledge_base.extend([
        {
            "doc_id": str(uuid4()),
            "doc_type": "store_info",
            "content": "All Starbucks stores in India are open from 7:00 AM to 10:00 PM Monday through Thursday, extended hours 7:00 AM to 11:00 PM on Friday and Saturday, and 8:00 AM to 10:00 PM on Sunday. All locations offer complimentary Wi-Fi with password 'StarbucksIndia2024', power outlets for laptops, air conditioning, and comfortable seating arrangements. Most stores have parking facilities available. We provide wheelchair accessibility and baby-friendly facilities including high chairs.",
            "store_id": None,
            "metadata": {
                "category": "general_info",
                "valid_until": get_valid_until(12),
                "applicable_tier": "all",
                "weather_condition": "all"
            }
        },
        {
            "doc_id": str(uuid4()),
            "doc_type": "store_info", 
            "content": "Our Delhi Central store at Connaught Place features outdoor seating perfect for Delhi weather, with heating during winter months. Mumbai Bandra store offers sea-view seating and 24/7 operation on weekends. Bangalore Koramangala store has a dedicated co-working space with private meeting rooms available for booking. All metro stores have drive-through facilities available from 7 AM to 9 PM daily.",
            "store_id": None,
            "metadata": {
                "category": "location_specific",
                "valid_until": get_valid_until(12),
                "applicable_tier": "all", 
                "weather_condition": "all"
            }
        },
        {
            "doc_id": str(uuid4()),
            "doc_type": "store_info",
            "content": "Special amenities include outdoor terraces at select locations, pet-friendly seating areas, charging stations for electric vehicles at Mumbai and Delhi stores, and live music events on Friday evenings. Our Bangalore and Hyderabad stores feature rooftop seating with city views. All stores have Instagram-worthy photo spots and provide free birthday treats for loyalty members.",
            "store_id": None,
            "metadata": {
                "category": "special_features",
                "valid_until": get_valid_until(12),
                "applicable_tier": "all",
                "weather_condition": "all"
            }
        }
    ])
    
    # 2. Products & Pricing (4 docs)
    knowledge_base.extend([
        {
            "doc_id": str(uuid4()),
            "doc_type": "product",
            "content": "Hot Beverages Menu: Americano ₹240 (Tall), ₹280 (Grande), ₹320 (Venti). Cappuccino ₹280/₹320/₹360. Latte ₹320/₹360/₹400. Caramel Macchiato ₹380/₹420/₹460. Hot Chocolate ₹290/₹330/₹370. Masala Chai Latte ₹270/₹310/₹350. Filter Coffee ₹220/₹260/₹300. Flat White ₹320/₹360. All beverages can be made with oat milk, almond milk, or soy milk for an additional ₹30.",
            "store_id": None,
            "metadata": {
                "category": "hot_beverages",
                "valid_until": get_valid_until(6),
                "applicable_tier": "all",
                "weather_condition": "cold"
            }
        },
        {
            "doc_id": str(uuid4()),
            "doc_type": "product",
            "content": "Cold Beverages Menu: Iced Americano ₹260/₹300/₹340. Cold Brew ₹300/₹340/₹380. Iced Latte ₹340/₹380/₹420. Frappuccino varieties: Caramel ₹420/₹460/₹500, Chocolate ₹400/₹440/₹480, Vanilla ₹380/₹420/₹460. Iced Tea ₹200/₹240/₹280. Fresh Lime Soda ₹180/₹220/₹260. Mango Lassi Frappuccino ₹450/₹490/₹530 (seasonal). All cold beverages available with extra shot ₹60, extra ice, or light ice upon request.",
            "store_id": None,
            "metadata": {
                "category": "cold_beverages", 
                "valid_until": get_valid_until(6),
                "applicable_tier": "all",
                "weather_condition": "hot"
            }
        },
        {
            "doc_id": str(uuid4()),
            "doc_type": "product",
            "content": "Food Menu: Sandwiches - Chicken Club ₹450, Paneer Tikka ₹380, Egg & Cheese ₹320. Wraps - Chicken Keema ₹420, Aloo Masala ₹350. Pastries - Croissant ₹220, Chocolate Danish ₹180, Blueberry Muffin ₹160. Cookies ₹120 each. Cakes - Chocolate Truffle Slice ₹280, Red Velvet ₹320. Indian snacks - Samosa ₹80, Dhokla ₹100, Masala Nuts ₹150. Fresh salads available - Caesar ₹380, Mediterranean ₹420.",
            "store_id": None,
            "metadata": {
                "category": "food_items",
                "valid_until": get_valid_until(3),
                "applicable_tier": "all",
                "weather_condition": "all"
            }
        },
        {
            "doc_id": str(uuid4()),
            "doc_type": "product",
            "content": "Merchandise & Gift Cards: Starbucks Tumbler ₹1200-₹2500 (various designs), Coffee Mugs ₹800-₹1500, Travel Mugs ₹1800-₹3200. Premium Coffee Beans: Pike Place Roast ₹950/250g, Indian Espresso Roast ₹1100/250g, Decaf House Blend ₹850/250g. Gift Cards available from ₹500 to ₹10,000. Branded merchandise: T-shirts ₹1200, Tote Bags ₹900, Keychains ₹350. Seasonal items updated monthly.",
            "store_id": None,
            "metadata": {
                "category": "merchandise",
                "valid_until": get_valid_until(12),
                "applicable_tier": "all",
                "weather_condition": "all"
            }
        }
    ])
    
    # 3. Promotions & Offers (4 docs)
    knowledge_base.extend([
        {
            "doc_id": str(uuid4()),
            "doc_type": "promotion",
            "content": "Current Active Promotions: WELCOME10 - 10% off on first order for new customers (minimum ₹200). STUDENT15 - 15% off for students with valid college ID (Monday-Friday, 2-6 PM). COMBO20 - 20% off when you buy any beverage + food item together. FRIYAY25 - 25% off on all Frappuccinos every Friday. EARLYBIRD - Buy any hot beverage before 9 AM and get a free cookie. All promotions valid until December 31, 2025.",
            "store_id": None,
            "metadata": {
                "category": "active_promotions",
                "valid_until": "2025-12-31T23:59:59Z",
                "applicable_tier": "all",
                "weather_condition": "all"
            }
        },
        {
            "doc_id": str(uuid4()),
            "doc_type": "promotion",
            "content": "Loyalty Program Benefits: Bronze Members (0-499 stars) - Free birthday drink, 10% off merchandise. Silver Members (500-1499 stars) - Free drink every 125 points, 15% off food items, early access to new products. Gold Members (1500+ stars) - Free drink every 100 points, 20% off everything, complimentary size upgrades, exclusive member events. Platinum Members (2500+ stars) - Free drink every 75 points, 25% off, priority ordering, personal barista consultations.",
            "store_id": None,
            "metadata": {
                "category": "loyalty_program",
                "valid_until": get_valid_until(12),
                "applicable_tier": "all",
                "weather_condition": "all"
            }
        },
        {
            "doc_id": str(uuid4()),
            "doc_type": "promotion",
            "content": "Seasonal Offers: Winter Warmth Special (Nov-Feb) - 15% off all hot beverages and hot chocolate. Summer Cool Down (Mar-Jun) - 20% off cold beverages and Frappuccinos, free ice cream with any Frappuccino. Monsoon Comfort (Jul-Sep) - Hot chai and coffee combos at ₹399. Festival Specials during Diwali, Holi, and Christmas with themed drinks and 30% off gift cards. Weekend Warriors - Double loyalty points on Saturday and Sunday purchases.",
            "store_id": None,
            "metadata": {
                "category": "seasonal_offers",
                "valid_until": get_valid_until(12),
                "applicable_tier": "all",
                "weather_condition": "all"
            }
        },
        {
            "doc_id": str(uuid4()),
            "doc_type": "promotion",
            "content": "Exclusive Member Deals: Gold & Platinum exclusive: Free extra shot in any espresso drink, complimentary oat milk substitute, access to limited edition seasonal flavors. Member Monday - 30% off your entire order. Refer-a-Friend program - Both you and your friend get ₹200 off next purchase when they join loyalty program. Corporate partnerships with major Indian companies provide employee discounts. Group orders of 5+ beverages get 15% automatic discount.",
            "store_id": None,
            "metadata": {
                "category": "exclusive_deals",
                "valid_until": get_valid_until(12),
                "applicable_tier": "silver",
                "weather_condition": "all"
            }
        }
    ])
    
    # 4. Policies (3 docs)
    knowledge_base.extend([
        {
            "doc_id": str(uuid4()),
            "doc_type": "policy",
            "content": "Return and Refund Policy: Unsatisfied with your drink? We'll remake it for free or provide full refund within 30 minutes of purchase. Merchandise returns accepted within 30 days with receipt in original condition. Gift cards are non-refundable but can be transferred to another person. If you're not happy with your experience, please speak to our store manager who is authorized to provide immediate resolution including complimentary drinks or full refunds.",
            "store_id": None,
            "metadata": {
                "category": "returns_refunds",
                "valid_until": get_valid_until(12),
                "applicable_tier": "all",
                "weather_condition": "all"
            }
        },
        {
            "doc_id": str(uuid4()),
            "doc_type": "policy",
            "content": "Loyalty Tier Benefits Detailed: Bronze (₹0-₹2499 spent) - Birthday reward, 10% off packaged coffee. Silver (₹2500-₹7499) - Free drink every 125 stars, 15% off food, exclusive promotions access. Gold (₹7500-₹14999) - Free drink every 100 stars, 20% off everything, size upgrades, monthly bonus stars. Platinum (₹15000+) - Free drink every 75 stars, 25% off, personal barista, VIP customer service line, early product access. Stars earned: ₹1 = 1 star. Stars expire after 12 months of inactivity.",
            "store_id": None,
            "metadata": {
                "category": "loyalty_tiers",
                "valid_until": get_valid_until(12),
                "applicable_tier": "all",
                "weather_condition": "all"
            }
        },
        {
            "doc_id": str(uuid4()),
            "doc_type": "policy",
            "content": "Payment Methods: We accept cash, all major credit/debit cards (Visa, Mastercard, RuPay, Amex), UPI payments (PayTm, PhonePe, Google Pay, BHIM), digital wallets (PayTm Wallet, Mobikwik, Freecharge), Starbucks Gift Cards, and contactless payments. Minimum UPI transaction ₹50. Card transactions above ₹2000 require PIN. Corporate cards accepted for business customers. Split payments allowed up to 2 different methods per transaction.",
            "store_id": None,
            "metadata": {
                "category": "payment_methods",
                "valid_until": get_valid_until(12),
                "applicable_tier": "all",
                "weather_condition": "all"
            }
        }
    ])
    
    # 5. FAQs (3 docs)
    knowledge_base.extend([
        {
            "doc_id": str(uuid4()),
            "doc_type": "faq",
            "content": "Finding Your Nearest Store: Use our store locator on the Starbucks India app or website by entering your pincode or current location. All stores display real-time availability, current wait times, and special amenities. You can also call our customer service at 1800-266-0010 for store information. Major locations: Delhi - Connaught Place, Khan Market, Select City Walk. Mumbai - Bandra West, Phoenix Mall, Marine Drive. Bangalore - UB City, Brigade Road, Koramangala. Store hours and contact details available on Google Maps.",
            "store_id": None,
            "metadata": {
                "category": "store_locator",
                "valid_until": get_valid_until(12),
                "applicable_tier": "all",
                "weather_condition": "all"
            }
        },
        {
            "doc_id": str(uuid4()),
            "doc_type": "faq",
            "content": "Joining Loyalty Program: Download the Starbucks India app from Play Store or App Store, create account with mobile number and email, verify OTP, and start earning stars immediately. No membership fee required. You can also sign up in-store with our baristas. Link your payment method for faster checkout. Earn 1 star per ₹1 spent. Bronze status starts immediately, Silver at 500 stars, Gold at 1500 stars, Platinum at 2500 stars. Track your progress in the app and receive personalized offers.",
            "store_id": None,
            "metadata": {
                "category": "loyalty_signup",
                "valid_until": get_valid_until(12),
                "applicable_tier": "all",
                "weather_condition": "all"
            }
        },
        {
            "doc_id": str(uuid4()),
            "doc_type": "faq",
            "content": "Drink Customization Options: Milk alternatives - oat milk, almond milk, soy milk, coconut milk (+₹30). Sweetness levels - regular, half sweet, extra sweet, sugar-free syrups available. Temperature - extra hot, kids temp, iced versions of most drinks. Caffeine - decaf options, extra shots (+₹60), half-caff. Size modifications - short (not on menu but available), tall, grande, venti. Foam preferences - no foam, extra foam, dry cappuccino. Special dietary needs accommodated - vegan, lactose-free, keto-friendly options available.",
            "store_id": None,
            "metadata": {
                "category": "customization",
                "valid_until": get_valid_until(12),
                "applicable_tier": "all",
                "weather_condition": "all"
            }
        }
    ])
    
    # 6. Weather-Based Tips (2 docs)
    knowledge_base.extend([
        {
            "doc_id": str(uuid4()),
            "doc_type": "weather",
            "content": "Cold Weather Recommendations: Perfect drinks for chilly Delhi winters and monsoon season - Hot Chocolate with whipped cream ₹330, Masala Chai Latte ₹310, Caramel Macchiato ₹420, or our signature Pike Place Roast ₹280. Try adding an extra shot for more warmth. Pair with warm pastries like chocolate croissant ₹220 or blueberry muffin ₹160. Our heated indoor seating provides comfort during cold weather. Free blankets available at select outdoor seating areas during winter months.",
            "store_id": None,
            "metadata": {
                "category": "cold_weather",
                "valid_until": get_valid_until(12),
                "applicable_tier": "all",
                "weather_condition": "cold"
            }
        },
        {
            "doc_id": str(uuid4()),
            "doc_type": "weather",
            "content": "Hot Weather Recommendations: Beat the Indian summer heat with refreshing Cold Brew ₹340, Iced Caramel Macchiato ₹440, or tropical Mango Lassi Frappuccino ₹490. Our Iced Teas ₹240 and Fresh Lime Soda ₹220 are perfect thirst quenchers. Try blended beverages with extra ice for maximum cooling effect. Light food options like Mediterranean Salad ₹420 complement hot weather. All stores have powerful AC and chilled water stations. Outdoor misters available at terrace seating during peak summer.",
            "store_id": None,
            "metadata": {
                "category": "hot_weather",
                "valid_until": get_valid_until(12),
                "applicable_tier": "all",
                "weather_condition": "hot"
            }
        }
    ])
    
    # 7. Delivery & Services (1 doc)
    knowledge_base.extend([
        {
            "doc_id": str(uuid4()),
            "doc_type": "service",
            "content": "Delivery & Mobile Ordering: Available through Zomato, Swiggy, and Dunzo in all major cities with ₹50 delivery charges. Free delivery on orders above ₹400. Delivery time 25-45 minutes depending on location and weather. Mobile ordering through Starbucks app allows skip-the-line pickup - order ahead and collect from dedicated pickup counter. Bulk orders for offices and events available with 24-hour advance notice (minimum ₹2000). Catering services for corporate meetings and parties. Same-day delivery available in Mumbai and Delhi CBD areas.",
            "store_id": None,
            "metadata": {
                "category": "delivery_services",
                "valid_until": get_valid_until(12),
                "applicable_tier": "all",
                "weather_condition": "all"
            }
        }
    ])
    
    return knowledge_base

def save_knowledge_base_to_file():
    """Save the knowledge base to JSON file."""
    kb = generate_starbucks_knowledge_base()
    
    with open("starbucks_knowledge_base.json", "w", encoding="utf-8") as f:
        json.dump(kb, f, indent=2, ensure_ascii=False)
    
    print(f"Knowledge base generated with {len(kb)} documents")
    print("Categories included:")
    categories = {}
    for doc in kb:
        category = doc["metadata"]["category"]
        categories[category] = categories.get(category, 0) + 1
    
    for category, count in categories.items():
        print(f"  {category}: {count} documents")
    
    return kb

if __name__ == "__main__":
    save_knowledge_base_to_file()