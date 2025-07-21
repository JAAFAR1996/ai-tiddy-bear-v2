import bcrypt

from src.infrastructure.config.settings import get_settings
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


class PasswordHasher:
    """Service for securely hashing and verifying passwords using bcrypt.
    This implementation includes mitigations for timing attacks.
    """

    def __init__(self, settings=None) -> None:
        self.settings = settings if settings else get_settings()
        self.password_min_length = self.settings.security.PASSWORD_MIN_LENGTH
        self.bcrypt_rounds = self.settings.security.PASSWORD_HASH_ROUNDS
        logger.info(
            f"PasswordHasher initialized with {self.bcrypt_rounds} rounds "
            f"and min length of {self.password_min_length}.",
        )

    def hash_password(self, password: str) -> str:
        """Hashes a password using bcrypt with a securely generated salt."""
        if not password or len(password) < self.password_min_length:
            raise ValueError(
                f"Password does not meet security requirements. "
                f"Minimum length: {self.password_min_length} characters.",
            )
        try:
            password_bytes = password.encode("utf-8")
            salt = bcrypt.gensalt(rounds=self.bcrypt_rounds)
            hashed_bytes = bcrypt.hashpw(password_bytes, salt)
            return hashed_bytes.decode("utf-8")
        except Exception as e:
            logger.critical(
                "CRITICAL: Password hashing failed unexpectedly. "
                "This is a serious security risk.",
                exc_info=True,
            )
            # Do not expose internal error details to the caller.
            raise ValueError("Could not securely hash the password.") from e

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verifies a password against a bcrypt hash in a way that is resistant
        to timing attacks.
        """
        if not password or not hashed_password:
            return False
        try:
            password_bytes = password.encode("utf-8")
            hashed_password_bytes = hashed_password.encode("utf-8")
            # bcrypt.checkpw is the correct and secure way to verify bcrypt hashes.
            # It is designed to be slow and its internal comparison is resistant to timing attacks.
            return bcrypt.checkpw(password_bytes, hashed_password_bytes)
        except (ValueError, TypeError):
            # This can occur if the hashed_password is not a valid bcrypt hash.
            # To prevent timing analysis that could leak information about valid vs. invalid
            # hash formats, we perform a dummy hash operation to ensure a consistent
            # execution time, regardless of the input's validity.
            logger.warning(
                "Password verification failed due to a malformed hash or type error. "
                "This could indicate a security issue or data corruption.",
            )
            # Perform a dummy hash operation to mitigate timing attacks.
            self.hash_password("a" * self.password_min_length)
            return False
