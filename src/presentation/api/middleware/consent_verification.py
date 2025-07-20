"""COPPA Consent Verification Middleware
Ensures parental consent is verified at all child data collection points
"""

import json
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import HTTPException, Request, Response
from fastapi.routing import APIRoute

from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.child_safety import get_consent_manager

logger = get_logger(__name__, component="middleware")


class ConsentVerificationRoute(APIRoute):
    """Custom route class that verifies parental consent before processing requests
    that involve child data collection or interaction.
    """

    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        require_consent_types: list | None = None,
        **kwargs,
    ) -> None:
        self.require_consent_types = require_consent_types or ["data_collection"]
        super().__init__(path, endpoint, **kwargs)

    def get_route_handler(self) -> Callable[[Request], Awaitable[Response]]:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            # Extract child_id from request (path params, query params, or body)
            child_id = await self._extract_child_id(request)

            if child_id:
                # Verify consent before processing
                await self._verify_consent(request, child_id)

            # Proceed with original handler
            response = await original_route_handler(request)

            # Log data collection event
            if child_id:
                await self._log_data_collection(request, child_id)

            return response

        return custom_route_handler

    async def _extract_child_id(self, request: Request) -> str | None:
        """Extract child_id from various parts of the request."""
        try:
            # Check path parameters
            if "child_id" in request.path_params:
                return request.path_params["child_id"]

            # Check query parameters
            if "child_id" in request.query_params:
                return request.query_params["child_id"]

            # Check request body (for POST/PUT requests)
            if request.method in ["POST", "PUT", "PATCH"]:
                # Store body for later use
                body = await request.body()
                request._body = body  # Cache for later use

                # Try to parse JSON body
                if body:
                    try:
                        data = json.loads(body.decode())
                        if isinstance(data, dict) and "child_id" in data:
                            return data["child_id"]
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        pass

            return None
        except Exception as e:
            logger.error(f"Failed to extract child_id from request: {e}")
            return None

    async def _verify_consent(self, request: Request, child_id: str) -> None:
        """Verify parental consent for the child."""
        try:
            consent_manager = get_consent_manager()

            # Get parent_id from authenticated user
            user = getattr(request.state, "user", None)
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required for child data access",
                )

            parent_id = user.get("user_id")
            if not parent_id:
                raise HTTPException(
                    status_code=403,
                    detail="Parent identification required",
                )

            # Check consent for each required type
            for consent_type in self.require_consent_types:
                has_consent = await consent_manager.verify_parental_consent(
                    parent_id=parent_id,
                    child_id=child_id,
                    consent_type=consent_type,
                )

                if not has_consent:
                    logger.warning(
                        f"Consent verification failed: parent={parent_id}, "
                        f"child={child_id}, type={consent_type}",
                    )
                    raise HTTPException(
                        status_code=403,
                        detail=f"Parental consent required for {consent_type}. "
                        "Please provide consent in the parental dashboard.",
                    )

            logger.info(
                f"Consent verified: parent={parent_id}, child={child_id}, "
                f"types={self.require_consent_types}",
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Consent verification error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to verify parental consent",
            )

    async def _log_data_collection(self, request: Request, child_id: str) -> None:
        """Log the data collection event for audit trail."""
        try:
            from src.infrastructure.security.child_safety.data_models import (
                AuditLogEntry,
            )

            # Create audit log entry
            audit_entry = AuditLogEntry(
                event_type="data_collection",
                event_description=f"Child data access via {request.method} {request.url.path}",
                actor_type="api_endpoint",
                actor_id=f"{request.method}:{request.url.path}",
                target_type="child_data",
                target_id=child_id,
                coppa_relevant=True,
                metadata={
                    "method": request.method,
                    "path": request.url.path,
                    "user_agent": request.headers.get("user-agent"),
                    "ip_address": (
                        request.client.host if request.client else "unknown"
                    ),
                    "consent_types": self.require_consent_types,
                },
            )

            # In production, this would save to audit database
            logger.info(
                f"Data collection logged: {audit_entry.event_type} for child {child_id}",
            )
        except Exception as e:
            logger.error(f"Failed to log data collection event: {e}")
            # Don't fail the request for logging errors


def require_consent(*consent_types: str):
    """Decorator to mark endpoints that require specific consent types
    Usage: @require_consent("data_collection", "voice_recording")
           @router.post("/process-audio")
           async def process_audio(...): ...
    """

    def decorator(func):
        # Store consent requirements on the function
        func._consent_types = list(consent_types)
        return func

    return decorator


class ConsentVerificationMiddleware:
    """ASGI middleware to verify consent for child data operations."""

    def __init__(
        self,
        app,
        consent_required_paths: dict[str, list] | None = None,
    ) -> None:
        self.app = app
        self.consent_required_paths = consent_required_paths or {
            "/api/v1/process-audio": ["data_collection", "voice_recording"],
            "/api/v1/children": ["data_collection"],
            "/api/v1/conversations": ["data_collection", "usage_analytics"],
        }

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)

            # Check if path requires consent verification
            path = request.url.path
            required_consents = None

            for pattern, consents in self.consent_required_paths.items():
                if path.startswith(pattern):
                    required_consents = consents
                    break

            if required_consents:
                # Create custom route with consent verification
                route = ConsentVerificationRoute(
                    path=path,
                    endpoint=lambda: None,  # Placeholder
                    require_consent_types=required_consents,
                )

                # Extract and verify child_id
                child_id = await route._extract_child_id(request)
                if child_id:
                    await route._verify_consent(request, child_id)

        # Continue with the application
        await self.app(scope, receive, send)


# Export for use in FastAPI applications
__all__ = [
    "ConsentVerificationMiddleware",
    "ConsentVerificationRoute",
    "require_consent",
]
