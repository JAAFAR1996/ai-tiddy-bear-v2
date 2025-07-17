"""COPPA Compliance Package
Enterprise-grade COPPA compliance with modular architecture.
"""

from .consent_manager import ConsentManager, get_consent_manager
from .data_models import (
    AuditLogEntry,
    ChildData,
    DataDeletionRequest,
    DataRetentionPolicy,
    ParentConsent,
)
from .data_retention import DataRetentionManager, get_retention_manager

__all__ = [
    "AuditLogEntry",
    # Data models
    "ChildData",
    "ConsentManager",
    "DataDeletionRequest",
    # Managers
    "DataRetentionManager",
    "DataRetentionPolicy",
    "ParentConsent",
    "get_consent_manager",
    # Factory functions
    "get_retention_manager",
]
