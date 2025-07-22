"""Service providers using factory pattern."""
from .base import LazyServiceProvider

# COPPA Services


def _create_coppa_integration():
    from src.presentation.api.endpoints.children.compliance import COPPAIntegration
    from src.infrastructure.config.settings import get_settings
    from src.infrastructure.validators.security.coppa_validator import (
        COPPAValidator,
        coppa_validator
    )

    settings = get_settings()
    coppa_service = COPPAValidator()
    return COPPAIntegration(coppa_service, settings)


def _create_parental_consent_manager():
    from src.presentation.api.endpoints.children.compliance import ParentalConsentManager
    from src.infrastructure.validators.security.coppa_validator import (
        COPPAValidator,
        coppa_validator
    )

    coppa_service = COPPAValidator()
    return ParentalConsentManager(coppa_service)


def _create_compliance_validator():
    from src.presentation.api.endpoints.children.compliance import ComplianceValidator
    from src.infrastructure.config.settings import get_settings

    settings = get_settings()
    return ComplianceValidator(settings)


def _create_data_retention_manager():
    from src.presentation.api.endpoints.children.compliance import LocalRetentionManager
    from src.infrastructure.validators.security.coppa_validator import (
        COPPAValidator,
        coppa_validator
    )

    coppa_service = COPPAValidator()
    return LocalRetentionManager(coppa_service)


def _create_audio_processing_service():
    from src.application.services.device.audio_processing_service import AudioProcessingService
    return AudioProcessingService()


# Service providers
coppa_integration_provider = LazyServiceProvider(_create_coppa_integration)
parental_consent_provider = LazyServiceProvider(_create_parental_consent_manager)
compliance_validator_provider = LazyServiceProvider(_create_compliance_validator)
data_retention_provider = LazyServiceProvider(_create_data_retention_manager)
audio_processing_provider = LazyServiceProvider(_create_audio_processing_service)
