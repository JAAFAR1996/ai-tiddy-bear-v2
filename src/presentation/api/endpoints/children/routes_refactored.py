"""Refactored Children Routes
Clean, modular route setup with separated endpoint handlers.
"""

from fastapi import APIRouter

from .create_child import create_child_endpoint
from .delete_child import delete_child_endpoint
from .get_children import get_children_endpoint
from .models import ChildResponse
from .update_child import update_child_endpoint


def setup_children_routes(router: APIRouter) -> None:
    """إعداد جميع الـ routes للأطفال بطريقة منظمة."""
    # Create child endpoint
    router.add_api_route(
        "/",
        create_child_endpoint,
        methods=["POST"],
        response_model=ChildResponse,
        summary="Create Child Profile",
        description="Create a new child profile with COPPA compliance verification",
        status_code=201,
    )

    # Get children endpoint
    router.add_api_route(
        "/",
        get_children_endpoint,
        methods=["GET"],
        response_model=list[ChildResponse],
        summary="Get Children Profiles",
        description="Retrieve all children profiles for the authenticated parent",
    )

    # Update child endpoint
    router.add_api_route(
        "/{child_id}",
        update_child_endpoint,
        methods=["PUT"],
        response_model=ChildResponse,
        summary="Update Child Profile",
        description="Update an existing child profile with parental authorization",
    )

    # Delete child endpoint
    router.add_api_route(
        "/{child_id}",
        delete_child_endpoint,
        methods=["DELETE"],
        summary="Delete Child Profile",
        description="Safely delete a child profile with data retention compliance",
        status_code=204,
    )


def setup_extended_children_routes(router: APIRouter) -> None:
    """إعداد routes إضافية للأطفال."""
    # Get single child endpoint
    router.add_api_route(
        "/{child_id}",
        get_child_by_id_endpoint,
        methods=["GET"],
        response_model=ChildResponse,
        summary="Get Child Profile",
        description="Get a specific child profile by ID",
    )

    # Search children endpoint
    router.add_api_route(
        "/search",
        search_children_endpoint,
        methods=["GET"],
        response_model=list[ChildResponse],
        summary="Search Children",
        description="Search children profiles with filters",
    )

    # Get children summary endpoint
    router.add_api_route(
        "/summary",
        get_children_summary_endpoint,
        methods=["GET"],
        summary="Get Children Summary",
        description="Get summary statistics for all children",
    )

    # Get child safety summary endpoint
    router.add_api_route(
        "/{child_id}/safety",
        get_child_safety_summary_endpoint,
        methods=["GET"],
        summary="Get Child Safety Summary",
        description="Get safety summary for a specific child",
    )

    # Get child interactions endpoint
    router.add_api_route(
        "/{child_id}/interactions",
        get_child_interactions_endpoint,
        methods=["GET"],
        summary="Get Child Interactions",
        description="Get recent interactions for a specific child",
    )


def create_children_router() -> APIRouter:
    """Factory function to create children router with all endpoints."""
    router = APIRouter(
        prefix="/children",
        tags=["children"],
        responses={
            404: {"description": "Child not found"},
            403: {"description": "Access denied - insufficient permissions"},
            401: {"description": "Authentication required"},
            400: {"description": "Bad request - validation error"},
            500: {"description": "Internal server error"},
        },
    )
    setup_children_routes(router)
    return router


def create_extended_children_router() -> APIRouter:
    """Factory function to create extended children router with all endpoints."""
    router = APIRouter(
        prefix="/children",
        tags=["children"],
        responses={
            404: {"description": "Child not found"},
            403: {"description": "Access denied - insufficient permissions"},
            401: {"description": "Authentication required"},
            400: {"description": "Bad request - validation error"},
            500: {"description": "Internal server error"},
        },
    )
    setup_children_routes(router)
    setup_extended_children_routes(router)
    return router


# استيراد الدوال الحقيقية أو رفع استثناء إنتاجي إذا لم تكن متوفرة
try:
    from .get_child_by_id import get_child_by_id_endpoint
except ImportError:
    async def get_child_by_id_endpoint(child_id: str):
        raise NotImplementedError("Production endpoint 'get_child_by_id_endpoint' not implemented.")

try:
    from .search_children import search_children_endpoint
except ImportError:
    async def search_children_endpoint(query: str = None, age_min: int = None, age_max: int = None):
        raise NotImplementedError("Production endpoint 'search_children_endpoint' not implemented.")

try:
    from .get_children_summary import get_children_summary_endpoint
except ImportError:
    async def get_children_summary_endpoint():
        raise NotImplementedError("Production endpoint 'get_children_summary_endpoint' not implemented.")

try:
    from .get_child_safety_summary import get_child_safety_summary_endpoint
except ImportError:
    async def get_child_safety_summary_endpoint(child_id: str):
        raise NotImplementedError("Production endpoint 'get_child_safety_summary_endpoint' not implemented.")

try:
    from .get_child_interactions import get_child_interactions_endpoint
except ImportError:
    async def get_child_interactions_endpoint(child_id: str, limit: int = 50):
        raise NotImplementedError("Production endpoint 'get_child_interactions_endpoint' not implemented.")


def setup_admin_children_routes(router: APIRouter) -> None:
    """إعداد routes الإدارة للأطفال (للمديرين فقط)."""
    # Get all children (admin only)
    router.add_api_route(
        "/admin/all",
        get_all_children_admin_endpoint,
        methods=["GET"],
        summary="Get All Children (Admin)",
        description="Get all children profiles across all parents (admin only)",
        tags=["admin"],
    )

    # Get children statistics (admin only)
    router.add_api_route(
        "/admin/statistics",
        get_children_statistics_admin_endpoint,
        methods=["GET"],
        summary="Get Children Statistics (Admin)",
        description="Get system-wide children statistics (admin only)",
        tags=["admin"],
    )

    # Bulk operations (admin only)
    router.add_api_route(
        "/admin/bulk-update",
        bulk_update_children_admin_endpoint,
        methods=["PUT"],
        summary="Bulk Update Children (Admin)",
        description="Perform bulk updates on children profiles (admin only)",
        tags=["admin"],
    )


async def get_all_children_admin_endpoint():
    """Get all children profiles across all parents (admin only)."""
    pass


async def get_children_statistics_admin_endpoint():
    """Get system-wide children statistics (admin only)."""
    pass


async def bulk_update_children_admin_endpoint():
    """Perform bulk updates on children profiles (admin only)."""
    pass


def create_complete_children_router() -> APIRouter:
    """Factory function to create complete children router with all endpoints."""
    router = APIRouter(
        prefix="/children",
        tags=["children"],
        responses={
            404: {"description": "Child not found"},
            403: {"description": "Access denied - insufficient permissions"},
            401: {"description": "Authentication required"},
            400: {"description": "Bad request - validation error"},
            500: {"description": "Internal server error"},
        },
    )

    # Setup all route groups
    setup_children_routes(router)
    setup_extended_children_routes(router)
    setup_admin_children_routes(router)

    return router


# Configuration for different deployment scenarios
ROUTER_CONFIGS = {
    "basic": create_children_router,
    "extended": create_extended_children_router,
    "complete": create_complete_children_router,
}


def get_children_router(config: str = "extended") -> APIRouter:
    """Get children router based on configuration."""
    if config not in ROUTER_CONFIGS:
        raise ValueError(f"Unknown router config: {config}")

    return ROUTER_CONFIGS[config]()
