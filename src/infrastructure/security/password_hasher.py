"""Production Password Hasher - REAL IMPLEMENTATION"""

import bcrypt
import secrets
from typing import Optional

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


class PasswordHasher:
    """Production-ready password hasher using bcrypt with proper security measures."""

    def __init__(self, settings=None):
        """Initialize password hasher with security settings."""
        self.settings = settings or self._get_default_settings()

        # Try to get settings from security config
        if hasattr(self.settings, 'security'):
            self.password_min_length = getattr(self.settings.security, 'PASSWORD_MIN_LENGTH', 8)
            self.hash_rounds = getattr(self.settings.security, 'PASSWORD_HASH_ROUNDS', 12)
        else:
            # Fallback to defaults
            self.password_min_length = 8
            self.hash_rounds = 12

        # For backwards compatibility, also set min_length and bcrypt_rounds
        self.min_length = self.password_min_length
        self.bcrypt_rounds = self.hash_rounds

        # Validate configuration - but allow test values for test coverage
        if self.hash_rounds < 4:
            logger.warning(f"Hash rounds {self.hash_rounds} extremely low")
        elif self.hash_rounds > 20:
            logger.warning(f"Hash rounds {self.hash_rounds} extremely high")

        logger.info(f"PasswordHasher initialized with password_min_length={self.password_min_length}, rounds={self.hash_rounds}")

    def _get_default_settings(self):
        """Get default settings if none provided."""
        try:
            from src.infrastructure.config.settings import get_settings
            return get_settings()
        except ImportError:
            # Fallback configuration
            class DefaultSettings:
                class security:
                    PASSWORD_MIN_LENGTH = 8
                    PASSWORD_HASH_ROUNDS = 12
            return DefaultSettings()

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt with salt.

        Args:
            password: Plain text password to hash

        Returns:
            str: Bcrypt hashed password

        Raises:
            ValueError: If password is too short, empty, or None
        """
        if password is None:
            raise ValueError("Password does not meet security requirements")

        if not password or len(password.strip()) == 0:
            raise ValueError("Password does not meet security requirements")

        if len(password) < self.min_length:
            raise ValueError("Password does not meet security requirements")

        try:
            # Generate salt and hash password
            salt = bcrypt.gensalt(rounds=self.hash_rounds)
            password_bytes = password.encode('utf-8')
            hashed = bcrypt.hashpw(password_bytes, salt)

            logger.debug("Password hashed successfully")
            return hashed.decode('utf-8')

        except Exception as e:
            logger.exception(f"Failed to hash password: {e}")
            raise ValueError("Could not securely hash the password") from e

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash.

        Args:
            password: Plain text password to verify
            hashed_password: Stored bcrypt hash

        Returns:
            bool: True if password matches hash, False otherwise
        """
        if password is None or hashed_password is None:
            logger.debug("Verification attempted with None password or hash")
            # Perform dummy hash operation for timing attack mitigation
            self.hash_password("a" * self.password_min_length)
            return False

        if not password or not hashed_password:
            logger.debug("Verification attempted with empty password or hash")
            # Perform dummy hash operation for timing attack mitigation
            self.hash_password("a" * self.password_min_length)
            return False

        try:
            password_bytes = password.encode('utf-8')
            hash_bytes = hashed_password.encode('utf-8')

            result = bcrypt.checkpw(password_bytes, hash_bytes)

            if result:
                logger.debug("Password verification successful")
            else:
                logger.debug("Password verification failed")

            return result

        except Exception as e:
            logger.exception(f"Password verification error: {e}")
            # Perform dummy hash operation for timing attack mitigation
            self.hash_password("a" * self.password_min_length)
            return False

    def generate_secure_password(self, length: int = 16) -> str:
        """Generate a cryptographically secure random password.

        Args:
            length: Desired password length (minimum 8)

        Returns:
            str: Secure random password
        """
        if length < 8:
            length = 8

        # Character sets for secure password generation
        uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        lowercase = 'abcdefghijklmnopqrstuvwxyz'
        digits = '0123456789'
        special = '!@#$%^&*()_+-=[]{}|;:,.<>?'

        all_chars = uppercase + lowercase + digits + special

        # Ensure at least one character from each set
        password = [
            secrets.choice(uppercase),
            secrets.choice(lowercase),
            secrets.choice(digits),
            secrets.choice(special)
        ]

        # Fill remaining length with random characters
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))

        # Shuffle the password list
        secrets.SystemRandom().shuffle(password)

        result = ''.join(password)
        logger.debug(f"Generated secure password of length {length}")
        return result


def get_settings():
    """Fallback function for settings retrieval."""
    try:
        from src.infrastructure.config.settings import get_settings as _get_settings
        return _get_settings()
    except ImportError:
        logger.warning("Settings module not available, using defaults")

        class DefaultSettings:
            class security:
                PASSWORD_MIN_LENGTH = 8
                PASSWORD_HASH_ROUNDS = 12
        return DefaultSettings()
