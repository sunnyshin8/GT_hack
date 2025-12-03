# H-002 Hyper-Personalized Customer Support Chatbot

A comprehensive customer support chatbot system with React TypeScript frontend and FastAPI backend, featuring enterprise-grade PII protection, Google Gemini AI integration, and hyper-personalized responses.

## 🌟 Key Features

### Frontend (Next.js TypeScript)
- **Modern Next.js Interface**: TypeScript-based chat interface with server-side rendering
- **Tailwind CSS Styling**: Responsive design with teal color scheme and smooth animations
- **Real-time Chat**: Live conversation with loading indicators and error handling
- **Nearby Stores Display**: Location-based store finder with distance and status
- **Mobile-Responsive**: Mobile-first design with optimized layouts

### Backend (FastAPI)
- **FastAPI Framework**: High-performance async API with automatic OpenAPI documentation
- **SQLite Database**: Local database with SQLAlchemy ORM and async support
- **Google Gemini AI**: Integration with Gemini 2.5-flash model for intelligent responses
- **RAG Pipeline**: LangChain-based Retrieval Augmented Generation with FAISS vector store
- **PII Protection**: Comprehensive PII masking with regex patterns and spaCy NER
- **Hyper-Personalization**: Customer context with loyalty tiers and location-based recommendations
- **Redis Caching**: Performance optimization with distributed caching
- **Weather Integration**: Temperature-based product recommendations
- **Location Services**: Haversine distance calculation for nearby store finder

## 🏗️ System Architecture

The system consists of two main components:

### Backend Architecture (FastAPI)
```
GT_hack/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints.py              # Enhanced API routes with PII protection
│   ├── core/
│   │   ├── cache.py                  # Redis cache utilities
│   │   ├── config.py                 # Application configuration
│   │   ├── database.py               # SQLAlchemy async database setup
│   │   └── logging.py                # Structured logging with PII audit
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py                 # SQLAlchemy models (Customer, Store, Document, Interaction)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py                # Pydantic schemas with location validation
│   ├── services/
│   │   ├── customer_context.py       # Customer profiling & location services
│   │   ├── data_initialization.py    # Database initialization
│   │   ├── knowledge_base_generator.py # Starbucks knowledge base (20 documents)
│   │   ├── langchain_rag_pipeline.py # Google Gemini RAG integration
│   │   ├── mock_data_generator.py    # Mock customer/store data
│   │   ├── pii_masking.py           # Comprehensive PII detection & masking
│   │   └── rag_service.py           # Legacy RAG implementation
│   ├── __init__.py
│   └── main.py                      # FastAPI application with CORS
├── .env                             # Environment variables (Gemini API key)
├── requirements.txt                 # Python dependencies with optional spaCy
└── run.py                          # Application runner
```

### Frontend Architecture (Next.js TypeScript)
```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── ChatInterface.tsx         # Main chat layout (70% chat + 30% stores)
│   │   ├── MessageList.tsx           # Scrollable message display
│   │   ├── MessageInput.tsx          # Input with Send button
│   │   └── StoreCard.tsx            # Nearby store display card
│   ├── types/
│   │   └── index.ts                 # TypeScript interfaces
│   ├── utils/
│   │   └── api.ts                   # API integration functions
│   ├── pages/
│   │   ├── _app.tsx                 # Next.js App component
│   │   ├── _document.tsx            # Custom Document
│   │   └── index.tsx                # Home page with chat interface
│   └── styles/
│       └── globals.css              # Tailwind CSS imports
├── next.config.js                   # Next.js configuration
├── package.json                     # Node.js dependencies
├── tailwind.config.js              # Tailwind CSS configuration
└── tsconfig.json                   # TypeScript configuration
```

## 🔧 Technology Stack

### Backend
- **FastAPI**: Modern Python web framework with async support
- **SQLAlchemy**: ORM with async SQLite database
- **Google Gemini AI**: Gemini 2.5-flash model for intelligent responses
- **LangChain**: RAG pipeline with FAISS vector store
- **spaCy**: Advanced NLP for PII detection (optional)
- **Redis**: Distributed caching for performance
- **Pydantic**: Data validation and settings management

