"""from typing import List
from fastapi import APIRouter
from .create_child import create_child_endpoint
from .delete_child import delete_child_endpoint
from .get_children import get_children_endpoint
from .models import ChildCreateRequest, ChildResponse, ChildUpdateRequest
from .update_child import update_child_endpoint.
"""

"""Refactored Children Routes
Clean, modular route setup with separated endpoint handlers."""


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
    )

    # Get children endpoint
    router.add_api_route(
        "/",
        get_children_endpoint,
        methods=["GET"],
        response_model=List[ChildResponse],
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
        },
    )
    setup_children_routes(router)
    return router
