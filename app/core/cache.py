"""
Redis cache connection and utilities.
"""
import json
import logging
from typing import Any, Optional

import redis.asyncio as redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# Global Redis connection pool
redis_pool: Optional[redis.ConnectionPool] = None
redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Get Redis client instance."""
    global redis_client, redis_pool
    
    if redis_client is None:
        redis_pool = redis.ConnectionPool.from_url(
            settings.redis_url,
            password=settings.redis_password,
            db=settings.redis_db,
            encoding="utf-8",
            decode_responses=True,
        )
        redis_client = redis.Redis(connection_pool=redis_pool)
        
    return redis_client


async def close_redis_connection():
    """Close Redis connection."""
    global redis_client, redis_pool
    
    if redis_client:
        await redis_client.close()
        redis_client = None
        
    if redis_pool:
        await redis_pool.disconnect()
        redis_pool = None
        
    logger.info("Redis connection closed")


async def cache_set(key: str, value: Any, ttl: int = None) -> bool:
    """Set a value in cache with optional TTL."""
    try:
        client = await get_redis_client()
        serialized_value = json.dumps(value, default=str)
        
        if ttl:
            await client.setex(key, ttl, serialized_value)
        else:
            await client.set(key, serialized_value)
            
        return True
    except Exception as e:
        logger.error(f"Cache set error: {e}")
        return False


async def cache_get(key: str) -> Optional[Any]:
    """Get a value from cache."""
    try:
        client = await get_redis_client()
        value = await client.get(key)
        
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.error(f"Cache get error: {e}")
        return None


async def cache_delete(key: str) -> bool:
    """Delete a value from cache."""
    try:
        client = await get_redis_client()
        result = await client.delete(key)
        return bool(result)
    except Exception as e:
        logger.error(f"Cache delete error: {e}")
        return False


async def cache_exists(key: str) -> bool:
    """Check if key exists in cache."""
    try:
        client = await get_redis_client()
        result = await client.exists(key)
        return bool(result)
    except Exception as e:
        logger.error(f"Cache exists error: {e}")
        return False