### Frontend
- **Next.js 14**: Modern React framework with SSR and TypeScript
- **TypeScript**: Type-safe JavaScript development
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful SVG icons
- **Fetch API**: HTTP client for backend communication

## 🚀 Quick Start

### Backend Setup

1. **Clone Repository**:
   ```bash
   git clone https://github.com/sunnyshin8/GT_hack.git
   cd GT_hack
   ```

2. **Create Virtual Environment** (Python 3.10.11 recommended):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install Dependencies**:
   ```bash
   # Option 1: Full installation
   pip install -r requirements.txt
   
   # Option 2: Staged installation (if issues occur)
   .\install_dependencies.bat  # Windows
   # ./install_dependencies.sh  # Linux/Mac
   ```

4. **Configure Environment**:
   ```bash
   # Copy .env file and update with your Gemini API key
   GEMINI_API_KEY=AIzaSyBfyi7UZ_ETTGCHsZ5bCvgVk4LzxfXQzfY
   GEMINI_MODEL=gemini-2.5-flash
   ```

5. **Initialize Database**:
   ```bash
   python generate_mock_data.py      # Create mock customers/stores
   python generate_knowledge_base.py # Create Starbucks knowledge base
   ```

6. **Optional: Install spaCy for Enhanced PII Detection**:
   ```bash
   pip install spacy
   python -m spacy download en_core_web_sm
   ```

7. **Run Backend Server**:
   ```bash
   python run.py
   # Server runs at http://localhost:8000
   # API docs at http://localhost:8000/docs
   ```

### Frontend Setup

1. **Navigate to Frontend Directory**:
   ```bash
   cd frontend
   ```

2. **Install Node Dependencies**:
   ```bash
   npm install
   ```

3. **Run Development Server**:
   ```bash
   npm run dev
   # Frontend runs at http://localhost:3000
   ```

## 📚 API Documentation

### Enhanced Backend Endpoints

#### Chat Endpoint (Main Interface)
```
POST /api/v1/chat
Content-Type: application/json

{
  "customer_id": "demo-user-001",
  "message": "What's your best coffee for winter?",
  "location": {
    "latitude": 28.7041,
    "longitude": 77.1025
  }
}

Response:
{
  "response": "For winter, I recommend our Pike Place Roast...",
  "nearest_stores": [
    {
      "store_id": "store-001",
      "name": "Connaught Place",
      "distance_meters": 1200,
      "is_open": true,
      "current_promotions": ["10% OFF on hot beverages"]
    }
  ],
  "suggested_action": "visit_store",
  "timestamp": "2025-12-03T10:30:00Z"
}
```

#### Customer Profile
```
GET /api/v1/customers/{customer_id}

Response:
{
  "customer_id": "demo-user-001",
  "name": "John Doe",
  "preferences": ["espresso", "dark_roast"],
  "loyalty_tier": "Gold",
  "total_interactions": 45
}
```

#### Nearby Stores
```
GET /api/v1/stores/nearby?lat=28.7041&lon=77.1025&radius_km=5

Response:
[
  {
    "store_id": "store-001",
    "name": "Connaught Place",
    "distance_meters": 1200,
    "is_open": true,
    "current_promotions": ["10% OFF on hot beverages"]
  }
]
```

#### Document Search
```
GET /api/v1/documents/search?query=espresso

Response:
{
  "documents": [
    {
      "title": "Espresso Guide",
      "content": "Our signature espresso blend...",
      "relevance_score": 0.95
    }
  ]
}
```

#### Health Check
```
GET /api/v1/health

Response:
{
  "status": "healthy",
  "components": {
    "database": "connected",
    "redis": "connected",
    "gemini_api": "authenticated"
  },
  "timestamp": "2025-12-03T10:30:00Z"
}
```

## 🔒 Privacy & Security Features

