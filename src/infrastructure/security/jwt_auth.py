# type: ignore
# from fastapi_users import FastAPIUsers  # type: ignore
# from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy  # type: ignore
# from fastapi_users_sqlalchemy import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession

# from src.infrastructure.config.settings import get_settings
# from src.infrastructure.persistence.database import Base
# from src.infrastructure.security.vault_client import get_vault_client


class User(SQLAlchemyBaseUserTableUUID, Base):  # type: ignore
    __tablename__ = "users"

    # Additional fields for your user model, if any
    # For example:
    # first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    # last_name: Mapped[str] = mapped_column(String(255), nullable=True)


async def get_user_db(session: AsyncSession) -> SQLAlchemyUserDatabase[User]:
    yield SQLAlchemyUserDatabase(session, User)


async def get_jwt_strategy() -> JWTStrategy:
    settings = get_settings()
    vault_client = await get_vault_client()
    jwt_secret = None

    if vault_client:
        secrets = await vault_client.get_secret("jwt-secrets")
        jwt_secret = secrets.get("JWT_SECRET")

    if not jwt_secret:
        try:
            jwt_secret = settings.security.JWT_SECRET_KEY
        except AttributeError:
            jwt_secret = None

    if not jwt_secret or jwt_secret.strip() == "":
        raise ValueError(
            "JWT secret is empty or not configured. Set JWT_SECRET environment variable with a secure key.",
        )

    if len(jwt_secret) < 32:
        raise ValueError(
            "JWT secret is too short. Must be at least 32 characters for security.",
        )

    insecure_secrets = {
        "secret",
        "jwt_secret",
        "changeme",
        "default",
        "dev",
        "test",
        "password",
    }
    if jwt_secret.lower() in insecure_secrets:
        raise ValueError(
            "JWT secret uses a common/insecure value. Use a cryptographically secure random key.",
        )

    return JWTStrategy(secret=jwt_secret, lifetime_seconds=3600)


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

current_active_user = fastapi_users.current_active_user
