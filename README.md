# H-002 Hyper-Personalized Customer Support Chatbot

A FastAPI-based customer support chatbot with hyper-personalization capabilities, RAG (Retrieval Augmented Generation), and SQLite local database.

## Features

- **FastAPI Framework**: High-performance async API with automatic OpenAPI documentation
- **SQLite Database**: Local database with SQLAlchemy ORM and async support
- **Hyper-Personalization**: Customer profiles with preferences, purchase history, and loyalty tiers
- **RAG Integration**: Document embedding and semantic search using sentence-transformers
- **Redis Caching**: Optional Redis integration for improved performance
- **Comprehensive Logging**: Structured logging with request/response tracking
- **Location-Based Services**: Find nearby stores using Haversine distance calculation

## Project Structure

```
GT_hack/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints.py          # API routes
│   ├── core/
│   │   ├── cache.py             # Redis cache utilities
│   │   ├── config.py            # Application configuration
│   │   ├── database.py          # SQLAlchemy database setup
│   │   └── logging.py           # Structured logging
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py            # SQLAlchemy models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py           # Pydantic schemas
│   ├── services/
│   │   ├── data_initialization.py  # Mock data creation
│   │   └── rag_service.py          # RAG implementation
│   ├── __init__.py
│   └── main.py                  # FastAPI application
├── .env                         # Environment variables
├── requirements.txt             # Python dependencies
└── run.py                      # Application runner
```

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

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