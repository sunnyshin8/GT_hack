# PII Masking and Customer Context Services

This document describes the comprehensive PII (Personally Identifiable Information) masking engine and customer context retrieval services added to the FastAPI chatbot.

## 🔐 PII Masking Engine

### Overview
The PII masking engine provides multi-layered detection and masking of sensitive personal information to ensure privacy compliance and data protection.

### Detection Methods

1. **Regex Patterns** - High precision detection for:
   - Indian phone numbers: `+91-****-****-5678`
   - Email addresses: `r****@gmail.com`
   - Aadhar numbers: `[REDACTED]`
   - Credit cards: `[REDACTED]`
   - PAN cards: `[REDACTED]`

2. **spaCy NER** (Optional) - Natural Language processing for:
   - PERSON names: `[PERSON_MASKED_0]`
   - ORGANIZATION names: `[ORG_MASKED_0]`

3. **Indian Name Detection** - Pattern matching for common Indian names:
   - Male names: Rajesh, Amit, Rohit, Vikram, etc.
   - Female names: Priya, Sneha, Pooja, Kavya, etc.

### Core Functions

```python
from app.services.pii_masking import mask_user_input, pii_engine

# Process user input with PII detection and masking
result = await mask_user_input("Call me Rajesh at +91-9876543210")

# Returns:
{
    "original_text": "Call me Rajesh at +91-9876543210",
    "masked_text": "Call me [NAME_MASKED_0] at +91-****-****-3210", 
    "session_id": "uuid-string",
    "pii_detected": [
        {"type": "indian_name", "method": "name_pattern"},
        {"type": "phone", "method": "regex"}
    ],
    "pii_count": 2
}
```

### Security Features

- **No PII Storage**: Only hashed values stored for audit
- **Session Tracking**: Temporary PII mappings with 1-hour TTL
- **Audit Logging**: Anonymized audit trail for compliance
- **Redis Integration**: Secure temporary storage with automatic expiration

### Usage in Chat Endpoint

```python
# Step 1: Mask PII in user input
pii_result = await mask_user_input(request.message)
masked_message = pii_result['masked_text']
session_id = pii_result['session_id']

# Step 2: Process with AI using masked input
rag_response = await get_rag_response(masked_message, ...)

# Step 3: Return response with session tracking
return ChatResponse(..., session_id=session_id)
```

## 👤 Customer Context Service

### Overview
Provides comprehensive customer profiling and context for hyper-personalized responses.

### CustomerContext Structure

```python
@dataclass
class CustomerContext:
    customer_id: str
    basic_info: Dict[str, Any]          # Masked contact info
    preferences: Dict[str, Any]         # Loyalty tier, favorites
    purchase_history: List[Dict[str, Any]]  # Last 10 purchases
    loyalty_status: Dict[str, Any]      # Points, tier progress
    interaction_count: int              # Total interactions
    last_interaction: Optional[datetime]
```

### Core Functions

```python
from app.services.customer_context import get_customer_context

# Get comprehensive customer context
context = await get_customer_context("customer-id-123")

print(context.basic_info['name'])           # "Priya Sharma"
print(context.preferences['loyalty_tier'])  # "gold"
print(context.loyalty_status['total_points'])  # 15000
```

### Loyalty Tier Calculation

- **Bronze**: ₹0-₹2,499 spent
- **Silver**: ₹2,500-₹7,499 spent  
- **Gold**: ₹7,500-₹14,999 spent
- **Platinum**: ₹15,000+ spent

Points system: ₹1 = 1 point, with tier-based reward thresholds.

## 📍 Location Service

### Overview
Provides location-based store recommendations, distance calculations, and operational status.

### Core Functions

```python
from app.services.customer_context import get_nearest_stores

# Get nearby stores
stores = await get_nearest_stores(28.6139, 77.2090, radius_km=5.0)

for store in stores:
    print(f"{store.name} - {store.distance_km}km - {'Open' if store.is_open else 'Closed'}")
```

### Features

- **Haversine Distance**: Accurate geographical distance calculation
- **Operating Hours**: Real-time store status based on current time
- **Inventory Context**: Key item availability for recommendations
- **Promotion Awareness**: Current store-specific offers

## 🌤️ Weather Service (Mock)

### Overview
Provides weather-based recommendations for enhanced personalization.

### Features

