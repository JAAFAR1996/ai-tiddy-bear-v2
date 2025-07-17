# Standard library imports

# Third-party imports
try:
    from fastapi import APIRouter, HTTPException, status

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

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

"""Children Endpoints Package - Modular structure for better organization
This package provides child-safe API endpoints with COPPA compliance,
comprehensive safety monitoring, and parental control features."""

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="api")

# FastAPI Router setup - handle import failure
if not FASTAPI_AVAILABLE:
    logger.warning("FastAPI not available, using mock classes")

    class APIRouter:
        def __init__(self, *args, **kwargs) -> None:
            self.prefix = kwargs.get("prefix", "")
            self.tags = kwargs.get("tags", [])

        def post(self, path: str, **kwargs):
            def decorator(func):
                func._route_info = {"method": "POST", "path": path, **kwargs}
                return func

            return decorator

        def get(self, path: str, **kwargs):
            def decorator(func):
                func._route_info = {"method": "GET", "path": path, **kwargs}
                return func

            return decorator

        def put(self, path: str, **kwargs):
            def decorator(func):
                func._route_info = {"method": "PUT", "path": path, **kwargs}
                return func

            return decorator

        def delete(self, path: str, **kwargs):
            def decorator(func):
                func._route_info = {"method": "DELETE", "path": path, **kwargs}
                return func

            return decorator

    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str) -> None:
            self.status_code = status_code
            self.detail = detail

    class status:
        HTTP_200_OK = 200
        HTTP_201_CREATED = 201
        HTTP_404_NOT_FOUND = 404
        HTTP_500_INTERNAL_SERVER_ERROR = 500


# Create router instance with versioning
router = APIRouter(prefix="/api/v1/children", tags=["Children v1"])

# Apply routes to the router if available
if ROUTES_AVAILABLE:
    setup_routes(router)
else:
    logger.warning("Routes module not available")

# Export router for use in main application
__all__ = [
    "COPPAIntegration",
    # Models
    "ChildCreateRequest",
    "ChildDeleteResponse",
    # Services
    "ChildOperations",
    "ChildResponse",
    "ChildSafetyManager",
    "ChildSafetySummary",
    "ChildUpdateRequest",
    "ContentSafetyFilter",
    "PrivacyProtectionManager",
    "SafetyEventTypes",
    "UsageMonitor",
    # Operations
    "create_child",
    "delete_child",
    "get_child",
    # Safety
    "get_child_safety_summary",
    "get_children",
    "handle_compliant_child_deletion",
    "record_safety_event",
    "request_parental_consent",
    # FastAPI Router
    "router",
    "track_child_usage",
    "update_child",
    # Compliance
    "validate_child_creation_compliance",
    "validate_data_access_permission",
    "validate_interaction_safety",
]

if not FASTAPI_AVAILABLE:
    logger.info("Children endpoints package loaded in mock mode")
else:
    logger.info("Children endpoints package loaded successfully")
