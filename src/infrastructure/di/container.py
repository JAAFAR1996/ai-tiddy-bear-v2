"""DI Container - Facade for the new ApplicationContainer.
Maintains backward compatibility while using the new implementation.
"""
# Delayed import to avoid circular dependency - imports only when service is needed
# from src.presentation.api.endpoints.children.operations import ChildOperations
from src.application.services.child_safety.coppa_compliance_service import COPPAComplianceService
from src.infrastructure.pagination.pagination_service import PaginationService
from src.infrastructure import dependencies
from src.infrastructure.validators.security.coppa_validator import COPPAValidator
from .application_container import (
    ApplicationContainer,
    get_container,
    register_service,
    resolve_service
)
# Re-export the main container
container = get_container()
Container = ApplicationContainer  # Legacy compatibility

# Legacy compatibility exports
ProfessionalContainer = ApplicationContainer
ServiceLifetime = type('ServiceLifetime', (), {
    'SINGLETON': 'singleton',
    'TRANSIENT': 'transient',
    'FACTORY': 'factory'
})

# Re-export all necessary items
__all__ = [
    'Container',
    'container',
    'ProfessionalContainer',
    'ServiceLifetime',
    'register_service',
    'resolve_service'
]

# Legacy service registration


def register_legacy_services():
    """Register legacy services for backward compatibility."""

    # Register as factory
    register_service(COPPAValidator,
                     lambda: COPPAValidator()
                     )


# Auto-register legacy services on import
register_legacy_services()

# Register COPPA integration service

# Add required service attributes

# Register services as attributes
container.manage_child_profile_use_case = dependencies.get_manage_child_profile_use_case
container.pagination_service = lambda: PaginationService()
container.coppa_compliance_service = lambda: COPPAComplianceService()


# Re-enabled for Phase 2 - lazy import to avoid circular dependency
def _build_child_operations():
    # Import only when needed to avoid circular dependency
    from src.presentation.api.endpoints.children.operations import ChildOperations
    return ChildOperations(
        manage_child_profile_use_case=container.manage_child_profile_use_case(),
        coppa_compliance_service=container.coppa_compliance_service(),
        pagination_service=container.pagination_service(),
    )


# Re-enabled for Phase 2 - child operations service
container.child_operations_service = _build_child_operations
# Singleton instance
