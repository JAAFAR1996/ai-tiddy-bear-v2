import math
import re
from collections import Counter
from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from fastapi import Depends
from jose import JWTError, jwt

from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


class JWTSecurityValidator:
    """
    Comprehensive JWT secret validator with cryptographic strength requirements.

    CRITICAL CHILD SAFETY REQUIREMENT:
    - Minimum 64 characters for JWT secret
    - Shannon entropy ≥ 4.0 bits per character
    - Pattern detection for weak/guessable patterns
    - Cryptographic randomness validation
    """

    # Security constants
    MIN_SECRET_LENGTH = 64
    MIN_SHANNON_ENTROPY = 4.0

    # Weak patterns that MUST be rejected
    WEAK_PATTERNS = {
        # Common words and phrases
        "secret",
        "password",
        "key",
        "token",
        "jwt",
        "auth",
        "login",
        "admin",
        "user",
        "test",
        "dev",
        "development",
        "prod",
        "production",
        "staging",
        "demo",
        "example",
        "sample",
        "default",
        "changeme",
        "please_change",
        "change_me",
        "temp",
        "temporary",
        "placeholder",
        # Sequences and patterns
        "123",
        "456",
        "789",
        "abc",
        "def",
        "qwerty",
        "asdf",
        "zxcv",
        "000",
        "111",
        "222",
        "333",
        "444",
        "555",
        "666",
        "777",
        "888",
        "999",
        "aaa",
        "bbb",
        "ccc",
        "ddd",
        "eee",
        "fff",
        # Company/app specific
        "teddy",
        "bear",
        "child",
        "kids",
        "family",
        "parent",
        "coppa",
        "safety",
        "secure",
        "api",
        # Keyboard patterns
        "12345",
        "54321",
        "qwert",
        "asdfg",
        "zxcvb",
        # Dates and years
        "2023",
        "2024",
        "2025",
        "2026",
        "2027",
        # Common substitutions
        "@",
        "!",
        "#",
        "$",
        "%",
        "^",
        "&",
        "*",
    }

    # Patterns that indicate human-generated secrets (REJECT) - More lenient settings
    HUMAN_PATTERNS = [
        r"(.)\1{4,}",  # 5+ repeated characters (more lenient)
        r"(..)\1{3,}",  # 4+ repeated pairs (more lenient)
        r"(...)\1{3,}",  # 4+ repeated triplets (more lenient)
        r"0123|1234|2345|3456|4567|5678|6789|7890",  # Sequential numbers
        r"abcd|bcde|cdef|defg|efgh|fghi|ghij|hijk|ijkl|jklm|klmn|lmno|mnop|nopq|opqr|pqrs|qrst|rstu|stuv|tuvw|uvwx|vwxy|wxyz",  # Sequential letters
        r"[a-z]{15,}",  # 15+ consecutive lowercase (more lenient)
        r"[A-Z]{15,}",  # 15+ consecutive uppercase (more lenient)
        r"[0-9]{15,}",  # 15+ consecutive digits (more lenient)
        r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]{8,}",  # 8+ consecutive symbols (more lenient)
    ]

    def validate_jwt_secret(self, secret: str) -> bool:
        """
        Comprehensive JWT secret validation.

        Args:
            secret: JWT secret to validate

        Returns:
            bool: True if secret passes all security requirements

        Raises:
            ValueError: If secret fails any security requirement with detailed reason
        """
        # 1. Basic validation
        if not secret:
            raise ValueError("JWT secret cannot be empty")

        if not isinstance(secret, str):
            raise ValueError("JWT secret must be a string")

        # Remove whitespace for validation (but don't modify original)
        secret_clean = secret.strip()
        if not secret_clean:
            raise ValueError("JWT secret cannot be only whitespace")

        # 2. Length validation (CRITICAL)
        if len(secret_clean) < self.MIN_SECRET_LENGTH:
            raise ValueError(
                f"JWT secret must be at least {self.MIN_SECRET_LENGTH} characters long. "
                f"Current length: {len(secret_clean)}. "
                f"Weak secrets enable session hijacking and child data compromise."
            )

        # 3. Shannon entropy validation (CRITICAL)
        entropy = self._calculate_shannon_entropy(secret_clean)
        if entropy < self.MIN_SHANNON_ENTROPY:
            raise ValueError(
                f"JWT secret entropy too low: {entropy:.2f} bits/char. "
                f"Minimum required: {self.MIN_SHANNON_ENTROPY} bits/char. "
                f"Low entropy secrets are cryptographically weak and predictable."
            )

        # 4. Weak pattern detection (CRITICAL)
        if self._check_weak_patterns(secret_clean):
            raise ValueError(
                "JWT secret contains weak/guessable patterns. "
                "Secrets must be cryptographically random, not human-generated."
            )

        # 5. Human-generated pattern detection (CRITICAL)
        if self._check_human_patterns(secret_clean):
            raise ValueError(
                "JWT secret appears to be human-generated. "
                "Use cryptographically secure random generation instead."
            )

        # 6. Character distribution validation
        if not self._validate_character_distribution(secret_clean):
            raise ValueError(
                "JWT secret has poor character distribution. "
                "Use a wider range of characters for better security."
            )

        logger.info(
            f"JWT secret passed all validations: length={len(secret_clean)}, entropy={entropy:.2f}"
        )
        return True

    def _calculate_shannon_entropy(self, data: str) -> float:
        """Calculate Shannon entropy in bits per character."""
        if not data:
            return 0.0

        # Count character frequencies
        char_counts = Counter(data)
        data_length = len(data)

        # Calculate Shannon entropy
        entropy = 0.0
        for count in char_counts.values():
            probability = count / data_length
            if probability > 0:
                entropy -= probability * math.log2(probability)

        return entropy

    def _check_weak_patterns(self, secret: str) -> bool:
        """Check for weak/guessable patterns in secret."""
        secret_lower = secret.lower()

        # Check for any weak patterns
        for pattern in self.WEAK_PATTERNS:
            if pattern in secret_lower:
                logger.warning(f"Weak pattern detected: {pattern}")
                return True

        return False

    def _check_human_patterns(self, secret: str) -> bool:
        """Check for patterns indicating human-generated (non-random) secrets."""
        for pattern in self.HUMAN_PATTERNS:
            if re.search(pattern, secret, re.IGNORECASE):
                logger.warning(f"Human-generated pattern detected: {pattern}")
                return True

        return False

    def _validate_character_distribution(self, secret: str) -> bool:
        """Validate character distribution across different character classes."""
        char_classes = {
            "lowercase": sum(1 for c in secret if c.islower()),
            "uppercase": sum(1 for c in secret if c.isupper()),
            "digits": sum(1 for c in secret if c.isdigit()),
            "symbols": sum(1 for c in secret if not c.isalnum()),
        }

        total_chars = len(secret)

        # Require at least 2 different character classes (more lenient)
        used_classes = sum(1 for count in char_classes.values() if count > 0)
        if used_classes < 2:
            logger.warning("JWT secret uses insufficient character classes")
            return False

        # No single class should dominate (>90% of characters) - more lenient
        for class_name, count in char_classes.items():
            if count > (total_chars * 0.9):
                logger.warning(f"JWT secret dominated by {class_name} characters")
                return False

        return True


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

        # CRITICAL CHILD SAFETY: Comprehensive JWT secret validation
        jwt_validator = JWTSecurityValidator()
        try:
            jwt_validator.validate_jwt_secret(self.secret_key)
            logger.info("JWT secret passed comprehensive cryptographic validation")
        except ValueError as e:
            logger.critical(f"JWT SECRET VALIDATION FAILED: {e}")
            logger.critical(
                "SYSTEM STARTUP BLOCKED - JWT secret does not meet child safety security requirements"
            )
            raise ValueError(f"JWT security validation failed: {e}") from e

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
            logger.error(f"Invalid user data for token creation")
            raise ValueError("Failed to create access token")
        except JWTError as e:
            logger.error(f"JWT encoding error")
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
            logger.error(f"Invalid user data for refresh token")
            raise ValueError("Failed to create refresh token")
        except JWTError as e:
            logger.error(f"JWT encoding error")
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
            logger.error(f"JWT verification error")
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
            logger.error(f"Token refresh error")
            raise ValueError("Failed to refresh token")


def get_token_service(settings: Settings = Depends(get_settings)) -> TokenService:
    """Factory function for TokenService dependency injection."""
    return TokenService(settings)
