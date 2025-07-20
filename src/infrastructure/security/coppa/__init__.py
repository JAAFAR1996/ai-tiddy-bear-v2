"""COPPA Compliance Package
Enterprise-grade COPPA compliance with modular architecture.
"""
from .consent_manager import COPPAConsentManager
from .data_models import (
    AuditLogEntry,
    COPPAChildData,
    DataDeletionRequest,
    DataRetentionPolicy,
    ParentConsent,
)
from .data_retention import DataRetentionManager, get_retention_manager


def get_consent_manager() -> COPPAConsentManager:
    """Factory function to get COPPA consent manager instance."""
    return COPPAConsentManager()

__all__ = [
    "AuditLogEntry",
    # Data models
    "COPPAChildData",
    "COPPAConsentManager",
    "DataDeletionRequest",
    # Managers
    "DataRetentionManager",
    "DataRetentionPolicy",
    "ParentConsent",
    "get_consent_manager",
    # Factory functions
    "get_retention_manager",
]
