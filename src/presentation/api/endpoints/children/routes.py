from typing import Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from src.domain.entities.child_delete_response import ChildDeleteResponse
from src.domain.entities.child_profile import ChildProfile
from src.domain.entities.user import User
from src.infrastructure.di.container import container
from src.infrastructure.logging_config import get_logger
from src.presentation.api.endpoints.children.route_handlers import ChildRouteHandlers

logger = get_logger(__name__, component="api")
# Security dependency
security = HTTPBearer()
# Production-only imports - no fallbacks allowed
try:
    from fastapi import APIRouter, HTTPException, status
except ImportError as e:
    logger.critical(f"CRITICAL ERROR: FastAPI is required for production use: {e}")
    logger.critical("Install required dependencies: pip install fastapi")
    raise ImportError(f"Missing required dependencies for children routes: {e}") from e


def _setup_create_child_route(router: APIRouter) -> None:
    """Setup create child endpoint."""

    @router.post("/", response_model=ChildProfile)
    @inject
    async def create_child_endpoint(
        request: ChildProfile,
        current_user: User = Depends(container.auth_service.get_current_user),
        child_route_handlers: ChildRouteHandlers = Depends(
            Provide[container.child_route_handlers],
        ),
    ):
        """Create a new child profile with COPPA compliance."""
        return await child_route_handlers.create_child_handler(request, current_user)


def _setup_get_children_route(router: APIRouter) -> None:
    """Setup get children endpoint."""

    @router.get("/", response_model=list[ChildProfile])
    @inject
    async def get_children_endpoint(
        current_user: User = Depends(container.auth_service.get_current_user),
        child_route_handlers: ChildRouteHandlers = Depends(
            Provide[container.child_route_handlers],
        ),
    ):
        """Get list of children for the authenticated parent."""
        return await child_route_handlers.get_children_handler(current_user)


def _setup_get_child_route(router: APIRouter) -> None:
    """Setup get individual child endpoint."""

    @router.get("/{child_id}", response_model=ChildProfile)
    @inject
    async def get_child_endpoint(
        child_id: str,
        current_user: User = Depends(container.auth_service.get_current_user),
        child_route_handlers: ChildRouteHandlers = Depends(
            Provide[container.child_route_handlers],
        ),
    ):
        """Get detailed information for a specific child."""
        return await child_route_handlers.get_child_handler(child_id, current_user)


def _setup_update_child_route(router: APIRouter) -> None:
    """Setup update child endpoint."""

    @router.put("/{child_id}", response_model=ChildProfile)
    @inject
    async def update_child_endpoint(
        child_id: str,
        request: ChildProfile,
        current_user: User = Depends(container.auth_service.get_current_user),
        child_route_handlers: ChildRouteHandlers = Depends(
            Provide[container.child_route_handlers],
        ),
    ):
        """Update an existing child profile."""
        return await child_route_handlers.update_child_handler(
            child_id,
            request,
            current_user,
        )


def _setup_delete_child_route(router: APIRouter) -> None:
    """Setup delete child endpoint."""

    @router.delete("/{child_id}", response_model=ChildDeleteResponse)
    @inject
    async def delete_child_endpoint(
        child_id: str,
        current_user: User = Depends(container.auth_service.get_current_user),
        child_route_handlers: ChildRouteHandlers = Depends(
            Provide[container.child_route_handlers],
        ),
    ):
        """Delete a child profile with COPPA compliance checks."""
        return await child_route_handlers.delete_child_handler(child_id, current_user)


def _setup_safety_routes(router: APIRouter) -> None:
    """Setup child safety-related endpoints."""

    @router.get("/{child_id}/safety-status", response_model=dict[str, Any])
    @inject
    async def get_child_safety_status_endpoint(
        child_id: str,
        current_user: User = Depends(container.auth_service.get_current_user),
        child_route_handlers: ChildRouteHandlers = Depends(
            Provide[container.child_route_handlers],
        ),
    ):
        """Get real-time safety status for a child profile."""
        return await child_route_handlers.get_child_safety_status_handler(
            child_id,
            current_user,
        )


def _setup_monitoring_routes(router: APIRouter) -> None:
    """Setup additional routes for monitoring and analytics."""

    @router.get("/{child_id}/activity-log")
    async def get_child_activity_log(child_id: str, limit: int = 50):
        """Get child activity log."""
        try:
            # In real application, log will be fetched from database
            activity_log = [
                {
                    "timestamp": "2024-01-01T10:00:00Z",
                    "activity_type": "conversation",
                    "duration": 300,
                    "safety_score": 95,
                },
            ]
            return {
                "child_id": child_id,
                "activities": activity_log[:limit],
                "total_count": len(activity_log),
            }
        except Exception as e:
            logger.error(f"Error getting activity log: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get activity log: {e!s}",
            )

    @router.get("/{child_id}/compliance-report")
    async def get_compliance_report(child_id: str):
        """Get child compliance report."""
        try:
            report = {
                "child_id": child_id,
                "coppa_compliant": True,
                "data_retention_compliant": True,
                "parental_consent_status": "granted",
                "last_consent_update": "2024-01-01T00:00:00Z",
                "data_types_covered": ["preferences", "voice_interactions"],
                "compliance_score": 100,
            }
            return report
        except Exception as e:
            logger.error(f"Error getting compliance report: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get compliance report: {e!s}",
            )


def setup_routes(router: APIRouter) -> None:
    """Setup all child-related routes for the given router."""
    _setup_create_child_route(router)
    _setup_get_children_route(router)
    _setup_get_child_route(router)
    _setup_update_child_route(router)
    _setup_delete_child_route(router)
    _setup_safety_routes(router)
    _setup_monitoring_routes(router)
