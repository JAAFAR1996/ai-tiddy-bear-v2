"""Children Endpoints Package - Modular structure for better organization

This package provides child-safe API endpoints with COPPA compliance,
comprehensive safety monitoring, and parental control features.
"""

# Standard library imports

# Third-party imports
from fastapi import APIRouter

# Local imports
# Re-enabled for Phase 2 - compliance module fixed
from .compliance import (
    COPPAComplianceRouter,
    COPPAIntegration,
    ParentalConsentRouter,
    PrivacyProtectionRouter,
    handle_compliant_child_deletion,
    request_parental_consent,
    validate_child_creation_compliance,
    validate_data_access_permission,
)

# Re-enabled for Phase 2 - models module created
from .models import (
    ChildCreateRequest,
    ChildDeleteResponse,
    ChildProfileModel,
    ChildResponse,
    ChildSafetySummary,
    ChildUpdateRequest,
    InteractionModel,
    SafetyConfigModel,
)
from .operations import (
    ChildOperations,
    create_child,
    delete_child,
    get_child,
    get_children,
    update_child,
)
from .safety import (
    ChildSafetyManager,
    ContentSafetyFilter,
    PrivacyProtectionManager,
    SafetyEventTypes,
    UsageMonitor,
    get_child_safety_summary,
    record_safety_event,
    track_child_usage,
    validate_interaction_safety,
)

# Import route handlers with error handling
try:
    from .routes import setup_routes

    ROUTES_AVAILABLE = True
except ImportError:
    ROUTES_AVAILABLE = False

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="api")

# Create router instance with versioning
router = APIRouter(prefix="/api/v1/children", tags=["Children v1"])

# Apply routes to the router if available
if ROUTES_AVAILABLE:
    setup_routes(router)
else:
    logger.warning("Routes module not available")

# Log package initialization status
logger.info("Children endpoints package loaded successfully")

# Export router for use in main application
__all__ = [
    # FastAPI Router
    "router",
    # Compliance routers - re-enabled for Phase 2
    "COPPAComplianceRouter",
    "ParentalConsentRouter",
    "PrivacyProtectionRouter",
    # Compliance functions - re-enabled for Phase 2
    "COPPAIntegration",
    "handle_compliant_child_deletion",
    "request_parental_consent",
    "validate_child_creation_compliance",
    "validate_data_access_permission",
    # Models - re-enabled for Phase 2
    "ChildCreateRequest",
    "ChildDeleteResponse",
    "ChildResponse",
    "ChildSafetySummary",
    "ChildProfileModel",
    "InteractionModel",
    "SafetyConfigModel",
    "ChildUpdateRequest",
    # Operations
    "ChildOperations",
    "create_child",
    "delete_child",
    "get_child",
    "get_children",
    "update_child",
    # Safety
    "ChildSafetyManager",
    "ContentSafetyFilter",
    "PrivacyProtectionManager",
    "SafetyEventTypes",
    "UsageMonitor",
    "get_child_safety_summary",
    "record_safety_event",
    "track_child_usage",
    "validate_interaction_safety",
]
