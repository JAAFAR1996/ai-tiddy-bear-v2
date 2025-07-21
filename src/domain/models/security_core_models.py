from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class EncryptionMetadata:
    """Encryption metadata."""

    encrypted_at: datetime
    encryption_version: str
    key_derivation: str
    field_count: int
    checksum: str


@dataclass
class COPPAValidatorRecord:
    """COPPA compliance record."""

    child_id: str
    parental_consent_given: bool
    consent_timestamp: datetime
    consent_method: str  # "email", "phone", "in_person"
    consent_ip_address: str | None = None
    data_retention_expires: datetime | None = None
    audit_trail: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    
    enable_rate_limiting: bool = True
    enable_audit_logging: bool = True
    enable_encryption: bool = True
    max_login_attempts: int = 5
    session_timeout_minutes: int = 30
    require_https: bool = True
    enable_2fa: bool = False
    min_password_length: int = 8
