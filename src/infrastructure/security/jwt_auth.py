"""JWT Authentication module for FastAPI users"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

try:
    from fastapi_users import FastAPIUsers
    from fastapi_users.authentication import (
        AuthenticationBackend,
        BearerTransport,
        JWTStrategy,
    )
    from fastapi_users_sqlalchemy import (
        SQLAlchemyBaseUserTableUUID,
        SQLAlchemyUserDatabase,
    )

    FASTAPI_USERS_AVAILABLE = True
except ImportError:
    FASTAPI_USERS_AVAILABLE = False

    # Mock classes for when fastapi-users is not installed
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
    from src.infrastructure.config.settings import get_settings
except ImportError:

    def get_settings():
        """Mock settings function"""

        class MockSettings:
            class Security:
                JWT_SECRET_KEY = "your-secret-key-here"

            security = Security()

        return MockSettings()


try:
    from src.infrastructure.persistence.models.base import Base
except ImportError:
    from sqlalchemy.orm import declarative_base

    Base = declarative_base()

try:
    from src.infrastructure.security.vault_client import get_vault_client
except ImportError:

    async def get_vault_client():
        """Mock vault client function"""
        return


class User(SQLAlchemyBaseUserTableUUID, Base):
    """User model extending FastAPI Users base table"""

    __tablename__ = "users"

    # Additional fields for your user model, if any
    # For example:
    # first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    # last_name: Mapped[str] = mapped_column(String(255), nullable=True)


async def get_user_db(
    session: AsyncSession,
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    """Get user database instance"""
    if not FASTAPI_USERS_AVAILABLE:
        raise ImportError("fastapi-users is required but not installed")

    yield SQLAlchemyUserDatabase(session, User)


async def get_jwt_strategy() -> JWTStrategy:
    """Get JWT strategy with secure configuration"""
    if not FASTAPI_USERS_AVAILABLE:
        raise ImportError("fastapi-users is required but not installed")

    settings = get_settings()
    vault_client = await get_vault_client()
    jwt_secret = None

    # Try to get JWT secret from vault first
    if vault_client:
        try:
            secrets = await vault_client.get_secret("jwt-secrets")
            jwt_secret = secrets.get("JWT_SECRET")
        except Exception:
            # Fallback to settings if vault fails
            pass

    # Fallback to settings
    if not jwt_secret:
        try:
            jwt_secret = settings.security.JWT_SECRET_KEY
        except AttributeError:
            jwt_secret = None

    # Validate JWT secret
    if not jwt_secret or jwt_secret.strip() == "":
        raise ValueError(
            "JWT secret is empty or not configured. "
            "Set JWT_SECRET environment variable with a secure key."
        )

    if len(jwt_secret) < 32:
        raise ValueError(
            "JWT secret is too short. " "Must be at least 32 characters for security."
        )

    # Check for insecure secrets
    insecure_secrets = {
        "secret",
        "jwt_secret",
        "changeme",
        "default",
        "dev",
        "test",
        "password",
        "your-secret-key-here",
    }
    if jwt_secret.lower() in insecure_secrets:
        raise ValueError(
            "JWT secret uses a common/insecure value. "
            "Use a cryptographically secure random key."
        )

    return JWTStrategy(secret=jwt_secret, lifetime_seconds=3600)


def create_auth_components():
    """Create authentication components"""
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


# Initialize components if fastapi-users is available
if FASTAPI_USERS_AVAILABLE:
    auth_components = create_auth_components()
    bearer_transport = auth_components["bearer_transport"]
    auth_backend = auth_components["auth_backend"]
    fastapi_users = auth_components["fastapi_users"]
    current_active_user = auth_components["current_active_user"]
else:
    # Provide None values when not available
    bearer_transport = None
    auth_backend = None
    fastapi_users = None
    current_active_user = None
