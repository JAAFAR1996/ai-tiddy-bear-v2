"""COPPA Compliance Package
Enterprise-grade COPPA compliance with modular architecture"""

from .data_models import (
    ChildData,
    ParentConsent,
    DataRetentionPolicy,
    AuditLogEntry,
    DataDeletionRequest)
from .data_retention import DataRetentionManager, get_retention_manager
from .consent_manager import ConsentManager, get_consent_manager

__all__ = [
    # Data models
    "ChildData",
    "ParentConsent",
    "DataRetentionPolicy",
    "AuditLogEntry",
    "DataDeletionRequest",
    # Managers
    "DataRetentionManager",
    "ConsentManager",
    # Factory functions
    "get_retention_manager",
    "get_consent_manager"
]