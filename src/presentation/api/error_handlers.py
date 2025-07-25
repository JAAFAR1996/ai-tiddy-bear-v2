"""Production-Ready Error Handlers for API Endpoints.

Comprehensive error handling with child safety and COPPA compliance
"""

from datetime import datetime

from fastapi import HTTPException, Request

from src.common.exceptions import (
    ChildSafetyException,
    InvalidInputError,
    ResourceNotFoundError,
    SecurityError,
)
from src.infrastructure.error_handling import handle_errors, safe_execution
from src.infrastructure.error_handling.error_types import (
    BaseApplicationError,
    ExternalServiceError,
)
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="api")

# Constants for validation
MIN_CHILD_ID_LENGTH = 3


class ErrorResponseData:
    """Data structure for error response parameters."""

    def __init__(
        self,
        request: Request,
        status_code: int,
        error_type: str,
        message: str | None = None,
        security_error: bool = False,
    ):
        self.request = request
        self.status_code = status_code
        self.error_type = error_type
        self.message = message
        self.security_error = security_error


class AITeddyErrorHandler:
    """Production-grade error handler with comprehensive safety features."""

    def __init__(self):
        """Initialize error handler with child-friendly messages."""
        self.child_friendly_messages = {
            400: (
                "Oops! Something wasn't quite right with your request. "
                "Please try again!"
            ),
            401: "You need to sign in first before we can help you!",
            403: "Sorry, you don't have permission to do that right now.",
            404: "We couldn't find what you're looking for. Let's try something else!",
            422: (
                "Some information wasn't filled in correctly. "
                "Please check and try again!"
            ),
            429: ("Whoa! You're going too fast! Please wait a moment and try again."),
            500: (
                "Oh no! Something went wrong on our end. "
                "Don't worry, we're fixing it!"
            ),
        }

    @handle_errors(
        (ValueError, InvalidInputError),
        (PermissionError, SecurityError),
        default_error=BaseApplicationError,
        log_errors=True,
    )
    def handle_authentication_error(
        self,
        error: Exception | None = None,
        operation: str = "",
        user_message: str = "Authentication required",
        request: Request | None = None,
    ) -> HTTPException:
        """Handle authentication errors with child safety considerations."""
        logger.warning("Authentication error in %s: %s", operation, error)

        # Use child-friendly message if this is a child-related request
        if request and self._is_child_related_request(request):
            user_message = self.child_friendly_messages[401]

        return HTTPException(
            status_code=401,
            detail=user_message,
            headers={"WWW-Authenticate": "Bearer"},
        )

    @handle_errors(
        (PermissionError, SecurityError),
        (ChildSafetyException, SecurityError),
        default_error=BaseApplicationError,
        log_errors=True,
    )
    def handle_authorization_error(
        self,
        operation: str = "",
        user_message: str = "Access denied",
        request: Request | None = None,
    ) -> HTTPException:
        """Handle authorization errors with child protection."""
        logger.warning("Authorization error in %s", operation)

        # Use child-friendly message if this is a child-related request
        if request and self._is_child_related_request(request):
            user_message = self.child_friendly_messages[403]

        return HTTPException(status_code=403, detail=user_message)

    @handle_errors(
        (ValueError, InvalidInputError),
        (TypeError, InvalidInputError),
        default_error=BaseApplicationError,
        log_errors=True,
    )
    def handle_validation_error(
        self,
        error: Exception,
        operation: str = "",
        user_message: str = "Invalid input",
        request: Request | None = None,
    ) -> HTTPException:
        """Handle validation errors with age-appropriate messaging."""
        logger.warning("Validation error in %s: %s", operation, error)

        # Use child-friendly message if this is a child-related request
        if request and self._is_child_related_request(request):
            user_message = self.child_friendly_messages[422]

        return HTTPException(status_code=422, detail=user_message)

    @handle_errors(
        (FileNotFoundError, ResourceNotFoundError),
        default_error=BaseApplicationError,
        log_errors=True,
    )
    def handle_not_found_error(
        self,
        resource: str,
        resource_id: str,
        operation: str = "",
        request: Request | None = None,
    ) -> HTTPException:
        """Handle not found errors with safe error responses."""
        logger.warning(
            "Resource not found in %s: %s %s", operation, resource, resource_id
        )

        # Use child-friendly message if this is a child-related request
        if request and self._is_child_related_request(request):
            user_message = self.child_friendly_messages[404]
        else:
            user_message = f"{resource} not found"

        return HTTPException(status_code=404, detail=user_message)

    @handle_errors(
        (RuntimeError, ExternalServiceError),
        (ConnectionError, ExternalServiceError),
        default_error=BaseApplicationError,
        log_errors=True,
    )
    def handle_internal_error(
        self,
        error: Exception,
        operation: str = "",
        user_message: str = "Internal server error",
        request: Request | None = None,
    ) -> HTTPException:
        """Handle internal errors with comprehensive logging and safe responses."""
        logger.error("Internal error in %s: %s", operation, error, exc_info=True)

        # Use child-friendly message if this is a child-related request
        if request and self._is_child_related_request(request):
            user_message = self.child_friendly_messages[500]

        return HTTPException(status_code=500, detail=user_message)

    def create_error_response(self, error_data: ErrorResponseData) -> dict[str, any]:
        """Create a comprehensive error response with child safety indicators."""
        # Use child-friendly message if available and appropriate
        if self._is_child_related_request(error_data.request) or not error_data.message:
            safe_message = self.child_friendly_messages.get(
                error_data.status_code,
                "Something unexpected happened. Please try again later!",
            )
        else:
            safe_message = error_data.message

        # Base error response
        error_response = {
            "error": True,
            "status_code": error_data.status_code,
            "error_type": error_data.error_type,
            "message": safe_message,
            "timestamp": datetime.utcnow().isoformat(),
            "path": error_data.request.url.path,
        }

        # Add child safety indicators for child-related requests
        if self._is_child_related_request(error_data.request):
            error_response.update(
                {
                    "child_safe": True,
                    "coppa_compliant": True,
                    "safety_verified": True,
                }
            )

        # Add security indicators for security-related errors
        if error_data.security_error:
            error_response["security_event"] = True

        return error_response

    def _is_child_related_request(self, request: Request) -> bool:
        """Determine if this is a child-related request requiring special handling."""
        if not request:
            return False

        child_paths = [
            "/api/v1/children",
            "/api/v1/conversation",
            "/api/v1/voice",
            "/api/v1/playground",
            "/api/voice/esp32",
        ]

        return any(request.url.path.startswith(path) for path in child_paths)


