import json
import time
from datetime import datetime
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.application.services.data.audit_service import AuditService
from src.infrastructure.config.settings import get_settings
from src.infrastructure.security.web.request_security_detector import (
    RequestSecurityDetector,
)

"""Request Logging Middleware for AI Teddy Bear
Comprehensive request/response logging with child safety and COPPA compliance"""

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Comprehensive request logging middleware for child safety compliance.
    Features:
    - Detailed request/response logging
    - COPPA-compliant data handling
    - Security event detection
    - Child safety tracking.
    """

    def __init__(self, app) -> None:
        super().__init__(app)
        self.settings = get_settings()
        self.is_production = self.settings.ENVIRONMENT == "production"
        self.request_security_detector = RequestSecurityDetector()
        self.audit_service = AuditService()

        # Sensitive data patterns to redact
        self.sensitive_patterns = [
            "password",
            "token",
            "secret",
            "key",
            "api_key",
            "authorization",
            "cookie",
            "session",
            "ssn",
            "credit_card",
        ]

        # Child data fields requiring special handling
        self.child_data_fields = [
            "child_name",
            "child_id",
            "medical_notes",
            "emergency_contacts",
            "special_needs",
            "cultural_background",
            "date_of_birth",
        ]

        # Endpoints that require audit logging
        self.audit_endpoints = [
            "/api/v1/children",
            "/api/v1/conversation",
            "/api/v1/voice",
            "/api/v1/auth",
            "/api/v1/parental",
        ]

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Log request and response with child safety compliance.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/endpoint
        Returns:
            Response with logging completed

        """
        start_time = time.time()
        request_timestamp = datetime.utcnow().isoformat()

        # Extract request information
        request_info = await self._extract_request_info(request)

        # Log request (if enabled for this endpoint)
        if self._should_log_request(request):
            self._log_request(request_info, request_timestamp)

        # Process request
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Extract response information
        response_info = self._extract_response_info(response, process_time)

        # Log response
        if self._should_log_response(request, response):
            self._log_response(request_info, response_info, request_timestamp)

        # Handle audit logging for child-related operations
        if self._requires_audit_log(request):
            self.audit_service.create_audit_log(
                request_info,
                response_info,
                request_timestamp,
            )

        # Detect and log security events
        security_events = self.request_security_detector.detect_security_events(
            request_info,
            response_info,
        )

        if security_events:
            security_log = {
                "type": "security_event",
                "timestamp": datetime.utcnow().isoformat(),
                "events": security_events,
                "client_ip": request_info["client_ip"],
                "path": request_info["path"],
                "method": request_info["method"],
                "user_agent": request_info["user_agent"][:100],
                "status_code": response_info["status_code"],
            }
            logger.warning(f"Security Event: {json.dumps(security_log, default=str)}")

        return response

    async def _extract_request_info(self, request: Request) -> dict[str, Any]:
        """Extract request information with privacy protection.

        Args:
            request: HTTP request object
        Returns:
            Dict containing sanitized request information

        """
        # Basic request info
        info = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
            "headers": dict(request.headers),
            "query_params": dict(request.query_params),
        }

        # Sanitize headers
        info["headers"] = self._sanitize_data(info["headers"])

        # Extract body for certain methods
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    content_type = request.headers.get("content-type", "")
                    if "application/json" in content_type:
                        try:
                            json_body = json.loads(body)
                            info["body"] = self._sanitize_data(json_body)
                        except json.JSONDecodeError:
                            info["body"] = {"_error": "Invalid JSON"}
                    elif "application/x-www-form-urlencoded" in content_type:
                        # Form data - don't log for child safety
                        info["body"] = {"_note": "Form data not logged for privacy"}
                    elif "multipart/form-data" in content_type:
                        # File upload - don't log content
                        info["body"] = {"_note": "File upload detected"}
                    else:
                        info["body"] = {"_note": f"Content type: {content_type}"}
            except Exception as e:
                info["body"] = {"_error": f"Failed to read body: {e!s}"}

        return info

    def _extract_response_info(
        self,
        response: Response,
        process_time: float,
    ) -> dict[str, Any]:
        """Extract response information for logging.

        Args:
            response: HTTP response object
            process_time: Request processing time
        Returns:
            Dict containing response information

        """
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "process_time": round(process_time, 3),
            "content_length": response.headers.get("content-length", "unknown"),
        }

    def _sanitize_data(self, data: Any) -> Any:
        """Sanitize data to remove sensitive information.

        Args:
            data: Data to sanitize
        Returns:
            Sanitized data with sensitive fields redacted

        """
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                key_lower = key.lower()

                # Check for sensitive patterns
                if any(pattern in key_lower for pattern in self.sensitive_patterns):
                    sanitized[key] = "[REDACTED]"
                # Check for child data that requires special handling
                elif any(field in key_lower for field in self.child_data_fields):
                    if self.is_production:
                        sanitized[key] = "[CHILD_DATA_PROTECTED]"
                    else:
                        sanitized[key] = "[CHILD_DATA]"
                else:
                    sanitized[key] = self._sanitize_data(value)

            return sanitized
        if isinstance(data, list | tuple):
            return [self._sanitize_data(item) for item in data]
        if isinstance(data, str) and len(data) > 1000:
            # Truncate very long strings
            return data[:1000] + "...[TRUNCATED]"

        return data

    def _should_log_request(self, request: Request) -> bool:
        """Determine if request should be logged."""
        # Don't log health checks in production
        if request.url.path == "/health" and self.is_production:
            return False

        # Don't log static files
        if request.url.path.startswith("/static/"):
            return False

        # Log all API requests
        if request.url.path.startswith("/api/"):
            return True

        # Log root requests
        return request.url.path == "/"

    def _should_log_response(self, request: Request, response: Response) -> bool:
        """Determine if response should be logged."""
        # Always log errors
        if response.status_code >= 400:
            return True

        # Log API responses
        return bool(request.url.path.startswith("/api/"))

    def _requires_audit_log(self, request: Request) -> bool:
        """Check if request requires audit logging for COPPA compliance."""
        return any(
            request.url.path.startswith(endpoint) for endpoint in self.audit_endpoints
        )

    def _log_request(self, request_info: dict[str, Any], timestamp: str) -> None:
        """Log request information."""
        log_data = {
            "type": "request",
            "timestamp": timestamp,
            "method": request_info["method"],
            "path": request_info["path"],
            "client_ip": request_info["client_ip"],
            "user_agent": request_info["user_agent"][:200],  # Truncate user agent
        }

        # Add query params if present
        if request_info["query_params"]:
            log_data["query_params"] = request_info["query_params"]

        # Add body for certain requests
        if request_info.get("body"):
            log_data["body"] = request_info["body"]

        logger.info(f"Request: {json.dumps(log_data, default=str)}")

    def _log_response(
        self,
        request_info: dict[str, Any],
        response_info: dict[str, Any],
        timestamp: str,
    ) -> None:
        """Log response information."""
        log_data = {
            "type": "response",
            "timestamp": timestamp,
            "method": request_info["method"],
            "path": request_info["path"],
            "status_code": response_info["status_code"],
            "process_time": response_info["process_time"],
            "client_ip": request_info["client_ip"],
        }

        # Determine log level based on status code
        if response_info["status_code"] >= 500:
            logger.error(f"Response: {json.dumps(log_data, default=str)}")
        elif response_info["status_code"] >= 400:
            logger.warning(f"Response: {json.dumps(log_data, default=str)}")
        else:
            logger.info(f"Response: {json.dumps(log_data, default=str)}")

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"
