"""Security Monitoring Middleware for Real-time Threat Detection

This middleware integrates the comprehensive security monitoring system
with FastAPI to provide real-time threat detection and incident response
for all incoming requests.

CRITICAL SECURITY FEATURES:
- Real-time request analysis for injection attacks
- COPPA-compliant child operation monitoring
- Automatic incident response and blocking
- Secure audit logging with no PII exposure
- Performance monitoring and alerting
"""

import time
from typing import Callable, Optional

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.infrastructure.logging_config import get_logger
from src.infrastructure.monitoring.security_monitoring_system import (
    AlertLevel,
    SecurityEvent,
    SecurityEventType,
    get_security_monitoring_system,
)

logger = get_logger(__name__, component="security_middleware")


class SecurityMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for real-time security monitoring and threat detection."""

    # Endpoints that require special child safety monitoring
    CHILD_SENSITIVE_ENDPOINTS = [
        "/api/v1/children",
        "/api/v1/child-profiles",
        "/api/v1/conversations",
        "/api/v1/audio/process",
        "/api/v1/stories/generate",
    ]

    # High-risk endpoints that need enhanced monitoring
    HIGH_RISK_ENDPOINTS = [
        "/api/v1/auth",
        "/api/v1/admin",
        "/api/v1/database",
        "/api/v1/vault",
    ]

    def __init__(self, app, enable_blocking: bool = True):
        super().__init__(app)
        self.enable_blocking = enable_blocking
        self.security_monitoring: Optional[object] = None
        logger.info(
            f"SecurityMonitoringMiddleware initialized (blocking={'enabled' if enable_blocking else 'disabled'})"
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Main middleware dispatch with comprehensive security monitoring."""
        start_time = time.time()

        # Initialize security monitoring if not already done
        if not self.security_monitoring:
            try:
                self.security_monitoring = await get_security_monitoring_system()
            except Exception as e:
                logger.error(f"Failed to initialize security monitoring: {e}")
                # Continue without monitoring rather than blocking requests

        # Extract request information for analysis
        request_data = await self._extract_request_data(request)

        # Perform security analysis
        security_events = []
        if self.security_monitoring:
            try:
                security_events = await self.security_monitoring.monitor_request(
                    request_data
                )
            except Exception as e:
                logger.error(f"Security monitoring failed for request: {e}")

        # Check for blocking conditions
        should_block, block_reason = self._should_block_request(security_events)

        if should_block and self.enable_blocking:
            logger.warning(
                f"Request blocked: {block_reason} from {request_data.get('source_ip')}"
            )
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Security policy violation",
                    "message": "Request blocked by security monitoring",
                    "incident_id": f"block_{int(time.time())}",
                },
            )

        # Process the request
        try:
            response = await call_next(request)

            # Monitor response for additional security checks
            await self._monitor_response(
                request_data, response, time.time() - start_time
            )

            return response

        except Exception as e:
            # Log security incident for unhandled exceptions
            if self.security_monitoring:
                error_event = SecurityEvent(
                    event_id=f"unhandled_error_{int(time.time())}",
                    event_type=SecurityEventType.SERVICE_UNAVAILABLE,
                    alert_level=AlertLevel.HIGH,
                    timestamp=request_data.get("timestamp"),
                    source_ip=request_data.get("source_ip"),
                    endpoint=request_data.get("endpoint"),
                    user_agent=request_data.get("user_agent"),
                    details={"error": str(e), "error_type": type(e).__name__},
                )
                await self.security_monitoring.process_security_event(error_event)

            raise

    async def _extract_request_data(self, request: Request) -> dict:
        """Extract request data for security analysis."""
        # Get client IP (handle proxy headers)
        source_ip = self._get_real_ip(request)

        # Get request body for content analysis
        body_content = ""
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Read body once and store for later use
                body = await request.body()
                if body:
                    body_content = body.decode("utf-8", errors="ignore")
                    # Store in request state for later access by endpoints
                    request.state.raw_body = body
            except Exception as e:
                logger.debug(f"Could not read request body: {e}")

        # Extract query parameters
        query_params = dict(request.query_params)

        # Combine all content for analysis
        combined_content = f"{body_content} {' '.join(query_params.values())}"

        return {
            "timestamp": time.time(),
            "source_ip": source_ip,
            "method": request.method,
            "endpoint": str(request.url.path),
            "full_url": str(request.url),
            "user_agent": request.headers.get("user-agent", ""),
            "content_type": request.headers.get("content-type", ""),
            "content_length": request.headers.get("content-length", 0),
            "content": combined_content,
            "query_params": query_params,
            "headers": dict(request.headers),
            "is_child_sensitive": self._is_child_sensitive_endpoint(request.url.path),
            "is_high_risk": self._is_high_risk_endpoint(request.url.path),
        }

    def _get_real_ip(self, request: Request) -> str:
        """Get the real client IP address considering proxy headers."""
        # Check common proxy headers in order of preference
        proxy_headers = [
            "CF-Connecting-IP",  # Cloudflare
            "True-Client-IP",  # Cloudflare
            "X-Real-IP",  # Nginx
            "X-Forwarded-For",  # Standard proxy header
            "X-Client-IP",  # Apache
            "X-Cluster-Client-IP",  # Cluster proxy
        ]

        for header in proxy_headers:
            ip = request.headers.get(header)
            if ip:
                # X-Forwarded-For can be a comma-separated list
                if "," in ip:
                    ip = ip.split(",")[0].strip()
                return ip

        # Fallback to direct connection
        if hasattr(request, "client") and request.client:
            return request.client.host

        return "unknown"

    def _is_child_sensitive_endpoint(self, path: str) -> bool:
        """Check if endpoint handles child-related data."""
        return any(sensitive in path for sensitive in self.CHILD_SENSITIVE_ENDPOINTS)

    def _is_high_risk_endpoint(self, path: str) -> bool:
        """Check if endpoint is considered high-risk."""
        return any(risky in path for risky in self.HIGH_RISK_ENDPOINTS)

    def _should_block_request(
        self, security_events: list
    ) -> tuple[bool, Optional[str]]:
        """Determine if request should be blocked based on security events."""
        if not security_events:
            return False, None

        # Block critical security threats immediately
        for event in security_events:
            if event.alert_level == AlertLevel.CRITICAL:
                return True, f"Critical security threat: {event.event_type.value}"

            # Block child safety violations
            if event.child_related and event.alert_level == AlertLevel.HIGH:
                return True, f"Child safety violation: {event.event_type.value}"

            # Block brute force attacks
            if event.event_type == SecurityEventType.AUTH_BRUTE_FORCE:
                return True, "Brute force attack detected"

            # Block injection attempts with high confidence
            if (
                event.event_type
                in [
                    SecurityEventType.SQL_INJECTION_ATTEMPT,
                    SecurityEventType.COMMAND_INJECTION,
                    SecurityEventType.PATH_TRAVERSAL_ATTEMPT,
                ]
                and event.details
                and event.details.get("threat_score", 0) > 80
            ):
                return (
                    True,
                    f"High-confidence injection attack: {event.event_type.value}",
                )

        return False, None

    async def _monitor_response(
        self, request_data: dict, response: Response, processing_time: float
    ) -> None:
        """Monitor response for additional security analysis."""
        if not self.security_monitoring:
            return

        try:
            # Check for suspicious response patterns
            status_code = response.status_code

            # Monitor for potential data exposure
            if status_code == 200 and request_data.get("is_child_sensitive"):
                # Additional monitoring for child-sensitive endpoints
                await self._monitor_child_sensitive_response(request_data, response)

            # Monitor for error patterns that might indicate attacks
            if status_code >= 400:
                error_event = SecurityEvent(
                    event_id=f"error_response_{int(time.time())}",
                    event_type=SecurityEventType.API_ABUSE_DETECTED
                    if status_code == 429
                    else SecurityEventType.UNAUTHORIZED_ACCESS
                    if status_code == 403
                    else SecurityEventType.SERVICE_UNAVAILABLE,
                    alert_level=AlertLevel.MEDIUM
                    if status_code < 500
                    else AlertLevel.HIGH,
                    timestamp=request_data.get("timestamp"),
                    source_ip=request_data.get("source_ip"),
                    endpoint=request_data.get("endpoint"),
                    details={
                        "status_code": status_code,
                        "processing_time_ms": processing_time * 1000,
                        "method": request_data.get("method"),
                    },
                )
                await self.security_monitoring.process_security_event(error_event)

            # Monitor performance issues
            processing_time_ms = processing_time * 1000
            if processing_time_ms > 5000:  # 5 seconds
                performance_event = SecurityEvent(
                    event_id=f"slow_response_{int(time.time())}",
                    event_type=SecurityEventType.HIGH_LATENCY,
                    alert_level=AlertLevel.MEDIUM,
                    timestamp=request_data.get("timestamp"),
                    source_ip=request_data.get("source_ip"),
                    endpoint=request_data.get("endpoint"),
                    details={
                        "processing_time_ms": processing_time_ms,
                        "status_code": status_code,
                    },
                )
                await self.security_monitoring.process_security_event(performance_event)

        except Exception as e:
            logger.error(f"Response monitoring failed: {e}")

    async def _monitor_child_sensitive_response(
        self, request_data: dict, response: Response
    ) -> None:
        """Special monitoring for child-sensitive endpoints."""
        try:
            # Extract user context if available
            user_id = request_data.get("headers", {}).get("x-user-id")
            child_id = request_data.get("query_params", {}).get("child_id")

            if user_id and child_id:
                # Monitor child operation with COPPA compliance
                operation = (
                    f"{request_data.get('method')}_{request_data.get('endpoint')}"
                )

                await self.security_monitoring.monitor_child_operation(
                    operation=operation,
                    user_id=user_id,
                    child_id=child_id,
                    details={
                        "operation_type": "api_access",
                        "endpoint": request_data.get("endpoint"),
                        "source_ip": request_data.get("source_ip"),
                        "parental_consent": request_data.get("headers", {}).get(
                            "x-parental-consent", False
                        ),
                        "status_code": response.status_code,
                    },
                )
        except Exception as e:
            logger.error(f"Child-sensitive response monitoring failed: {e}")


class SecurityHealthMiddleware(BaseHTTPMiddleware):
    """Lightweight middleware for security health monitoring."""

    def __init__(self, app):
        super().__init__(app)
        logger.info("SecurityHealthMiddleware initialized")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Perform lightweight security health checks."""

        # Add security headers to all responses
        response = await call_next(request)

        # Add essential security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers[
            "Strict-Transport-Security"
        ] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers[
            "Permissions-Policy"
        ] = "geolocation=(), microphone=(), camera=()"

        # Add custom security headers for child protection
        response.headers["X-Child-Safety-Protected"] = "true"
        response.headers["X-COPPA-Compliant"] = "true"

        return response


def setup_security_monitoring_middleware(app, enable_blocking: bool = True):
    """Setup security monitoring middleware for the application."""

    # Add comprehensive security monitoring
    app.add_middleware(SecurityMonitoringMiddleware, enable_blocking=enable_blocking)

    # Add security headers middleware
    app.add_middleware(SecurityHealthMiddleware)

    logger.info("Security monitoring middleware configured successfully")
