from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from fastapi import Depends
from jose import JWTError, jwt

from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


class TokenService:
    """Service for creating, verifying, and managing JWT tokens."""

    def __init__(self, settings: Settings = Depends(get_settings)) -> None:
        self.settings = settings
        self.secret_key = self.settings.security.SECRET_KEY
        self.algorithm = self.settings.security.JWT_ALGORITHM
        self.access_token_expire_minutes = (
            self.settings.security.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        self.refresh_token_expire_days = (
            self.settings.security.REFRESH_TOKEN_EXPIRE_DAYS
        )

        if not self.secret_key or len(self.secret_key) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")

    def create_access_token(self, user_data: dict[str, Any]) -> str:
        """Create JWT access token with user data."""
        try:
            to_encode = {
                "sub": user_data["id"],
                "email": user_data["email"],
                "role": user_data["role"],
                "type": "access",
                "jti": str(uuid4()),
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow()
                + timedelta(minutes=self.access_token_expire_minutes),
            }
            return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        except (KeyError, TypeError) as e:
            logger.error(f"Invalid user data for token creation: {e}")
            raise ValueError("Failed to create access token")
        except JWTError as e:
            logger.error(f"JWT encoding error: {e}")
            raise ValueError("Failed to create access token")

    def create_refresh_token(self, user_data: dict[str, Any]) -> str:
        """Create JWT refresh token."""
        try:
            to_encode = {
                "sub": user_data["id"],
                "email": user_data["email"],
                "type": "refresh",
                "jti": str(uuid4()),
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow()
                + timedelta(days=self.refresh_token_expire_days),
            }
            return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        except (KeyError, TypeError) as e:
            logger.error(f"Invalid user data for refresh token: {e}")
            raise ValueError("Failed to create refresh token")
        except JWTError as e:
            logger.error(f"JWT encoding error: {e}")
            raise ValueError("Failed to create refresh token")

    async def verify_token(self, token: str) -> dict[str, Any]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Validate required fields
            if "jti" not in payload:
                raise ValueError("Token missing JWT ID field")

            return payload
        except JWTError as e:
            logger.error(f"JWT verification error: {e}")
            raise ValueError("Invalid token")

    async def refresh_access_token(self, refresh_token: str) -> str:
        """Create new access token from refresh token."""
        try:
            payload = await self.verify_token(refresh_token)

            if payload.get("type") != "refresh":
                raise ValueError("Invalid refresh token")

            user_data = {
                "id": payload["sub"],
                "email": payload["email"],
                "role": payload.get("role", "user"),
            }
            return self.create_access_token(user_data)
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            raise ValueError("Failed to refresh token")
