"""from typing import Optional, Dict, Any
from uuid import uuid4
import logging
import time
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from jose import JWTError
from redis.exceptions import RedisError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback
from src.infrastructure.config.settings import get_settings.
"""

"""Centralized Error Handling Middleware for Production"""

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="middleware")
settings = get_settings()


class ErrorResponse:
    """Standardized error response format."""

    def __init__(
        self,
        error_id: str,
        message: str,
        status_code: int,
        details: Optional[Dict[str, Any]] = None,
        path: Optional[str] = None,
    ):
        self.error_id = error_id
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.path = path
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response."""
        response = {
            "error": {
                "id": self.error_id,
                "message": self.message,
                "status_code": self.status_code,
                "timestamp": self.timestamp,
            },
        }
        if self.path:
            response["error"]["path"] = self.path
        # Include details only in debug mode
        if settings.application.DEBUG and self.details:
            response["error"]["details"] = self.details
        return response


async def error_handler_middleware(request: Request, call_next) -> Response:
    """Centralized error handling middleware with comprehensive exception handling.
    Features:
    - Catches all unhandled exceptions
    - Provides consistent error response format
    - Logs errors with context
    - Masks sensitive information in production
    - Handles specific exception types appropriately.
    """
    error_id = str(uuid4())
    try:
        # Add error ID to request state for logging
        request.state.error_id = error_id
        # Process the request
        response = await call_next(request)
        return response
    except Exception as exc:
        # Log the full exception with traceback
        logger.error(
            f"Unhandled exception {error_id}: {type(exc).__name__}",
            exc_info=True,
            extra={
                "error_id": error_id,
                "path": request.url.path,
                "method": request.method,
                "client": request.client.host if request.client else None,
            },
        )
        # Handle specific exception types
        error_response = handle_exception(exc, error_id, request.url.path)
        return JSONResponse(
            status_code=error_response.status_code,
            content=error_response.to_dict(),
        )


def handle_exception(
    exc: Exception, error_id: str, path: str
) -> ErrorResponse:
    """Handle specific exception types and return appropriate error responses."""
    # Validation errors (422)
    if isinstance(exc, RequestValidationError):
        return ErrorResponse(
            error_id=error_id,
            message="Validation error: Invalid request data",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=(
                {"validation_errors": exc.errors()}
                if settings.application.DEBUG
                else None
            ),
            path=path,
        )
    # HTTP exceptions (various status codes)
    if isinstance(exc, StarletteHTTPException):
        return ErrorResponse(
            error_id=error_id,
            message=exc.detail or "HTTP error occurred",
            status_code=exc.status_code,
            path=path,
        )
    # JWT authentication errors (401)
    if isinstance(exc, JWTError):
        return ErrorResponse(
            error_id=error_id,
            message="Authentication failed: Invalid or expired token",
            status_code=status.HTTP_401_UNAUTHORIZED,
            path=path,
        )
    # Database integrity errors (409)
    if isinstance(exc, IntegrityError):
        return ErrorResponse(
            error_id=error_id,
            message="Data conflict: The requested operation violates data constraints",
            status_code=status.HTTP_409_CONFLICT,
            details={"db_error": str(exc)} if settings.DEBUG else None,
            path=path,
        )
    # Database data errors (400)
    if isinstance(exc, DataError):
        return ErrorResponse(
            error_id=error_id,
            message="Invalid data format for database operation",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"db_error": str(exc)} if settings.DEBUG else None,
            path=path,
        )
    # General database errors (503)
    if isinstance(exc, SQLAlchemyError):
        return ErrorResponse(
            error_id=error_id,
            message="Database service temporarily unavailable",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            path=path,
        )
    # Redis errors (503)
    if isinstance(exc, RedisError):
        return ErrorResponse(
            error_id=error_id,
            message="Cache service temporarily unavailable",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            path=path,
        )
    # Value errors (400)
    if isinstance(exc, ValueError):
        return ErrorResponse(
            error_id=error_id,
            message=(
                str(exc) if len(str(exc)) < 100 else "Invalid input provided"
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
            path=path,
        )
    # Permission errors (403)
    if isinstance(exc, PermissionError):
        return ErrorResponse(
            error_id=error_id,
            message="Permission denied: Insufficient privileges for this operation",
            status_code=status.HTTP_403_FORBIDDEN,
            path=path,
        )
    # Not found errors (404)
    if isinstance(exc, FileNotFoundError):
        return ErrorResponse(
            error_id=error_id,
            message="Resource not found",
            status_code=status.HTTP_404_NOT_FOUND,
            path=path,
        )
    # Timeout errors (504)
    if isinstance(exc, TimeoutError):
        return ErrorResponse(
            error_id=error_id,
            message="Request timeout: The operation took too long to complete",
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            path=path,
        )
    # Default: Internal server error (500)
    # In production, never expose internal error details
    message = (
        "An unexpected error occurred"
        if not settings.application.DEBUG
        else str(exc)
    )
    return ErrorResponse(
        error_id=error_id,
        message=message,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details=(
            {"exception": type(exc).__name__}
            if settings.application.DEBUG
            else None
        ),
        path=path,
    )


def register_exception_handlers(app) -> None:
    """Register exception handlers with the FastAPI app."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        error_id = getattr(request.state, "error_id", str(uuid4()))
        error_response = handle_exception(exc, error_id, request.url.path)
        return JSONResponse(
            status_code=error_response.status_code,
            content=error_response.to_dict(),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        error_id = getattr(request.state, "error_id", str(uuid4()))
        error_response = handle_exception(exc, error_id, request.url.path)
        return JSONResponse(
            status_code=error_response.status_code,
            content=error_response.to_dict(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        error_id = getattr(request.state, "error_id", str(uuid4()))
        # Log the exception
        logger.error(
            f"Unhandled exception {error_id}: {type(exc).__name__}",
            exc_info=True,
            extra={
                "error_id": error_id,
                "path": request.url.path,
                "method": request.method,
            },
        )
        error_response = handle_exception(exc, error_id, request.url.path)
        return JSONResponse(
            status_code=error_response.status_code,
            content=error_response.to_dict(),
        )
