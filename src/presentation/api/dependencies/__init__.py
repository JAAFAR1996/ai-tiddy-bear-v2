"""Professional dependency injection system."""

from .providers import (
    audio_processing_provider,
    compliance_validator_provider,
    coppa_integration_provider,
    data_retention_provider,
    parental_consent_provider,
)


# Audio dependencies
def get_audio_processing_service():
    """Get audio processing service."""
    return audio_processing_provider.get()


# Compliance dependencies
def get_coppa_integration():
    """Get COPPA integration service."""
    return coppa_integration_provider.get()


def get_parental_consent_manager():
    """Get parental consent manager."""
    return parental_consent_provider.get()


def get_compliance_validator():
    """Get compliance validator."""
    return compliance_validator_provider.get()


def get_data_retention_manager():
    """Get data retention manager."""
    return data_retention_provider.get()


__all__ = [
    "get_audio_processing_service",
    "get_coppa_integration",
    "get_data_retention_manager",
    "get_parental_consent_manager",
]
