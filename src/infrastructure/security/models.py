from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


@dataclass
class EncryptionMetadata:
    """Encryption metadata"""
    encrypted_at: datetime
    encryption_version: str
    key_derivation: str
    field_count: int
    checksum: str


@dataclass
class COPPAComplianceRecord:
    """COPPA compliance record"""
    child_id: str
    parental_consent_given: bool
    consent_timestamp: datetime
    consent_method: str  # "email", "phone", "in_person"
    consent_ip_address: Optional[str] = None
    data_retention_expires: Optional[datetime] = None
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)