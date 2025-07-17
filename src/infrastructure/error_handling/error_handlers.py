"""
Error handlers for AI Teddy Bear backend
"""

from datetime import datetime
from typing import Dict, Any, Optional, Callable
import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import traceback
from src.infrastructure.error_handling.exceptions import (
    AITeddyError, ValidationError, AuthenticationError, AuthorizationError,
    ExternalServiceError, DatabaseError, SystemError, ChildSafetyError, NotFoundError, ConflictError, RateLimitError)
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="infrastructure")

class ErrorHandler:
    """Base error handler with common functionality"""
    def __init__(self) -> None:
        self.error_count = {}
        self.error_callbacks: Dict[ErrorCategory, Callable] = {}

    def register_callback(self, category: ErrorCategory, callback: Callable) -> None:
        """Register a callback for specific error category"""
        self.error_callbacks[category] = callback

    async def handle_error(
        self,
        error: Exception,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Handle an error with appropriate strategy"""
        context = context or {}
        # Log the error
        self._log_error(error, context)
        # Track error metrics
        self._track_error(error)
        # Execute category-specific callback if registered
        if isinstance(error, BaseApplicationError):
            callback = self.error_callbacks.get(error.category)
            if callback:
                try:
                    await callback(error, context)
                except Exception as e:
                    logger.error(f"Error in callback: {e}")
        # Return appropriate response
        return self._format_response(error)

    def _log_error(self, error: Exception, context: Dict[str, Any]):
        """Log error with appropriate level"""
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "timestamp": datetime.utcnow().isoformat(),
            "traceback": traceback.format_exc()
        }
        if isinstance(error, AITeddyError) and error.http_status >= 500:
            logger.error("Server Error", extra=error_info)
        elif isinstance(error, AITeddyError):
            logger.warning("Client Error", extra=error_info)
        else:
            logger.exception("Unhandled Exception", extra=error_info)

    def _track_error(self, error: Exception):
        """Track error metrics"""
        error_name = type(error).__name__
        self.error_count[error_name] = self.error_count.get(error_name, 0) + 1

    def _format_response(self, error: Exception) -> Dict[str, Any]:
        """Format error response based on error type"""
        if isinstance(error, AITeddyError):
            return {
                "error": {
                    "code": error.error_code,
                    "message": error.message,
                    "details": error.details
                },
                "status_code": error.http_status
            }
        elif isinstance(error, HTTPException):
            return {
                "error": {
                    "code": "HTTP_EXCEPTION",
                    "message": error.detail,
                },
                "status_code": error.status_code
            }
        else:
            return {
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred."
                },
                "status_code": 500
            }

async def http_exception_handler(request: Request, exc: HTTPException):
    """FastAPI handler for HTTPException"""
    logger.warning(f"HTTPException: {exc.detail}", extra={"url": str(request.url)})
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

async def aiteddy_error_handler(request: Request, exc: AITeddyError):
    """FastAPI handler for AITeddyError"""
    handler = ErrorHandler()
    response_data = await handler.handle_error(exc, {"url": str(request.url)})
    return JSONResponse(
        status_code=response_data["status_code"],
        content=response_data["error"],
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """FastAPI handler for generic exceptions"""
    handler = ErrorHandler()
    response_data = await handler.handle_error(exc, {"url": str(request.url)})
    return JSONResponse(
        status_code=response_data["status_code"],
        content=response_data["error"],
    )

def setup_error_handlers(app):
    """Add error handlers to the FastAPI app"""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(AITeddyError, aiteddy_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler)