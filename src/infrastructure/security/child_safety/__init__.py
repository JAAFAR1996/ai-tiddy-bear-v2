"""Child safety and COPPA compliance services."""

from .child_data_security_manager import ChildDataSecurityManager
from .consent_manager import COPPAConsentManager
from .data_retention import DataRetentionManager

# Global instances
_consent_manager_instance = None


def get_consent_manager() -> COPPAConsentManager:
    """Get or create the global consent manager instance."""
    if _consent_manager_instance is None:
        return COPPAConsentManager()
    return _consent_manager_instance


__all__ = [
    "ChildDataSecurityManager",
    "COPPAConsentManager",
    "DataRetentionManager",
    "get_consent_manager",
]
