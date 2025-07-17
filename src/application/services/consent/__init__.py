"""
COPPA - Compliant Consent Management Package
Modular consent management system providing enterprise - grade COPPA compliance
for child data collection and processing.
"""

from .consent_models import (
    VerificationMethod,
    VerificationStatus,
    ConsentRecord,
    VerificationAttempt)
from .consent_service import ConsentService
from .verification_service import VerificationService

__all__ = [
    "ConsentService",
    "VerificationService",
    "VerificationMethod",
    "VerificationStatus",
    "ConsentRecord",
    "VerificationAttempt"
]