"""DI Container - Facade for the new ApplicationContainer.
Maintains backward compatibility while using the new implementation.
"""
from src.infrastructure.di.application_container import (
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
    from src.infrastructure.security.coppa_validator import (
        COPPAValidator,
        coppa_validator,
        is_coppa_subject,
        requires_parental_consent
    )
    
    # Register as factory
    register_service(
        COPPAValidator,
        lambda: COPPAValidator()
    )
    
# Auto-register legacy services on import
register_legacy_services()

# Register COPPA integration service

# Add required service attributes
from src.infrastructure import dependencies
from src.infrastructure.pagination import PaginationService
from src.infrastructure.security.coppa_validator import COPPAValidator
from src.application.services.coppa.coppa_compliance_service import COPPAComplianceService

# Register services as attributes
container.manage_child_profile_use_case = dependencies.get_manage_child_profile_use_case
container.pagination_service = lambda: PaginationService()

# استخدام الخدمة الجديدة بدلاً من COPPAValidator مباشرة
container.coppa_compliance_service = lambda: COPPAComplianceService()

container.child_operations_service = lambda: None
container.child_search_service = lambda: None
