"""
from datetime import datetime
from typing import Dict, Any, Callable, Awaitable
import json
import time
import uuid
from config.settings import get_settings
from fastapi import FastAPI # Added FastAPI import
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
"""

"""Enhanced logging middleware for child safety monitoring and system observability.
Implements 2025 structured logging standards.
"""

class ChildSafetyLoggingMiddleware(BaseHTTPMiddleware):
    """
    Enhanced logging middleware with child safety monitoring.
    Features: 
    - Structured logging for security analysis 
    - Child interaction tracking(anonymized) 
    - Performance monitoring 
    - Security event detection
    """
    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)
        self.settings = get_settings()

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # Generate correlation ID for request tracking
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        # Record start time
        start_time = time.time()
        
        # Extract relevant request information (anonymized for child safety)
        request_info = self._extract_request_info(request, correlation_id)
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Add performance headers
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Correlation-ID"] = correlation_id
            
            # Log the completed request
            self._log_request_completion(request_info, response, process_time)
            
            return response
        except Exception as e:
            # Log the error
            process_time = time.time() - start_time
            self._log_request_error(request_info, e, process_time)
            raise

    def _extract_request_info(
        self, request: Request, correlation_id: str
    ) -> Dict[str, Any]:
        """Extract request information for logging(child - safe anonymized)."""
        # Get child ID from headers (if present) for safety monitoring
        child_id = request.headers.get("X-Child-ID")
        device_id = request.headers.get("X-Device-ID")
        
        return {
            "correlation_id": correlation_id,
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "user_agent": request.headers.get("User-Agent", "Unknown"),
            "client_ip": self._get_client_ip(request),
            "child_id_hash": self._hash_child_id(child_id) if child_id else None,
            "device_id": device_id,
            "content_length": request.headers.get("Content-Length"),
            "is_child_request": "/esp32/" in request.url.path,
        }

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address with proxy support."""
        # Check for forwarded headers first (common in production)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client
        return str(request.client.host) if request.client else "unknown"

    def _hash_child_id(self, child_id: str) -> str:
        """Create anonymized hash of child ID for safety monitoring."""
        # In production, use a proper hashing function with salt
        return f"child_{hash(child_id) % 10000:04d}"

    def _log_request_completion(
        self, request_info: Dict[str, Any], response: Response, process_time: float
    ) -> None:
        """Log successful request completion."""
        log_data = {
            **request_info,
            "status_code": response.status_code,
            "process_time_seconds": round(process_time, 4),
            "response_size": response.headers.get("Content-Length"),
            "event_type": "request_completed",
        }
        
        # Add child safety flags
        if request_info["is_child_request"]:
            log_data["child_safety_event"] = True
            log_data["interaction_type"] = "child_system_interaction"
        
        # In production, use proper structured logging (e.g., JSON to stdout/file)
        if self.settings.DEBUG:
            logger.info(
                f"{request_info['method']} {request_info['path']} - {response.status_code} - {process_time:.4f}s"
            )
        else:
            logger.info(json.dumps(log_data))

    def _log_request_error(
        self, request_info: Dict[str, Any], error: Exception, process_time: float
    ) -> None:
        """Log request errors with child safety considerations."""
        log_data = {
            **request_info,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "process_time_seconds": round(process_time, 4),
            "event_type": "request_error",
        }
        
        # Add child safety flags for errors
        if request_info["is_child_request"]:
            log_data["child_safety_event"] = True
            log_data["child_safety_error"] = True
            log_data["requires_investigation"] = True
        
        # In production, use proper structured logging and alerting
        if self.settings.DEBUG:
            logger.error(
                f"{request_info['method']} {request_info['path']} - ERROR: {error} - {process_time:.4f}s"
            )
        else:
            logger.error(json.dumps(log_data))

def setup_logging_middleware(app: FastAPI) -> None:
    """Setup enhanced logging middleware for the application."""
    app.add_middleware(ChildSafetyLoggingMiddleware)