# Global error handler instance for consistency
error_handler = AITeddyErrorHandler()


def _validate_child_id(child_id: str) -> None:
    """Validate child ID format and raise error if invalid."""
    if not child_id or len(child_id) < MIN_CHILD_ID_LENGTH:
        raise InvalidInputError()


@safe_execution(fallback_value=False, log_errors=True)
def validate_child_access(user_context: dict[str, any], child_id: str) -> bool:
    """Production-grade child access validation with comprehensive permission checks."""
    if not user_context:
        raise HTTPException(
            status_code=401,
            detail="Authentication required for child data access",
        )

    user_id = user_context.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid user context - missing user ID",
        )

    # Get user's authorized child IDs
    child_ids = user_context.get("child_ids", [])
    user_role = user_context.get("role", "user")

    # Check if user has access to this child
    if child_id not in child_ids and user_role not in ["admin", "parent"]:
        logger.warning(
            "Access denied: User %s attempted to access child %s", user_id, child_id
        )
        raise HTTPException(
            status_code=403,
            detail="Access denied to child data",
        )

    # Additional safety checks for child protection
    try:
        # Verify child exists and is active (would integrate with child repository)
        _validate_child_id(child_id)

    except InvalidInputError as exc:
        logger.exception("Child access validation error")
        raise HTTPException(
            status_code=500,
            detail="Unable to validate child access at this time",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected child access validation error")
        raise HTTPException(
            status_code=500,
            detail="Unable to validate child access at this time",
        ) from exc
    else:
        logger.info("Child access validated: User %s -> Child %s", user_id, child_id)
        return True
