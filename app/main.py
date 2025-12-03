"""
FastAPI application for hyper-personalized customer support chatbot.
"""
import time
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.endpoints import router
from app.core.cache import close_redis_connection
from app.core.config import get_settings
from app.core.database import create_tables, close_db_connection, get_db
from app.core.logging import configure_logging, get_logger, RequestLogger
from app.services.data_initialization import data_init_service
from app.services.rag_service import rag_service

# Configure logging first
configure_logging()
logger = get_logger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    
    # Startup
    logger.info("Starting hyper-personalized customer support chatbot")
    
    try:
        # Initialize database tables
        logger.info("Creating database tables...")
        await create_tables()
        
        # Initialize RAG service
        logger.info("Initializing RAG service...")
        await rag_service.initialize()
        
        # Load mock data
        logger.info("Loading mock data...")
        async for db_session in get_db():
            mock_data_ids = await data_init_service.initialize_all_mock_data(db_session)
            logger.info("Mock data loaded", extra=mock_data_ids)
            break
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    
    try:
        # Close database connection
        await close_db_connection()
        
        # Close Redis connection
        await close_redis_connection()
        
        logger.info("Application shutdown completed")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)


# Create FastAPI application
app = FastAPI(
    title="Hyper-Personalized Customer Support Chatbot",
    description="AI-powered customer support with personalization and RAG capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all HTTP requests and responses."""
    start_time = time.time()
    
    # Log request
    logger.info(
        "Incoming request",
        **RequestLogger.log_request(
            method=request.method,
            url=request.url,
            client_ip=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown")
        )
    )
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log response
        logger.info(
            "Request completed",
            **RequestLogger.log_response(
                status_code=response.status_code,
                processing_time=processing_time
            )
        )
        
        return response
        
    except Exception as e:
        # Log error
        processing_time = time.time() - start_time
        
        logger.error(
            "Request failed",
            **RequestLogger.log_error(
                error=e,
                processing_time=processing_time,
                method=request.method,
                url=str(request.url)
            )
        )
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": None  # Could implement request ID generation
            }
        )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors."""
    logger.warning(
        "Endpoint not found",
        method=request.method,
        url=str(request.url)
    )
    
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Endpoint not found",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    """Handle validation errors."""
    logger.warning(
        "Validation error",
        method=request.method,
        url=str(request.url),
        errors=str(exc)
    )
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors() if hasattr(exc, 'errors') else str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Include API routes
app.include_router(router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Hyper-Personalized Customer Support Chatbot API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs",
        "health": f"{settings.api_v1_prefix}/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )