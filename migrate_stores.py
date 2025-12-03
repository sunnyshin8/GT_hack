"""
Migration script to add store_type and cuisine_type columns to stores table.
Run this script to update existing database schema.
"""
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import text
from app.core.database import engine
from app.core.logging import get_logger

# Load environment variables
load_dotenv()

# Load environment variables
load_dotenv()

logger = get_logger(__name__)

async def migrate_stores_table():
    """Add new columns to stores table."""
    migration_queries = [
        """
        ALTER TABLE stores 
        ADD COLUMN store_type VARCHAR(50) NOT NULL DEFAULT 'cafe'
        """,
        """
        ALTER TABLE stores 
        ADD COLUMN cuisine_type VARCHAR(50) DEFAULT NULL
        """,
        """
        UPDATE stores 
        SET store_type = 'cafe', cuisine_type = 'american' 
        WHERE store_type IS NULL OR store_type = 'cafe'
        """
    ]
    
    async with engine.begin() as conn:
        for query in migration_queries:
            try:
                await conn.execute(text(query))
                logger.info(f"Executed: {query.strip()[:50]}...")
            except Exception as e:
                logger.warning(f"Migration query failed (might already exist): {e}")
    
    logger.info("Migration completed successfully")

if __name__ == "__main__":
    asyncio.run(migrate_stores_table())