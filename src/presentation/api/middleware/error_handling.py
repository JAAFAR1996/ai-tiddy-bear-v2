"""Error Handling Middleware for AI Teddy Bear
Comprehensive error handling with child safety and COPPA compliance
"""

from datetime import datetime
from typing import Dict, Any, Optional, Union
import logging
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.middleware.base import RequestResponseEndpoint
import traceback

from src.infrastructure.config.settings import get_settings
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="middleware")


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive error handling middleware for child safety applications.
    """

    def __init__(self, app) -> None:
        super().__init__(app)
        self.settings = get_settings()
        self.is_production = self.settings.ENVIRONMENT == "production"

        # Child-friendly error messages
        self.child_friendly_messages = {
            400: "Oops! Something wasn't quite right with your request. Please try again!",
            401: "You need to sign in first before we can help you!",
            403: "Sorry, you don't have permission to do that right now.",
            404: "We couldn't find what you're looking for. Let's try something else!",
            429: "Whoa! You're going too fast! Please wait a moment and try again.",
            500: "Oh no! Something went wrong on our end. Don't worry, we're fixing it!"
        }

        # Security-related error codes that need special handling
        self.security_error_codes = {401, 403, 422, 429}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Handle request with comprehensive error catching and safe responses."""
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            return await self._handle_http_exception(request, e)
        except ValidationError as e:
            return await self._handle_validation_error(request, e)
        except Exception as e:
            return await self._handle_unexpected_error(request, e)

    async def _handle_http_exception(self, request: Request, exc: HTTPException) -> JSONResponse:
        """Handle FastAPI HTTP exceptions with child safety considerations."""
        error_response = self._create_error_response(
            request=request,
            status_code=exc.status_code,
            error_type="http_exception",
            message=str(exc.detail),
            is_security_error=exc.status_code in self.security_error_codes
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response
        )

    async def _handle_validation_error(self, request: Request, exc: ValidationError) -> JSONResponse:
        """Handle Pydantic validation errors with child-appropriate messages."""
        if self._is_child_related_request(request):
            message = "Some information wasn't filled in correctly. Please check and try again!"
        else:
            message = "Please check your input and try again."

        error_response = self._create_error_response(
            request=request,
            status_code=422,
            error_type="validation_error",
            message=message
        )

        return JSONResponse(
            status_code=422,
            content=error_response
        )

    async def _handle_unexpected_error(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected errors with comprehensive logging and safe responses."""
        logger.error(f"Unexpected error: {exc}", exc_info=True)

        error_response = self._create_error_response(
            request=request,
            status_code=500,
            error_type="internal_error",
            message=None,
            is_unexpected=True
        )

        return JSONResponse(
            status_code=500,
            content=error_response
        )

    def _create_error_response(
        self,
        request: Request,
        status_code: int,
        error_type: str,
        message: Optional[str] = None,
        is_security_error: bool = False,
        is_unexpected: bool = False
    ) -> Dict[str, Any]:
        """Create a safe error response appropriate for the context."""
        # Use child-friendly message if available and appropriate
        if self._is_child_related_request(request) or not message:
            safe_message = self.child_friendly_messages.get(
                status_code,
                "Something unexpected happened. Please try again later!"
            )
        else:
            safe_message = message

        # Base error response
        error_response = {
            "error": True,
            "status_code": status_code,
            "message": safe_message,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }

        # Add child safety indicators
        if self._is_child_related_request(request):
            error_response["child_safe"] = True
            error_response["coppa_compliant"] = True

        return error_response

    def _is_child_related_request(self, request: Request) -> bool:
        """Determine if this is a child-related request requiring special handling."""
        child_paths = [
            "/api/v1/children",
            "/api/v1/conversation",
            "/api/v1/voice",
            "/api/v1/playground"
        ]

        return any(request.url.path.startswith(path) for path in child_paths)
