"""Consent Management Data Models
Defines the core data structures for COPPA - compliant consent management.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


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
class VerificationAttempt:
    """Verification attempt tracking."""

    attempt_id: str
    consent_id: str
    method: VerificationMethod
    status: VerificationStatus
    attempted_at: str
    completed_at: str | None = None
    failure_reason: str | None = None
    verification_code: str | None = None
