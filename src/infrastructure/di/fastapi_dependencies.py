from functools import lru_cache
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.infrastructure.caching.redis_cache import RedisCacheManager as RedisCache

from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.persistence.database_manager import Database
from src.infrastructure.security.core.main_security_service import (
    MainSecurityService,
    get_security_service,
)
from src.infrastructure.security.auth.real_auth_service import ProductionAuthService

"""FastAPI Dependency Injection Utilities"""

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="infrastructure")

# Security scheme
security = HTTPBearer()


# Core Dependencies (Singletons)
@lru_cache
def get_cached_settings() -> Settings:
    """Get cached settings instance."""
    return get_settings()


@lru_cache
def get_database(
    settings: Settings = Depends(get_cached_settings),
) -> Database:
    """Get database connection."""
    try:
        return Database(str(settings.database.DATABASE_URL))
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Return mock database for development
        from src.infrastructure.persistence.mock_database import MockDatabase

        return MockDatabase()


@lru_cache
def get_cache(
    settings: Settings = Depends(get_cached_settings),
) -> RedisCacheManager:
    """Get cache service."""
    try:
        return RedisCacheManager(str(settings.redis.REDIS_URL))
    except Exception as e:
        logger.warning(f"Redis not available, using memory cache: {e}")
        from src.infrastructure.caching.memory_cache import MemoryCache

        return MemoryCache()


@lru_cache
def get_main_security_service() -> MainSecurityService:
    """Get main security service."""
    return get_security_service()


@lru_cache
def get_auth_service(
    database: Database = Depends(get_database),
    cache: Any = Depends(get_cache),
    settings: Settings = Depends(get_cached_settings),
) -> ProductionAuthService:
    """Get authentication service."""
    return ProductionAuthService(database, cache, settings.SECRET_KEY)


# Security Dependencies
async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    auth_service: ProductionAuthService = Depends(get_auth_service),
) -> dict[str, Any]:
    """Get current user from token."""
    user = await auth_service.get_user_from_token(token.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Get current active user."""
    if not current_user.get("is_active"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
