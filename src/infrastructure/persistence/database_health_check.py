import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

logger = logging.getLogger(__name__)


async def check_database_connection(
    database_url: str,
    retries: int = 5,
    delay: float = 2.0,
) -> bool:
    """Attempts to connect to the database and execute a simple query to verify connectivity.
    Includes retry logic with exponential backoff.
    """
    engine = None
    for i in range(retries):
        try:
            logger.info(f"Attempt {i + 1}/{retries}: Connecting to database...")
            engine = create_async_engine(database_url)
            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful.")
            return True
        except Exception as e:
            logger.warning(f"❌ Database connection failed: {e}")
            if i < retries - 1:
                await asyncio.sleep(delay * (2**i))  # Exponential backoff
            else:
                logger.error("❌ All database connection attempts failed.")
        finally:
            if engine:
                await engine.dispose()
    return False
