
from functools import lru_cache
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.infrastructure.caching.redis_cache import RedisCacheManager
from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.persistence.database_manager import Database
from src.infrastructure.security.core.main_security_service import (
    MainSecurityService,
    get_security_service,
)
from src.infrastructure.security.auth.real_auth_service import ProductionAuthService
from src.domain.entities.user import User

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
        logger.critical(f"Database initialization failed: {e}")
        raise RuntimeError(
            "Production database connection failed. Database service is required for operation."
        )


@lru_cache
def get_cache(
    settings: Settings = Depends(get_cached_settings),
) -> RedisCacheManager:
    """Get cache service."""
    try:
        return RedisCacheManager(str(settings.redis.REDIS_URL))
    except Exception as e:
        logger.critical(f"Redis not available: {e}")
        raise RuntimeError(
            "Production Redis connection failed. Redis service is required for operation."
        )


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
    token: HTTPAuthorizationCredentials = None,
    auth_service: ProductionAuthService = None,
) -> User:
    """Get current user from token as User model."""
    if token is None:
        token = Depends(security)
        token = token()
    if auth_service is None:
        auth_service = Depends(get_auth_service)
        auth_service = auth_service()
    user_data = await auth_service.get_user_from_token(token.credentials)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # تحويل dict إلى كائن User
    return User(
        id=user_data["id"],
        email=user_data["email"],
        role=user_data["role"],
        name=user_data.get("name", ""),
        is_active=user_data.get("is_active", True),
        created_at=user_data.get("created_at"),
        last_login=user_data.get("last_login"),
    )


async def get_current_active_user(
    current_user: User = None,
) -> User:
    if current_user is None:
        current_user = Depends(get_current_user)
        current_user = current_user()
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
