import asyncio
from typing import Any

import httpx
import redis.asyncio as redis
from pydantic import BaseModel
from sqlalchemy import text

from src.infrastructure.config.settings import get_settings
from src.infrastructure.logging_config import get_logger
from src.infrastructure.persistence.database_manager import Database

# Import Vault health check
try:
    from src.infrastructure.security.vault_client import VaultClient

    VAULT_AVAILABLE = True
except ImportError:
    VAULT_AVAILABLE = False

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


async def check_vault() -> DependencyCheck:
    """Check HashiCorp Vault connectivity and health."""
    start_time = asyncio.get_event_loop().time()

    if not VAULT_AVAILABLE:
        return DependencyCheck(
            name="vault",
            status="unknown",
            response_time_ms=0.0,
            details={"note": "Vault client not available"},
            error="Vault integration not configured",
        )

    try:
        settings = get_settings()
        if not settings.security.VAULT_ENABLED:
            return DependencyCheck(
                name="vault",
                status="disabled",
                response_time_ms=0.0,
                details={"note": "Vault integration disabled"},
                error=None,
            )

        # Create Vault client and test connection
        vault_client = VaultClient(
            vault_url=settings.security.VAULT_URL,
            vault_token=settings.security.VAULT_TOKEN.get_secret_value()
            if settings.security.VAULT_TOKEN
            else None,
            namespace=settings.security.VAULT_NAMESPACE,
        )

        # Perform health check
        health_result = await vault_client.health_check()
        response_time = (asyncio.get_event_loop().time() - start_time) * 1000

        if health_result.get("is_healthy", False):
            return DependencyCheck(
                name="vault",
                status="healthy",
                response_time_ms=response_time,
                details={
                    "vault_url": health_result.get("vault_url", "unknown"),
                    "is_authenticated": health_result.get("is_authenticated", False),
                    "is_sealed": health_result.get("is_sealed", True),
                    "version": health_result.get("version", "unknown"),
                },
            )
        else:
            return DependencyCheck(
                name="vault",
                status="unhealthy",
                response_time_ms=response_time,
                details=health_result.get("details", {}),
                error=health_result.get("error", "Vault health check failed"),
            )

    except Exception as e:
        response_time = (asyncio.get_event_loop().time() - start_time) * 1000
        return DependencyCheck(
            name="vault",
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
        check_vault(),  # Add Vault check
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
