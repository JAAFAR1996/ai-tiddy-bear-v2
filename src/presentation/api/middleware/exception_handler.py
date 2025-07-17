"""
from typing import Dict, Any, Optional
import logging
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import traceback
from src.infrastructure.exceptions import (
"""

"""Global Exception Handler Middleware"""

    BaseApplicationException,
    handle_exception,
    ChildSafetyError,
    AuthenticationError,
    ValidationError,
    ResourceError,
    SystemError)

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="middleware")


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """
    Global exception handler middleware.
    """
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.debug_mode = False  # Never expose stack traces in production

    async def dispatch(self, request: Request, call_next):
        """
        Handle all exceptions globally with proper error responses.
        """
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            # FastAPI HTTP exceptions
            return await self._handle_http_exception(request, e)
        except BaseApplicationException as e:
            # Our custom application exceptions
            return await self._handle_application_exception(request, e)
        except ValueError as e:
            # Common validation errors
            return await self._handle_value_error(request, e)
        except KeyError as e:
            # Missing data errors
            return await self._handle_key_error(request, e)
        except Exception as e:
            # Any other unexpected exception
            return await self._handle_unexpected_exception(request, e)

    async def _handle_http_exception(self, request: Request, exc: HTTPException) -> JSONResponse:
        """Handle FastAPI HTTP exceptions"""
        # Check if this is a child endpoint
        is_child_endpoint = self._is_child_endpoint(request.url.path)
        
        if is_child_endpoint and exc.status_code >= 400:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "message": self._get_child_friendly_message(exc.status_code),
                    "child_friendly": True
                }
            )
            
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "status_code": exc.status_code
            }
        )

    async def _handle_application_exception(self, request: Request, exc: BaseApplicationException) -> JSONResponse:
        """Handle our custom application exceptions"""
        # Check if this is a child endpoint
        is_child_endpoint = self._is_child_endpoint(request.url.path)
        
        if is_child_endpoint and isinstance(exc, ChildSafetyError):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=exc.to_child_response()
            )
            
        # Determine appropriate HTTP status code
        status_code = self._get_status_code_for_exception(exc)
        
        return JSONResponse(
            status_code=status_code,
            content=exc.to_dict()
        )

    async def _handle_value_error(self, request: Request, exc: ValueError) -> JSONResponse:
        """Handle ValueError exceptions"""
        logger.warning(f"ValueError in {request.url.path}: {str(exc)}")
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "ValidationError",
                "message": "Invalid value provided",
                "detail": str(exc) if self.debug_mode else "Invalid input"
            }
        )

    async def _handle_key_error(self, request: Request, exc: KeyError) -> JSONResponse:
        """Handle KeyError exceptions"""
        logger.warning(f"KeyError in {request.url.path}: {str(exc)}")
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "MissingDataError",
                "message": "Required data missing",
                "detail": f"Missing key: {str(exc)}" if self.debug_mode else "Required field missing"
            }
        )

    async def _handle_unexpected_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle any unexpected exceptions"""
        # Log the full exception with traceback
        logger.error(
            f"Unexpected exception in {request.url.path}",
            exc_info=True,
            extra={
                "request_path": request.url.path,
                "request_method": request.method,
                "exception_type": type(exc).__name__
            }
        )
        
        # Check if this is a child endpoint
        is_child_endpoint = self._is_child_endpoint(request.url.path)
        
        if is_child_endpoint:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": "Oops! Something went wrong. Let's try again!",
                    "child_friendly": True,
                    "suggestion": "Maybe we can try something different?"
                }
            )
            
        # Never expose internal details in production
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred",
                "request_id": getattr(request.state, "request_id", "unknown")
            }
        )

    def _is_child_endpoint(self, path: str) -> bool:
        """Check if endpoint is child - facing"""
        child_paths = ["/esp32", "/ai/generate", "/audio", "/voice", "/child"]
        return any(path.startswith(p) for p in child_paths)

    def _get_child_friendly_message(self, status_code: int) -> str:
        """Get child - friendly error message for status code"""
        messages = {
            400: "Hmm, I didn't understand that. Can you try again?",
            401: "Let's make sure it's really you! Can you try logging in again?",
            403: "Oops! You need special permission for that.",
            404: "I couldn't find what you're looking for. Want to try something else?",
            429: "Wow, you're fast! Let's slow down a bit.",
            500: "Something went wrong on my end. Let's try again!"
        }
        return messages.get(status_code, "Something went wrong. Let's try again!")

    def _get_status_code_for_exception(self, exc: BaseApplicationException) -> int:
        """Map exception types to HTTP status codes"""
        if isinstance(exc, AuthenticationError):
            return status.HTTP_401_UNAUTHORIZED
        elif isinstance(exc, ValidationError):
            return status.HTTP_400_BAD_REQUEST
        elif isinstance(exc, ResourceError):
            return status.HTTP_404_NOT_FOUND
        elif isinstance(exc, ChildSafetyError):
            return status.HTTP_403_FORBIDDEN
        elif isinstance(exc, SystemError):
            return status.HTTP_503_SERVICE_UNAVAILABLE
        else:
            return status.HTTP_500_INTERNAL_SERVER_ERROR


# Exception handlers for specific exception types
async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle pydantic validation errors"""
    errors = []
    if hasattr(exc, "errors"):
        for error in exc.errors():
            errors.append({
                "field": error.get("loc", ["unknown"])[0],
                "message": error.get("msg", "Invalid value"),
                "type": error.get("type", "validation_error")
            })
            
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Input validation failed",
            "errors": errors
        }
    )


async def database_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle database - related exceptions"""
    logger.error(f"Database error in {request.url.path}: {type(exc).__name__}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": "DatabaseError",
            "message": "Database operation failed",
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )


def setup_exception_handlers(app) -> None:
    """
    Setup all exception handlers for the FastAPI app.
    """
    # Add middleware
    app.add_middleware(ExceptionHandlerMiddleware)
    
    # Add specific handlers
    from pydantic import ValidationError as PydanticValidationError
    app.add_exception_handler(PydanticValidationError, validation_exception_handler)
    
    # Database exceptions (if using SQLAlchemy)
    try:
        from sqlalchemy.exc import SQLAlchemyError
        app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    except ImportError:
        pass
        
    logger.info("Exception handlers configured successfully")