### PII Protection Pipeline
1. **Multi-Method Detection**:
   - Regex patterns for Indian phone numbers, emails, Aadhar cards
   - spaCy NER for person and organization names
   - Indian name pattern matching (30+ common names)

2. **Secure Masking**:
   - Replace sensitive data with secure tokens
   - Store original-to-token mapping in Redis with TTL
   - Generate audit trails with hashed identifiers

3. **Session Management**:
   - 24-hour session expiry for PII tokens
   - Automatic cleanup of expired mappings
   - No PII stored in permanent logs

### Customer Context Services
1. **Loyalty Tier Calculation**:
   - Bronze: 0-10 interactions
   - Silver: 11-25 interactions
   - Gold: 26-50 interactions
   - Platinum: 51+ interactions

2. **Location Intelligence**:
   - Haversine distance calculation for nearby stores
   - Real-time store status (open/closed)
   - Distance-based recommendations

3. **Weather Integration**:
   - Temperature-based product suggestions
   - Seasonal menu recommendations
   - Climate-appropriate offers

## 🎯 AI & Personalization Pipeline

### Google Gemini Integration
1. **LangChain RAG Pipeline**:
   - GoogleGenerativeAIEmbeddings for document embedding
   - ChatGoogleGenerativeAI with Gemini 2.5-flash model
   - FAISS vector store for similarity search
   - 20 comprehensive Starbucks knowledge documents

2. **Context-Aware Responses**:
   - Customer profile integration (loyalty tier, preferences)
   - Location-based recommendations (nearby stores, weather)
   - Purchase history and interaction patterns
   - Real-time promotions and offers

3. **Response Enhancement**:
   - Masked PII for safe processing
   - Contextual product recommendations
   - Store-specific information
   - Personalized loyalty benefits

### Frontend User Experience

#### Chat Interface (Next.js TypeScript)
- **70% Chat Area**: 
  - User messages: Teal background, right-aligned
  - Bot messages: White background with border, left-aligned
  - Timestamps for all messages
  - Loading spinner during AI processing
  - Error handling with toast notifications

- **30% Stores Sidebar**:
  - Live nearby stores with distance
  - Open/closed status color coding (Green/Red)
  - Current promotions with badges
  - Click-to-navigate functionality

#### Component Architecture
```typescript
// Main App State
interface AppState {
  messages: Message[];
  isLoading: boolean;
  nearbyStores: Store[];
  customerId: string; // "demo-user-001"
  location: { lat: number; lon: number }; // Delhi coordinates
}

// Message Interface
interface Message {
  id: string;
  sender: 'user' | 'bot';
  content: string;
  timestamp: Date;
  stores?: Store[];
}

// Store Interface
interface Store {
  store_id: string;
  name: string;
  distance_meters: number;
  is_open: boolean;
  current_promotions: string[];
}
```

## 🧪 Testing & Validation

### Backend Tests
```bash
# Run comprehensive service tests
python test_services.py

# Test PII masking functionality
python -c "
from app.services.pii_masking import PIIMaskingEngine
engine = PIIMaskingEngine()
result = engine.process_user_input('Call me at 9876543210', 'session-123')
print(f'Masked: {result.masked_text}')
"

# Test customer context services
python -c "
import asyncio
from app.services.customer_context import CustomerContextService
async def test():
    service = CustomerContextService()
    context = await service.get_customer_context('demo-user-001')
    print(f'Loyalty Tier: {context.loyalty_tier}')
asyncio.run(test())
"

# Test RAG pipeline with Gemini
python test_gemini_rag.py
```

### Frontend Tests (After Setup)
```bash
cd frontend
npm test                    # Run Jest unit tests
npm run test:integration   # Run integration tests
npm run test:e2e          # Run end-to-end tests
```

## 🛠️ Development Workflow

### Backend Development
1. **Database Changes**: Update models in `app/models/models.py`
2. **API Routes**: Add endpoints in `app/api/endpoints.py`
3. **Business Logic**: Implement services in `app/services/`
4. **Validation**: Define schemas in `app/schemas/schemas.py`
5. **Configuration**: Update settings in `app/core/config.py`

