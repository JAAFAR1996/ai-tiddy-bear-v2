"""
from datetime import datetime
from typing import Dict, Any, Optional, Union
import logging
from fastapi import Request, Response, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.middleware.base import RequestResponseEndpoint
import traceback
from src.infrastructure.config.settings import get_settings
from src.infrastructure.exceptions import (
"""

"""Error Handling Middleware for AI Teddy Bear
Comprehensive error handling with child safety and COPPA compliance
"""

    BaseApplicationException,
    AuthenticationError,
    ChildSafetyError,
    ValidationError as AppValidationError,
    ResourceError,
    SystemError,
    handle_exception)

from src.infrastructure.logging_config import get_logger
logger = get_logger(__name__, component="middleware")


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive error handling middleware for child safety applications.
    Features: - Safe error responses(no internal details exposed) - Child - appropriate error messages - COPPA - compliant error logging - Security incident detection - Detailed logging for debugging
    """
    def __init__(self, app) -> None:
        super().__init__(app)
        self.settings = get_settings()
        self.is_production = self.settings.application.ENVIRONMENT == "production"
        
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
        
        # Errors that should not expose details even in development
        self.sensitive_errors = {
            "authentication", "authorization", "permission", "access_denied",
            "invalid_token", "expired_token", "child_safety", "coppa_violation"
        }

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        Handle request with comprehensive error catching and safe responses.
        Args: request: Incoming HTTP request
            call_next: Next middleware / endpoint
        Returns: Response with error handling applied
        """
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            return await self._handle_http_exception(request, e)
        except ValidationError as e:
            return await self._handle_validation_error(request, e)
        except BaseApplicationException as e:
            return await self._handle_application_exception(request, e)
        except ValueError as e:
            return await self._handle_value_error(request, e)
        except KeyError as e:
            return await self._handle_key_error(request, e)
        except AttributeError as e:
            return await self._handle_attribute_error(request, e)
        except Exception as e:
            return await self._handle_unexpected_error(request, e)

    async def _handle_http_exception(self, request: Request, exc: HTTPException) -> JSONResponse:
        """
        Handle FastAPI HTTP exceptions with child safety considerations.
        Args: request: HTTP request that caused the error
            exc: HTTP exception to handle
        Returns: JSONResponse with safe error information
        """
        # Log the error
        await self._log_error(request, exc, "http_exception")
        
        # Determine if this is a security-related error
        is_security_error = exc.status_code in self.security_error_codes
        
        # Create safe error response
        error_response = self._create_error_response(
            request=request,
            status_code=exc.status_code,
            error_type="http_exception",
            message=exc.detail,
            is_security_error=is_security_error
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response,
            headers=self._get_error_headers(request, exc.status_code)
        )

    async def _handle_validation_error(self, request: Request, exc: ValidationError) -> JSONResponse:
        """
        Handle Pydantic validation errors with child - appropriate messages.
        Args: request: HTTP request that caused the error
            exc: Validation error to handle
        Returns: JSONResponse with validation error information
        """
        # Log the validation error
        await self._log_error(request, exc, "validation_error")
        
        # Create child-friendly validation messages
        if self._is_child_related_request(request):
            message = "Some information wasn't filled in correctly. Please check and try again!"
            detailed_errors = []  # Don't expose validation details for child requests
        else:
            message = "Please check your input and try again."
            detailed_errors = self._format_validation_errors(exc.errors())
            
        error_response = self._create_error_response(
            request=request,
            status_code=422,
            error_type="validation_error",
            message=message,
            details=detailed_errors if detailed_errors else None
        )
        
        return JSONResponse(
            status_code=422,
            content=error_response,
            headers=self._get_error_headers(request, 422)
        )

    async def _handle_application_exception(self, request: Request, exc: BaseApplicationException) -> JSONResponse:
        """
        Handle our custom application exceptions.
        """
        await self._log_error(request, exc, "application_exception")
        
        # Use child-friendly response if needed
        if self._is_child_related_request(request) and hasattr(exc, 'to_child_response'):
            response_data = exc.to_child_response()
        else:
            response_data = exc.to_dict()
            
        # Determine status code
        status_code = 400  # Default
        if isinstance(exc, AuthenticationError):
            status_code = 401
        elif isinstance(exc, ChildSafetyError):
            status_code = 403
        elif isinstance(exc, ResourceError):
            status_code = 404
        elif isinstance(exc, SystemError):
            status_code = 503
            
        return JSONResponse(
            status_code=status_code,
            content=response_data,
            headers=self._get_error_headers(request, status_code)
        )

    async def _handle_value_error(self, request: Request, exc: ValueError) -> JSONResponse:
        """
        Handle ValueError with proper context.
        """
        await self._log_error(request, exc, "value_error")
        
        error_response = self._create_error_response(
            request=request,
            status_code=400,
            error_type="value_error",
            message="Invalid value provided",
            details={"error": str(exc)} if not self.is_production else None
        )
        
        return JSONResponse(
            status_code=400,
            content=error_response
        )

    async def _handle_key_error(self, request: Request, exc: KeyError) -> JSONResponse:
        """
        Handle KeyError with proper context.
        """
        await self._log_error(request, exc, "key_error")
        
        error_response = self._create_error_response(
            request=request,
            status_code=400,
            error_type="missing_data",
            message="Required data is missing",
            details={"missing_key": str(exc)} if not self.is_production else None
        )
        
        return JSONResponse(
            status_code=400,
            content=error_response
        )

    async def _handle_attribute_error(self, request: Request, exc: AttributeError) -> JSONResponse:
        """
        Handle AttributeError with proper context.
        """
        await self._log_error(request, exc, "attribute_error")
        
        error_response = self._create_error_response(
            request=request,
            status_code=500,
            error_type="configuration_error",
            message="System configuration error",
            is_unexpected=True
        )
        
        return JSONResponse(
            status_code=500,
            content=error_response
        )

    async def _handle_unexpected_error(self, request: Request, exc: Exception) -> JSONResponse:
        """
        Handle unexpected errors with comprehensive logging and safe responses.
        Args: request: HTTP request that caused the error
            exc: Unexpected exception
        Returns: JSONResponse with safe error response
        """
        # Log the unexpected error with full traceback
        await self._log_error(request, exc, "unexpected_error", include_traceback=True)
        
        # Determine status code based on error type
        status_code = self._determine_status_code(exc)
        
        # Create safe error response
        error_response = self._create_error_response(
            request=request,
            status_code=status_code,
            error_type="internal_error",
            message=None,  # Will use default child-friendly message
            is_unexpected=True
        )
        
        return JSONResponse(
            status_code=status_code,
            content=error_response,
            headers=self._get_error_headers(request, status_code)
        )

    def _create_error_response(
        self,
        request: Request,
        status_code: int,
        error_type: str,
        message: Optional[str] = None,
        details: Optional[Any] = None,
        is_security_error: bool = False,
        is_unexpected: bool = False
    ) -> Dict[str, Any]:
        """
        Create a safe error response appropriate for the context.
        Args: request: HTTP request
            status_code: HTTP status code
            error_type: Type of error
            message: Error message
            details: Additional error details
            is_security_error: Whether this is a security - related error
            is_unexpected: Whether this was an unexpected error
        Returns: Dict containing safe error response
        """
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
        
        # Add request ID if available
        if hasattr(request.state, 'request_id'):
            error_response["request_id"] = request.state.request_id
            
        # Add details only in appropriate contexts
        if details and not self.is_production and not is_security_error:
            error_response["details"] = details
            
        # Add child safety indicators
        if self._is_child_related_request(request):
            error_response["child_safe"] = True
            error_response["coppa_compliant"] = True
            
        # Add security indicators for security errors
        if is_security_error:
            error_response["security_incident"] = True
            error_response["contact_support"] = True
            
        # Add helpful information
        error_response["help"] = self._get_help_information(status_code, error_type)
        
        return error_response

    def _format_validation_errors(self, errors: list) -> list:
        """
        Format Pydantic validation errors for safe display.
        Args: errors: List of validation errors
        Returns: List of formatted error messages
        """
        formatted_errors = []
        for error in errors:
            field_path = " -> ".join(str(loc) for loc in error["loc"])
            error_msg = error["msg"]
            
            # Don't expose sensitive field names
            if any(sensitive in field_path.lower() for sensitive in self.sensitive_errors):
                field_path = "[field]"
                
            formatted_errors.append({
                "field": field_path,
                "message": error_msg,
                "type": error["type"]
            })
            
        return formatted_errors

    def _determine_status_code(self, exc: Exception) -> int:
        """
        Determine appropriate HTTP status code for an exception.
        Args: exc: Exception to analyze
        Returns: HTTP status code
        """
        exc_name = type(exc).__name__.lower()
        exc_message = str(exc).lower()
        
        # Database connection errors
        if "connection" in exc_message or "database" in exc_message:
            return 503  # Service Unavailable
            
        # Permission/access errors
        if "permission" in exc_message or "access" in exc_message:
            return 403  # Forbidden
            
        # Timeout errors
        if "timeout" in exc_message:
            return 504  # Gateway Timeout
            
        # Default to internal server error
        return 500

    def _is_child_related_request(self, request: Request) -> bool:
        """
        Determine if this is a child - related request requiring special handling.
        Args: request: HTTP request to analyze
        Returns: bool: True if child - related request
        """
        child_paths = [
            "/api/v1/children",
            "/api/v1/conversation",
            "/api/v1/voice",
            "/api/v1/playground"
        ]
        
        return any(request.url.path.startswith(path) for path in child_paths)

    def _get_help_information(self, status_code: int, error_type: str) -> Dict[str, str]:
        """
        Get helpful information for the user based on the error.
        Args: status_code: HTTP status code
            error_type: Type of error
        Returns: Dict with help information
        """
        help_info = {
            "support_email": "support@aiteddybear.com",
            "documentation": "https://docs.aiteddybear.com"
        }
        
        if status_code == 400:
            help_info["suggestion"] = "Please check your input and try again."
        elif status_code == 401:
            help_info["suggestion"] = "Please sign in and try again."
        elif status_code == 403:
            help_info["suggestion"] = "Please contact support if you believe this is an error."
        elif status_code == 404:
            help_info["suggestion"] = "Please check the URL and try again."
        elif status_code == 429:
            help_info["suggestion"] = "Please wait a moment before trying again."
        elif status_code >= 500:
            help_info["suggestion"] = "This is a temporary issue. Please try again later."
            
        return help_info

    def _get_error_headers(self, request: Request, status_code: int) -> Dict[str, str]:
        """
        Get appropriate headers for error responses.
        Args: request: HTTP request
            status_code: HTTP status code
        Returns: Dict with response headers
        """
        headers = {
            "Content-Type": "application/json",
            "X-Error-Handled": "true",
            "X-Child-Safe": "true" if self._is_child_related_request(request) else "false"
        }
        
        # Add rate limiting headers for 429 errors
        if status_code == 429:
            headers["Retry-After"] = "60"
            
        # Add security headers for security errors
        if status_code in self.security_error_codes:
            headers["X-Security-Alert"] = "true"
            
        return headers

    async def _log_error(
        self,
        request: Request,
        exc: Exception,
        error_type: str,
        include_traceback: bool = False
    ) -> None:
        """
        Log error information for debugging and monitoring.
        Args: request: HTTP request that caused the error
            exc: Exception that occurred
            error_type: Type of error for categorization
            include_traceback: Whether to include full traceback
        """
        # Basic error information
        error_info = {
            "error_type": error_type,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "request_method": request.method,
            "request_path": request.url.path,
            "request_id": getattr(request.state, 'request_id', 'unknown'),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", "")[:100],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add query parameters (sanitized)
        if request.query_params:
            error_info["query_params"] = dict(request.query_params)
            
        # Add traceback for unexpected errors
        if include_traceback:
            error_info["traceback"] = traceback.format_exc()
            
        # Add child safety context
        if self._is_child_related_request(request):
            error_info["child_related"] = True
            error_info["coppa_sensitive"] = True
            
        # Log with appropriate level
        if isinstance(exc, HTTPException) and exc.status_code < 500:
            logger.warning(f"HTTP Error: {error_info}")
        else:
            logger.error(f"Server Error: {error_info}")
            
        # Log security incidents separately
        if error_type == "http_exception" and isinstance(exc, HTTPException):
            if exc.status_code in self.security_error_codes:
                logger.warning(f"Security Incident: {error_info}")

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
            
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
            
        return request.client.host if request.client else "unknown"