```python
weather_context = weather_service.get_weather_context(28.6139, 77.2090)

# Returns:
{
    'temperature': 18,
    'condition': 'clear', 
    'city': 'Delhi',
    'category': 'cold',
    'recommendations': ['Hot beverages', 'Hot chocolate', 'Warm pastries'],
    'description': '18°C, clear weather in Delhi'
}
```

Temperature-based recommendations:
- **Cold (< 15°C)**: Hot beverages, warm pastries
- **Hot (> 28°C)**: Cold drinks, iced beverages
- **Pleasant**: Any beverage, seasonal specials

## 🎯 Prompt Context Builder

### Overview
Combines all context sources into a unified format for AI prompt injection.

### Usage

```python
from app.services.customer_context import build_prompt_context

# Build comprehensive context
context = await build_prompt_context(
    customer_id="customer-123",
    latitude=28.6139,
    longitude=77.2090,
    store_id="store-456"
)

# Returns formatted context ready for RAG prompts:
{
    'customer_name': 'Priya Sharma',
    'loyalty_tier': 'gold',
    'favorite_categories': ['coffee', 'pastries'],
    'distance_to_store': '1.2 km',
    'store_name': 'Starbucks Phoenix MarketCity',
    'weather': '18°C, clear weather in Delhi',
    'weather_recommendations': ['Hot beverages', 'Hot chocolate'],
    'current_time': '2025-12-03 14:30:00',
    'store_is_open': True,
    'store_promotions': ['Winter Special', 'Gold Member Discount']
}
```

## 🚀 Integration with Chat Endpoint

### Enhanced Chat Flow

1. **PII Detection & Masking**
   ```python
   pii_result = await mask_user_input(request.message)
   ```

2. **Context Building**
   ```python
   context = await build_prompt_context(
       customer_id=request.customer_id,
       latitude=request.metadata.get('latitude'),
       longitude=request.metadata.get('longitude'),
       store_id=request.store_id
   )
   ```

3. **RAG Processing with Context**
   ```python
   rag_response = await get_rag_response(
       pii_result['masked_text'],  # Masked input
       customer_context,
       location_context
   )
   ```

4. **Privacy-Safe Response**
   ```python
   return ChatResponse(
       response=response_text,
       session_id=pii_result['session_id'],  # For PII tracking
       sources=sources,
       confidence_score=confidence
   )
   ```

## 🔒 Privacy & Security

### PII Protection Measures

1. **Input Masking**: All PII detected and masked before AI processing
2. **No Storage**: Original PII never stored in database
3. **Hash-Only Audit**: Security audit uses hashes, not actual values
4. **Session Expiry**: Temporary mappings expire after 1 hour
5. **Masked Interactions**: Database stores session IDs instead of messages

### Compliance Features

- **GDPR Ready**: Right to erasure through cache expiry
- **Data Minimization**: Only necessary data processed
- **Audit Trail**: Complete anonymized logging
- **Access Control**: Session-based temporary access only

## 📊 Performance Features

### Caching Strategy

- **Customer Context**: 30-minute TTL
- **Location Data**: 15-minute TTL  
- **PII Mappings**: 1-hour TTL with auto-expiry
- **Store Inventory**: 10-minute TTL

### Database Optimization

- **Connection Pooling**: Efficient database access
- **Selective Queries**: Only required fields fetched
- **Index Usage**: Optimized for customer/store lookups
- **Batch Processing**: Multiple context sources in parallel

## 🧪 Testing

Run comprehensive tests:

```bash
python test_services.py
```

Test coverage includes:
- PII detection across multiple methods
- Customer context retrieval and caching
- Location services and distance calculation
- Weather context and recommendations
- Integrated workflow with complete chat pipeline

## 📝 API Updates

### Enhanced Chat Request

```python
{
    "message": "Hi, I'm Rajesh. What coffee do you recommend?",
    "customer_id": "customer-123",
    "store_id": "store-456", 
    "metadata": {
        "latitude": 28.6139,
        "longitude": 77.2090,
        "user_agent": "mobile-app"
    }
}
```

### Enhanced Chat Response

```python
{
    "response": "Hi [NAME_MASKED_0]! As a Gold member, I'd recommend our signature Pike Place Roast...",
    "session_id": "uuid-for-pii-tracking",
    "sources": [...],
    "confidence_score": 0.95,
    "processing_time_ms": 234
}
```

This comprehensive system ensures both privacy protection and hyper-personalization, providing the best of both worlds for customer support chatbot interactions.