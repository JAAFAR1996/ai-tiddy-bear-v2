"""Children Endpoints Package - Modular structure for better organization

This package provides child-safe API endpoints with COPPA compliance,
comprehensive safety monitoring, and parental control features.
"""

# Standard library imports

# Third-party imports
from fastapi import APIRouter, HTTPException, status


# Local imports
from .compliance import (
    COPPAIntegration,
    handle_compliant_child_deletion,
    request_parental_consent,
    validate_child_creation_compliance,
    validate_data_access_permission,
)
from .models import (
    ChildCreateRequest,
    ChildDeleteResponse,
    ChildResponse,
    ChildSafetySummary,
    ChildUpdateRequest,
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
if not FASTAPI_AVAILABLE:
    logger.info("Children endpoints package loaded in mock mode")
else:
    logger.info("Children endpoints package loaded successfully")

# Export router for use in main application
__all__ = [
    # FastAPI Router
    "router",
    # Compliance
    "COPPAIntegration",
    "handle_compliant_child_deletion",
    "request_parental_consent",
    "validate_child_creation_compliance",
    "validate_data_access_permission",
    # Models
    "ChildCreateRequest",
    "ChildDeleteResponse",
    "ChildResponse",
    "ChildSafetySummary",
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
