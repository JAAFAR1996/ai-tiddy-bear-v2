"""COPPA - Compliant Consent Management Package
Modular consent management system providing enterprise - grade COPPA compliance
for child data collection and processing.
"""
# استيراد ConsentRecord من domain models
from src.domain.models.consent_models import ConsentRecord

# استيراد الباقي من المكان المحلي
from .consent_models import (
    VerificationAttempt,
    VerificationMethod,
    VerificationStatus,
)
from .consent_service import ConsentService
from .verification_service import VerificationService

__all__ = [
    "ConsentRecord",
    "ConsentService", 
    "VerificationAttempt",
    "VerificationMethod",
    "VerificationService",
    "VerificationStatus",
]