### Frontend Development
1. **Components**: Create reusable components in `src/components/`
2. **API Integration**: Update API calls in `src/utils/api.ts`
3. **State Management**: Manage state in component level or context
4. **Styling**: Use Tailwind classes for consistent design
5. **Types**: Define TypeScript interfaces in `src/types/`

## 📊 Performance & Monitoring

### Backend Performance
- **Redis Caching**: 30-minute TTL for customer data
- **Async Operations**: All database operations are async
- **Connection Pooling**: SQLAlchemy connection pool management
- **Logging**: Structured logging with request tracking

### Frontend Performance
- **Code Splitting**: Lazy loading for components
- **Memoization**: React.memo for expensive components
- **Debounced Input**: Prevent excessive API calls
- **Error Boundaries**: Graceful error handling

## 🚀 Deployment

### Local Development
```bash
# Backend
python run.py              # http://localhost:8000

# Frontend
cd frontend && npm run dev # http://localhost:3000
```

### Production Deployment
1. **Backend**: Docker containerization with Gunicorn
2. **Frontend**: Build with `npm run build` and deploy to Vercel or serve with Nginx
3. **Database**: Migrate to PostgreSQL for production
4. **Caching**: Redis cluster for distributed caching
5. **Monitoring**: Add APM tools like New Relic or DataDog

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

For questions or issues:
- Create an issue on GitHub
- Check the API documentation at `http://localhost:8000/docs`
- Review the comprehensive logs in the console

---

**Built with ❤️ for the GT Hackathon 2025**

2. **Configure Environment** (optional):
   Edit `.env` file to customize settings like database URL, Redis connection, etc.

3. **Run the Application**:
   ```bash
   python run.py
   ```

4. **Access the API**:
   - Main API: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc

## API Endpoints

### Chat Endpoint
- **POST** `/api/v1/chat`
  - Main chatbot interaction endpoint
  - Supports customer personalization and store context
  - Returns AI-generated responses with sources

### Customer Management
- **GET** `/api/v1/customers/{customer_id}`
  - Retrieve customer profile with personalization data
  - Includes interaction history and loyalty information

### Store Locator
- **GET** `/api/v1/stores/nearby`
  - Find stores near a given location
  - Uses Haversine formula for distance calculation
  - Supports radius filtering and result limiting

### Health Check
- **GET** `/api/v1/health`
  - System health status
  - Database and Redis connectivity check

## Database Models

### Customer
- Personal information (masked for privacy)
- Preferences and communication settings
- Purchase history
- Loyalty tier (bronze, silver, gold, platinum)

### Store
- Location data (latitude, longitude)
- Operating hours
- Current promotions
- Inventory information

### Document
- Store-specific content for RAG
- Embedded vectors for semantic search
- Document types: FAQ, product info, policies

### Interaction
- Customer interaction tracking
- Conversation context and metadata
- Used for personalization improvements

## Configuration

Key configuration options in `.env`:

```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./chatbot.db

# Redis (optional)
REDIS_URL=redis://localhost:6379

# RAG Settings
EMBEDDING_MODEL=all-MiniLM-L6-v2
SIMILARITY_THRESHOLD=0.8

# Cache TTL
CUSTOMER_CACHE_TTL=600
STORE_CACHE_TTL=900
```

## Development

The application includes:
- Comprehensive error handling and logging
- Request/response middleware for monitoring
- CORS configuration for web frontends
- Async/await throughout for optimal performance
- Type hints and Pydantic validation

## Extending the System

- Add more sophisticated RAG models
- Integrate external APIs for real-time data
- Implement user authentication
- Add conversation memory and context tracking
- Enhance personalization algorithms

## Notes

- The application includes mock data for demonstration
- RAG service uses sentence-transformers for embeddings
- SQLite provides easy local development without external dependencies
- Redis is optional but recommended for production caching