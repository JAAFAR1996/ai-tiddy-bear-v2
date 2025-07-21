"""JWT Authentication module for FastAPI users"""

from src.infrastructure.config import get_settings
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from fastapi_users import FastAPIUsers
    from fastapi_users.authentication import (
        AuthenticationBackend,
        BearerTransport,
        JWTStrategy,
    )
    from fastapi_users_db_sqlalchemy import (
        SQLAlchemyBaseUserTableUUID,
        SQLAlchemyUserDatabase,
    )
    FASTAPI_USERS_AVAILABLE = True
except ImportError:
    FASTAPI_USERS_AVAILABLE = False

    class SQLAlchemyBaseUserTableUUID:
        pass

    class SQLAlchemyUserDatabase:
        pass

    class JWTStrategy:
        pass

    class BearerTransport:
        pass

    class AuthenticationBackend:
        pass

    class FastAPIUsers:
        pass

try:
    from src.domain.models.models_infra.base import Base
except ImportError:
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()

try:
    from src.infrastructure.security.encryption.vault_client import get_vault_client
except ImportError:
    async def get_vault_client():
        """Mock vault client function"""
        return

from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

class User(SQLAlchemyBaseUserTableUUID, Base):
    """User model extending FastAPI Users base table"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    email = Column(String(320), unique=True, index=True, nullable=False)
    hashed_password = Column(String(1024), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, active={self.is_active})>"

async def get_user_db(
    session: AsyncSession,
) -> AsyncGenerator["SQLAlchemyUserDatabase", None]:
    if not FASTAPI_USERS_AVAILABLE:
        raise ImportError("fastapi-users is required but not installed")
    yield SQLAlchemyUserDatabase(session, User)

async def get_jwt_strategy() -> "JWTStrategy":
    if not FASTAPI_USERS_AVAILABLE:
        raise ImportError("fastapi-users is required but not installed")
    settings = get_settings()
    vault_client = await get_vault_client()
    jwt_secret = None
    if vault_client:
        try:
            secrets = await vault_client.get_secret("jwt-secrets")
            jwt_secret = secrets.get("JWT_SECRET")
        except Exception:
            pass
    if not jwt_secret:
        try:
            jwt_secret = settings.security.JWT_SECRET_KEY
        except AttributeError:
            jwt_secret = None
    if not jwt_secret or jwt_secret.strip() == "":
        raise ValueError(
            "JWT secret is empty or not configured. "
            "Set JWT_SECRET environment variable with a secure key."
        )
    if len(jwt_secret) < 32:
        raise ValueError(
            "JWT secret is too short. Must be at least 32 characters for security."
        )
    insecure_secrets = {
        "secret", "jwt_secret", "changeme", "default", "dev", "test", "password", "your-secret-key-here",
    }
    if jwt_secret.lower() in insecure_secrets:
        raise ValueError(
            "JWT secret uses a common/insecure value. "
            "Use a cryptographically secure random key."
        )
    return JWTStrategy(secret=jwt_secret, lifetime_seconds=3600)

def create_auth_components():
    if not FASTAPI_USERS_AVAILABLE:
        raise ImportError("fastapi-users is required but not installed")
    bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
    auth_backend = AuthenticationBackend(
        name="jwt",
        transport=bearer_transport,
        get_strategy=get_jwt_strategy,
    )
    fastapi_users = FastAPIUsers(
        get_user_db,
        [auth_backend],
        User=User,
        UserCreate=User,
        UserUpdate=User,
        UserDB=User,
    )
    return {
        "bearer_transport": bearer_transport,
        "auth_backend": auth_backend,
        "fastapi_users": fastapi_users,
        "current_active_user": fastapi_users.current_active_user,
    }

if FASTAPI_USERS_AVAILABLE:
    auth_components = create_auth_components()
    bearer_transport = auth_components["bearer_transport"]
    auth_backend = auth_components["auth_backend"]
    fastapi_users = auth_components["fastapi_users"]
    current_active_user = auth_components["current_active_user"]
else:
    bearer_transport = None
    auth_backend = None
    fastapi_users = None
    current_active_user = None
