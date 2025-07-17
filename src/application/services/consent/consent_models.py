"""
Consent Management Data Models
Defines the core data structures for COPPA - compliant consent management.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional


class VerificationMethod(Enum):
    """Supported parental verification methods for COPPA compliance."""

    EMAIL_VERIFICATION = "email_verification"
    SMS_VERIFICATION = "sms_verification"
    CREDIT_CARD_VERIFICATION = "credit_card_verification"
    DIGITAL_SIGNATURE = "digital_signature"
    VIDEO_CALL_VERIFICATION = "video_call_verification"
    GOVERNMENT_ID_VERIFICATION = "government_id_verification"


class VerificationStatus(Enum):
    """Verification status states."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VERIFIED = "verified"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class ConsentRecord:
    """Core consent record structure."""

    consent_id: str
    parent_id: str
    child_id: str
    feature: str
    status: str
    requested_at: str
    expiry_date: str
    granted_at: Optional[str] = None
    revoked_at: Optional[str] = None
    verification_method: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class VerificationAttempt:
    """Verification attempt tracking."""

    attempt_id: str
    consent_id: str
    method: VerificationMethod
    status: VerificationStatus
    attempted_at: str
    completed_at: Optional[str] = None
    failure_reason: Optional[str] = None
    verification_code: Optional[str] = None
