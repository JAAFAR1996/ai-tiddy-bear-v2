"""DI Container - Facade for the new ApplicationContainer.

Maintains backward compatibility while using the new implementation.
"""

from src.application.interfaces.read_model_interfaces import IChildProfileReadModelStore
from src.application.services.child_safety.coppa_compliance_service import (
    COPPAComplianceService,
)
from src.infrastructure import dependencies
from src.infrastructure.pagination.pagination_service import PaginationService
from src.infrastructure.validators.security.coppa_validator import COPPAValidator

from .application_container import (
    ApplicationContainer,
    get_container,
    register_service,
    resolve_service,
)

# Re-export the main container
container = get_container()
Container = ApplicationContainer  # Legacy compatibility

# Legacy compatibility exports
ProfessionalContainer = ApplicationContainer
ServiceLifetime = type(
    "ServiceLifetime",
    (),
    {"SINGLETON": "singleton", "TRANSIENT": "transient", "FACTORY": "factory"},
)

# Re-export all necessary items
__all__ = [
    "Container",
    "ProfessionalContainer",
    "ServiceLifetime",
    "container",
    "register_service",
    "resolve_service",
]


def register_legacy_services():
    """Register legacy services for backward compatibility."""
    # Register as factory
    register_service(COPPAValidator, lambda: COPPAValidator())


def _get_child_profile_read_model_store():
    """Production factory for ChildProfileReadModelStore."""
    from src.infrastructure.read_models.child_profile_read_model import (
        ChildProfileReadModelStore,
    )

    return ChildProfileReadModelStore()


def _get_event_bus():
    """Production factory for KafkaEventBus."""
    from src.infrastructure.config.integrations.kafka_settings import KafkaSettings
    from src.infrastructure.messaging.kafka_event_bus import KafkaEventBus

    kafka_settings = KafkaSettings()
    return KafkaEventBus(
        bootstrap_servers=kafka_settings.KAFKA_BOOTSTRAP_SERVERS,
        schema_registry_url=kafka_settings.SCHEMA_REGISTRY_URL,
        client_id="teddy-bear-app",
    )


def _get_openai_client():
    """Production factory for OpenAIClient."""
    from src.infrastructure.config.services.ai_settings import AISettings
    from src.infrastructure.external_apis.openai_client import OpenAIClient

    ai_settings = AISettings()
    return OpenAIClient(api_key=ai_settings.OPENAI_API_KEY)


def _build_child_operations():
    """Build child operations service."""
    # Import only when needed to avoid circular dependency
    from src.presentation.api.endpoints.children.operations import ChildOperations

    return ChildOperations(
        manage_child_profile_use_case=container.manage_child_profile_use_case(),
        coppa_compliance_service=container.coppa_compliance_service(),
        pagination_service=container.pagination_service(),
    )


# Auto-register legacy services on import
register_legacy_services()

# Register concrete services in DI container
register_service(IChildProfileReadModelStore, _get_child_profile_read_model_store)
register_service("IEventBus", _get_event_bus)
register_service("IAIProvider", _get_openai_client)

# Register services as attributes for backward compatibility
container.manage_child_profile_use_case = dependencies.get_manage_child_profile_use_case
container.pagination_service = lambda: PaginationService()
container.coppa_compliance_service = lambda: COPPAComplianceService()

# Legacy attribute access for backward compatibility
container.child_profile_read_model_store = _get_child_profile_read_model_store
container.event_bus = _get_event_bus
container.openai_client = _get_openai_client

# Re-enabled for Phase 2 - child operations service
container.child_operations_service = _build_child_operations
