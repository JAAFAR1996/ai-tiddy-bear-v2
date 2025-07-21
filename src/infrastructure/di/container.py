"""DI Container - Facade for the new ApplicationContainer.
Maintains backward compatibility while using the new implementation.
"""
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

# Legacy compatibility exports
ProfessionalContainer = ApplicationContainer
ServiceLifetime = type('ServiceLifetime', (), {
    'SINGLETON': 'singleton',
    'TRANSIENT': 'transient',
    'FACTORY': 'factory'
})

# Re-export all necessary items
__all__ = [
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
container.child_operations_service = lambda: None
container.child_search_service = lambda: None
# Singleton instance
