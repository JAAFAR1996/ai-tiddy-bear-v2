
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class ConsentType(str, Enum):
    EXPLICIT = "explicit"
    IMPLICIT = "implicit"
    # Add more types if needed


class VerificationMethod(str, Enum):
    EMAIL_VERIFICATION = "email"
    SMS_VERIFICATION = "sms"


class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"


@dataclass
class VerificationAttempt:
    attempt_id: str
    consent_id: str
    method: VerificationMethod
    status: VerificationStatus
    attempted_at: str
    verification_code: str
    completed_at: Optional[str] = None
    failure_reason: Optional[str] = None


class ConsentStatus(str, Enum):
    PENDING = "pending"
    GRANTED = "granted"
    REVOKED = "revoked"
    EXPIRED = "expired"
    # Add more statuses if needed


@dataclass
class ConsentRecord:
    consent_id: str
    child_id: str
    parent_id: str
    type: ConsentType
    status: ConsentStatus
    issued_at: str
    revoked_at: Optional[str] = None
