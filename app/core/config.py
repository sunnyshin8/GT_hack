"""
Core configuration and settings for the application.
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database Configuration
    database_url: str = "sqlite+aiosqlite:///./chatbot.db"
    database_pool_size: int = 20
    database_max_overflow: int = 0
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    redis_password: Optional[str] = None
    redis_db: int = 0
    
    # Application Configuration
    api_v1_prefix: str = "/api/v1"
    debug: bool = True
    log_level: str = "INFO"
    
    # RAG Configuration
    embedding_model: str = "all-MiniLM-L6-v2"
    vector_dimension: int = 384
    similarity_threshold: float = 0.8
    
    # Cache Configuration
    cache_ttl: int = 300
    customer_cache_ttl: int = 600
    store_cache_ttl: int = 900
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()