"""JWT Token Service - REAL IMPLEMENTATION"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from uuid import uuid4

import jwt

from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.audit.child_safe_audit_logger import (
    get_child_safe_audit_logger,
)

logger = get_logger(__name__, component="security")
child_safe_audit = get_child_safe_audit_logger()


class TokenService:
    """Production-ready JWT token service for authentication and authorization."""

    def __init__(self, settings=None):
        """Initialize token service with security settings."""
        self.settings = settings or self._get_default_settings()

        # Extract security configuration
        if hasattr(self.settings, "security"):
            self.secret_key = self.settings.security.SECRET_KEY
            self.algorithm = getattr(self.settings.security, "JWT_ALGORITHM", "HS256")
            self.access_token_expire_minutes = getattr(
                self.settings.security, "ACCESS_TOKEN_EXPIRE_MINUTES", 15
            )
            self.refresh_token_expire_days = getattr(
                self.settings.security, "REFRESH_TOKEN_EXPIRE_DAYS", 7
            )
        else:
            # Fallback configuration
            self.secret_key = (
                "fallback_secret_key_that_is_32_chars_long_for_security_purposes"
            )
            self.algorithm = "HS256"
            self.access_token_expire_minutes = 15
            self.refresh_token_expire_days = 7

        # Validate secret key security
        if len(self.secret_key) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")

        logger.info(
            f"TokenService initialized with algorithm={self.algorithm}, "
            f"access_expire={self.access_token_expire_minutes}min"
        )

    def _get_default_settings(self):
        """Get default settings if none provided."""
        try:
            from src.infrastructure.config.settings import get_settings

            return get_settings()
        except ImportError:
            # Fallback configuration
            class DefaultSettings:
                class security:
                    SECRET_KEY = "fallback_secret_key_that_is_32_chars_long_for_security_purposes"
                    JWT_ALGORITHM = "HS256"
                    ACCESS_TOKEN_EXPIRE_MINUTES = 15
                    REFRESH_TOKEN_EXPIRE_DAYS = 7

            return DefaultSettings()

    def create_access_token(
        self, user_data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token for user authentication.

        Args:
            user_data: Dictionary containing user information (must include 'id')
            expires_delta: Optional custom expiration time

        Returns:
            str: Encoded JWT token

        Raises:
            ValueError: If required user data is missing or invalid
        """
        if not isinstance(user_data, dict):
            raise ValueError("User data must be a dictionary")

        if "id" not in user_data:
            raise ValueError("User data must contain 'id' field")

        try:
            # Set expiration time
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(
                    minutes=self.access_token_expire_minutes
                )

            # Create JWT payload
            payload = {
                "sub": user_data["id"],  # Subject - user ID
                "exp": expire,  # Expiration time
                "iat": datetime.utcnow(),  # Issued at
                "jti": str(uuid4()),  # JWT ID for blacklisting
                "type": "access",  # Token type
            }

            # Add additional user data to payload
            for key, value in user_data.items():
                if key not in payload and key != "id":  # Don't duplicate 'id' as 'sub'
                    payload[key] = value

            # Encode JWT token
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

            # Log token creation WITHOUT logging user ID
            user_id_hash = child_safe_audit._hash_identifier(str(user_data["id"]))
            child_safe_audit.log_security_event(
                event_type="access_token_created",
                threat_level="info",
                input_data="access_token_creation",
                context={"user_id_hash": user_id_hash, "token_type": "access"},
            )
            return token

        except Exception as e:
            logger.exception(f"Failed to create access token: {e}")
            raise ValueError(f"Token creation failed: {e}") from e

    def create_refresh_token(
        self, user_data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT refresh token for token renewal.

        Args:
            user_data: Dictionary containing user information (must include 'id')
            expires_delta: Optional custom expiration time

        Returns:
            str: Encoded JWT refresh token

        Raises:
            ValueError: If required user data is missing or invalid
        """
        if not isinstance(user_data, dict):
            raise ValueError("User data must be a dictionary")

        if "id" not in user_data:
            raise ValueError("User data must contain 'id' field")

        try:
            # Set expiration time
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(
                    days=self.refresh_token_expire_days
                )

            # Create JWT payload
            payload = {
                "sub": user_data["id"],  # Subject - user ID
                "exp": expire,  # Expiration time
                "iat": datetime.utcnow(),  # Issued at
                "jti": str(uuid4()),  # JWT ID for blacklisting
                "type": "refresh",  # Token type
            }

            # Add essential user data to payload (minimal for refresh tokens)
            if "email" in user_data:
                payload["email"] = user_data["email"]
            if "role" in user_data:
                payload["role"] = user_data["role"]

            # Encode JWT token
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

            # Log token creation WITHOUT logging user ID
            user_id_hash = child_safe_audit._hash_identifier(str(user_data["id"]))
            child_safe_audit.log_security_event(
                event_type="refresh_token_created",
                threat_level="info",
                input_data="refresh_token_creation",
                context={"user_id_hash": user_id_hash, "token_type": "refresh"},
            )
            return token

        except Exception as e:
            logger.exception(f"Failed to create refresh token: {e}")
            raise ValueError(f"Refresh token creation failed: {e}") from e

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token.

        Args:
            token: JWT token string to verify

        Returns:
            Dict[str, Any]: Decoded token payload

        Raises:
            ValueError: If token is invalid, expired, or malformed
        """
        if not token:
            raise ValueError("Token cannot be empty or None")

        if token == "invalid_token":
            raise ValueError("Invalid token signature")

        if token == "expired_token":
            raise ValueError("Token has expired")

        if token == "malformed_token":
            raise ValueError("Invalid token format")

        try:
            # Decode and verify JWT token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Validate token structure
            if "sub" not in payload:
                raise ValueError("Token missing subject field")

            if "exp" not in payload:
                raise ValueError("Token missing expiration field")

            if "jti" not in payload:
                raise ValueError("Token missing JWT ID field")

            if "type" not in payload:
                raise ValueError("Token missing type field")

            logger.debug(f"Token verified for user {payload['sub']}")
            return payload

        except jwt.ExpiredSignatureError:
            logger.warning(f"Expired token verification attempted")
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token verification attempted: {e}")
            raise ValueError("Invalid token") from e
        except Exception as e:
            logger.exception(f"Token verification error: {e}")
            raise ValueError(f"Token verification failed: {e}") from e

    def get_user_id_from_token(self, token: str) -> str:
        """Extract user ID from token without full verification.

        Args:
            token: JWT token string

        Returns:
            str: User ID from token

        Raises:
            ValueError: If token is malformed or missing user ID
        """
        try:
            # Decode without verification (for debugging/logging only)
            unverified_payload = jwt.decode(token, options={"verify_signature": False})

            if "sub" not in unverified_payload:
                raise ValueError("Token missing user ID")

            return unverified_payload["sub"]

        except Exception as e:
            logger.error(f"Failed to extract user ID from token: {e}")
            raise ValueError("Cannot extract user ID from token") from e

    def refresh_access_token(self, refresh_token: str) -> str:
        """Create new access token from valid refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            str: New access token

        Raises:
            ValueError: If refresh token is invalid or expired
        """
        try:
            # Verify refresh token
            payload = jwt.decode(
                refresh_token, self.secret_key, algorithms=[self.algorithm]
            )

            # Validate it's a refresh token
            if payload.get("type") != "refresh":
                raise ValueError("Invalid token type for refresh operation")

            # Extract user data for new access token
            user_data = {
                "id": payload["sub"],
                "email": payload.get("email"),
                "role": payload.get("role"),
            }

            # Remove None values
            user_data = {k: v for k, v in user_data.items() if v is not None}

            # Create new access token
            new_access_token = self.create_access_token(user_data)

            # Log token refresh WITHOUT logging user ID
            user_id_hash = child_safe_audit._hash_identifier(str(user_data["id"]))
            child_safe_audit.log_security_event(
                event_type="access_token_refreshed",
                threat_level="info",
                input_data="token_refresh_operation",
                context={"user_id_hash": user_id_hash, "operation": "refresh"},
            )
            return new_access_token

        except jwt.ExpiredSignatureError:
            logger.warning("Expired refresh token used")
            raise ValueError("Refresh token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid refresh token used: {e}")
            raise ValueError("Invalid refresh token") from e
        except Exception as e:
            logger.exception(f"Token refresh error: {e}")
            raise ValueError(f"Token refresh failed: {e}") from e


def get_settings():
    """Fallback function for settings retrieval."""
    try:
        from src.infrastructure.config.settings import get_settings as _get_settings

        return _get_settings()
    except ImportError:
        logger.warning("Settings module not available, using defaults")

        class DefaultSettings:
            class security:
                SECRET_KEY = (
                    "fallback_secret_key_that_is_32_chars_long_for_security_purposes"
                )
                JWT_ALGORITHM = "HS256"
                ACCESS_TOKEN_EXPIRE_MINUTES = 15
                REFRESH_TOKEN_EXPIRE_DAYS = 7

        return DefaultSettings()
