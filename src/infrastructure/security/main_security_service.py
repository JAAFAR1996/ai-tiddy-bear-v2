# Standard library imports
import os
import re
import secrets
from typing import Any

# Local imports
from ..config.settings import get_settings
from .child_data_encryption import ChildDataEncryption
from .rate_limiter import RateLimiter
from .real_auth_service import ProductionAuthService

"""Main security service - unified implementation"""
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


class MainSecurityService:
    """Unified security service consolidating all security features."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self.settings = get_settings()
        # Initialize sub-services
        self.auth_service = ProductionAuthService(
            database_session=self.config.get("database"),
            redis_cache=self.config.get("redis"),
        )
        self.encryption_service = ChildDataEncryption(
            encryption_key=self.settings.SECRET_KEY,
        )
        self.rate_limiter = RateLimiter(redis_client=self.config.get("redis"))
        logger.info("Main security service initialized")

    # Authentication methods (delegate to auth service)
    async def authenticate_user(
        self,
        email: str,
        password: str,
        ip_address: str | None = None,
    ):
        """Authenticate user with rate limiting."""
        return await self.auth_service.authenticate_user(email, password, ip_address)

    async def create_token(self, user_data: dict[str, Any]) -> str:
        """Create JWT token."""
        return self.auth_service.create_access_token(user_data)

    async def verify_token(self, token: str) -> dict[str, Any] | None:
        """Verify JWT token."""
        return await self.auth_service.verify_token(token)

    # Encryption methods (delegate to encryption service)
    def encrypt_child_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Encrypt sensitive child data."""
        return self.encryption_service.encrypt_child_data(data)

    def decrypt_child_data(self, encrypted_data: dict[str, Any]) -> dict[str, Any]:
        """Decrypt child data."""
        return self.encryption_service.decrypt_child_data(encrypted_data)

    # Security utility methods
    def generate_secure_password(self, length: int = 12) -> str:
        """Generate cryptographically secure password."""
        alphabet = (
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        )
        return "".join(secrets.choice(alphabet) for _ in range(length))

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        return self.auth_service.hash_password(password)

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        return self.auth_service.verify_password(password, hashed)

    def validate_input(
        self,
        input_data: str,
        input_type: str = "text",
    ) -> dict[str, Any]:
        """Validate and sanitize user input."""
        # Basic input validation
        if not input_data:
            return {"valid": False, "error": "Input cannot be empty"}
        # Type-specific validation
        if input_type == "email":
            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, input_data):
                return {"valid": False, "error": "Invalid email format"}
        elif input_type == "child_name":
            if len(input_data) > 50:
                return {"valid": False, "error": "Name too long"}
            if not re.match(r"^[a-zA-Z\s\'-]+$", input_data):
                return {"valid": False, "error": "Name contains invalid characters"}
        return {"valid": True, "sanitized": input_data.strip()}

    # Rate limiting methods
    async def check_rate_limit(self, identifier: str, limit: int | None = None) -> bool:
        """Check if request is within rate limit."""
        return await self.rate_limiter.check_rate_limit(
            identifier,
            max_requests=limit or self.settings.RATE_LIMIT_PER_MINUTE,
        )

    # Session management
    def generate_session_id(self) -> str:
        """Generate secure session ID."""
        return secrets.token_urlsafe(32)

    def generate_csrf_token(self) -> str:
        """Generate CSRF protection token."""
        return secrets.token_urlsafe(32)

    def validate_production_environment_security(self) -> list[str]:
        """Validates production environment security settings within the security service."""
        errors = []
        # Access environment variables directly to validate against secure
        # settings
        if os.getenv("DEBUG", "false").lower() in ("true", "1", "yes", "on"):
            errors.append("DEBUG mode is enabled in production.")
        # Ensure COPPA is enabled in production for child safety
        if os.getenv("COPPA_COMPLIANCE_MODE", "true").lower() in (
            "false",
            "0",
            "no",
            "off",
        ):
            errors.append("COPPA_COMPLIANCE_MODE is disabled in production.")

        # Example: Check for default/weak secret keys if not already handled by
        # settings validation
        dangerous_values = [
            "changeme",
            "test",
            "development",
            "default",
            "secret",
            "password",
            "12345",
        ]
        secret_key = self.settings.security.SECRET_KEY
        jwt_secret = self.settings.security.JWT_SECRET_KEY

        for dangerous in dangerous_values:
            if dangerous.lower() in secret_key.lower():
                errors.append(f"SECRET_KEY contains unsafe value: {dangerous}")
            if dangerous.lower() in jwt_secret.lower():
                errors.append(f"JWT_SECRET_KEY contains unsafe value: {dangerous}")

        return errors


# Factory function
def get_security_service(
    config: dict[str, Any] | None = None,
) -> MainSecurityService:
    """Get or create main security service instance."""
    return MainSecurityService(config)
