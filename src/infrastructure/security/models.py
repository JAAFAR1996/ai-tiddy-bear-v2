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
class COPPAComplianceRecord:
    """COPPA compliance record."""

    child_id: str
    parental_consent_given: bool
    consent_timestamp: datetime
    consent_method: str  # "email", "phone", "in_person"
    consent_ip_address: str | None = None
    data_retention_expires: datetime | None = None
    audit_trail: list[dict[str, Any]] = field(default_factory=list)
