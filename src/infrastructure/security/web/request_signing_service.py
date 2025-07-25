"""Request Signing Service
Provides cryptographic request signing and validation for child safety.
Implements HMAC-based signatures with replay attack protection.
"""

from enum import Enum

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


class SignatureAlgorithm(Enum):
    """Supported signature algorithms."""

    HMAC_SHA256 = "hmac-sha256"
    HMAC_SHA512 = "hmac-sha512"
