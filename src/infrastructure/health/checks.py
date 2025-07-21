import asyncio
from typing import Any

import httpx
import redis.asyncio as redis
from pydantic import BaseModel
from sqlalchemy import text

from src.infrastructure.config.settings import get_settings
from src.infrastructure.logging_config import get_logger
from src.infrastructure.persistence.database_manager import Database

logger = get_logger(__name__, component="infrastructure")


class DependencyCheck(BaseModel):
    """Individual dependency check result."""

    name: str
    status: str  # "healthy", "unhealthy", "unknown"
    response_time_ms: float
    details: dict[str, Any]
    error: str = None


async def check_database() -> DependencyCheck:
    """Check database connectivity and health."""
    start_time = asyncio.get_event_loop().time()
    try:
        settings = get_settings()
        database = Database(str(settings.database.DATABASE_URL))
        # Test connection
        async with database.get_session() as session:
            await session.execute(text("SELECT 1"))
        response_time = (asyncio.get_event_loop().time() - start_time) * 1000
        return DependencyCheck(
            name="database",
            status="healthy",
            response_time_ms=response_time,
            details={"provider": "postgresql", "connection_pool": "active"},
        )
    except Exception as e:
        response_time = (asyncio.get_event_loop().time() - start_time) * 1000
        return DependencyCheck(
            name="database",
            status="unhealthy",
            response_time_ms=response_time,
            details={},
            error=str(e),
        )


async def check_redis() -> DependencyCheck:
    """Check Redis connectivity and health."""
    start_time = asyncio.get_event_loop().time()
    try:
        settings = get_settings()
        redis_client = redis.from_url(
            str(settings.redis.REDIS_URL),
            decode_responses=True,
        )
        # Test connection
        await redis_client.ping()
        info = await redis_client.info()
        await redis_client.close()
        response_time = (asyncio.get_event_loop().time() - start_time) * 1000
        return DependencyCheck(
            name="redis",
            status="healthy",
            response_time_ms=response_time,
            details={
                "version": info.get("redis_version", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "unknown"),
            },
        )
    except Exception as e:
        response_time = (asyncio.get_event_loop().time() - start_time) * 1000
        return DependencyCheck(
            name="redis",
            status="unhealthy",
            response_time_ms=response_time,
            details={},
            error=str(e),
        )


async def check_openai() -> DependencyCheck:
    """Check OpenAI API connectivity."""
    start_time = asyncio.get_event_loop().time()
    try:
        settings = get_settings()
        # Test OpenAI API with a minimal request
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {settings.ai.OPENAI_API_KEY}"},
                timeout=10.0,
            )
        response_time = (asyncio.get_event_loop().time() - start_time) * 1000
        if response.status_code == 200:
            return DependencyCheck(
                name="openai",
                status="healthy",
                response_time_ms=response_time,
                details={
                    "api_status": "accessible",
                    "rate_limit_remaining": response.headers.get(
                        "x-ratelimit-remaining-requests",
                        "unknown",
                    ),
                },
            )
        return DependencyCheck(
            name="openai",
            status="unhealthy",
            response_time_ms=response_time,
            details={"status_code": response.status_code},
            error=f"API returned status {response.status_code}",
        )
    except Exception as e:
        response_time = (asyncio.get_event_loop().time() - start_time) * 1000
        return DependencyCheck(
            name="openai",
            status="unhealthy",
            response_time_ms=response_time,
            details={},
            error=str(e),
        )


async def check_all_dependencies() -> list[DependencyCheck]:
    """Check all external dependencies concurrently."""
    tasks = [
        check_database(),
        check_redis(),
        check_openai(),
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    dependency_checks = []
    for result in results:
        if isinstance(result, Exception):
            dependency_checks.append(
                DependencyCheck(
                    name="unknown",
                    status="unhealthy",
                    response_time_ms=0.0,
                    details={},
                    error=str(result),
                ),
            )
        else:
            dependency_checks.append(result)
    return dependency_checks
