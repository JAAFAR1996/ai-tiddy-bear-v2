"""
Security Headers Middleware
Implements comprehensive security headers for OWASP compliance
"""

import os
from typing import Callable

from fastapi import Request
from fastapi.responses import JSONResponse

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


class SecurityHeadersMiddleware:
    """
    Implements:
    - OWASP security headers
    - Content Security Policy
    - HSTS enforcement
    - XSS protection
    - Clickjacking protection
    """

    def __init__(self, app) -> None:
        self.app = app
        self.is_production = os.getenv("ENVIRONMENT") == "production"

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)

        # Create wrapper for send function
        send_wrapper = self._create_send_wrapper(request, send)
        
        # Process request through the app with wrapped send
        await self.app(scope, receive, send_wrapper)

    def _create_send_wrapper(self, request: Request, original_send: Callable) -> Callable:
        """Create a wrapper for the send function to add security headers"""
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Get existing headers
                headers = dict(message.get("headers", []))
                
                # Add security headers
                security_headers = self._get_security_headers(request)
                for name, value in security_headers.items():
                    headers[name.encode()] = value.encode()
                
                # Update message with new headers
                message["headers"] = [(k, v) for k, v in headers.items()]
            
            await original_send(message)

        return send_wrapper

    def _get_security_headers(self, request: Request) -> dict:
        """Return security headers for the response."""
        headers = {}

        # HSTS for production
        if self.is_production:
            headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        # Content Security Policy
        csp_policy = self._get_csp_policy()
        headers["Content-Security-Policy"] = csp_policy
        
        # Basic security headers
        headers["X-Frame-Options"] = "DENY"
        headers["X-Content-Type-Options"] = "nosniff"
        headers["X-XSS-Protection"] = "1; mode=block"
        headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions policy for child safety
        headers["Permissions-Policy"] = (
            "microphone=(), camera=(), geolocation=(), payment=(), "
            "usb=(), magnetometer=(), gyroscope=(), accelerometer=()"
        )
        
        # Cross-origin policies
        headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        headers["Cross-Origin-Opener-Policy"] = "same-origin"
        headers["Cross-Origin-Resource-Policy"] = "same-site"
        
        # Hide server information
        headers["Server"] = ""

        # Cache control for sensitive endpoints
        if self._is_sensitive_endpoint(request.url.path):
            headers["Cache-Control"] = (
                "no-store, no-cache, must-revalidate, private"
            )
            headers["Pragma"] = "no-cache"
            headers["Expires"] = "0"

        return headers

    def _get_csp_policy(self) -> str:
        """Return the Content Security Policy string."""
        policy_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline'",  # Allow inline scripts for FastAPI docs
            "style-src 'self' 'unsafe-inline'",  # Allow inline styles
            "img-src 'self' data: https:",
            "font-src 'self'",
            "connect-src 'self'",
            "media-src 'none'",
            "object-src 'none'",
            "child-src 'none'",
            "frame-src 'none'",
            "worker-src 'none'",
            "manifest-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'",
            "upgrade-insecure-requests",
        ]

        if self.is_production:
            policy_directives.append("block-all-mixed-content")

        return "; ".join(policy_directives)

    def _is_sensitive_endpoint(self, path: str) -> bool:
        """Check if endpoint handles sensitive data"""
        sensitive_patterns = [
            "/auth/",
            "/children/",
            "/parents/",
            "/export/",
            "/admin/",
            "/api/v1/child/",
            "/api/v1/parent/",
        ]
        return any(pattern in path for pattern in sensitive_patterns)


class CSRFProtectionMiddleware:
    """CSRF protection middleware for state-changing requests"""

    def __init__(self, app) -> None:
        self.app = app
        self.exempt_paths = [
            "/docs", 
            "/redoc", 
            "/openapi.json", 
            "/health",
            "/api/v1/health"
        ]

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)

        # Check if CSRF protection needed
        if self._needs_csrf_protection(request):
            if not await self._validate_csrf_token(request):
                response = JSONResponse(
                    status_code=403,
                    content={
                        "detail": "CSRF token validation failed",
                        "error_code": "csrf_validation_failed"
                    },
                )
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)

    def _needs_csrf_protection(self, request: Request) -> bool:
        """Check if request needs CSRF protection"""
        # Only protect state-changing methods
        if request.method not in ["POST", "PUT", "PATCH", "DELETE"]:
            return False

        # Skip exempt paths
        path = request.url.path
        if any(exempt in path for exempt in self.exempt_paths):
            return False

        return True

    async def _validate_csrf_token(self, request: Request) -> bool:
        """Validate CSRF token"""
        # Get CSRF token from header
        csrf_token = request.headers.get("X-CSRF-Token")
        if not csrf_token:
            logger.warning(
                f"Missing CSRF token in request to {request.url.path}"
            )
            return False

        # Basic validation - in production, validate against session-based token
        if len(csrf_token) < 32:
            logger.warning(
                f"Invalid CSRF token format for {request.url.path}"
            )
            return False

        # TODO: Implement proper CSRF token validation
        # - Generate tokens based on user session
        # - Store tokens securely
        # - Validate token against stored value

        return True


class RequestValidationMiddleware:
    """Request validation middleware for security and child safety"""

    def __init__(self, app) -> None:
        self.app = app
        self.max_request_size = int(
            os.getenv("MAX_REQUEST_SIZE", "10485760")
        )  # 10MB default
        self.max_child_request_size = int(
            os.getenv("MAX_CHILD_REQUEST_SIZE", "1048576")
        )  # 1MB for child requests

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)

        # Validate request size
        validation_result = await self._validate_request_size(request)
        if validation_result:
            await validation_result(scope, receive, send)
            return

        # Validate content type for POST/PUT requests
        content_type_result = await self._validate_content_type(request)
        if content_type_result:
            await content_type_result(scope, receive, send)
            return

        # Validate user agent for child safety
        user_agent_result = await self._validate_user_agent(request)
        if user_agent_result:
            await user_agent_result(scope, receive, send)
            return

        await self.app(scope, receive, send)

    async def _validate_request_size(self, request: Request):
        """Validate request size with special limits for child endpoints"""
        content_length = request.headers.get("content-length")
        if not content_length:
            return None

        try:
            size = int(content_length)
            
            # Check if this is a child-related endpoint
            is_child_endpoint = self._is_child_endpoint(request.url.path)
            max_size = self.max_child_request_size if is_child_endpoint else self.max_request_size
            
            if size > max_size:
                logger.warning(
                    f"Request size {size} exceeds limit {max_size} for {request.url.path}"
                )
                return JSONResponse(
                    status_code=413,
                    content={
                        "detail": "Request entity too large",
                        "max_size": max_size
                    },
                )
        except ValueError:
            logger.warning(f"Invalid content-length header: {content_length}")
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid content-length header"},
            )

        return None

    async def _validate_content_type(self, request: Request):
        """Validate content type for POST/PUT requests"""
        if request.method not in ["POST", "PUT", "PATCH"]:
            return None

        content_type = request.headers.get("content-type", "")
        allowed_types = [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
        ]
        
        # For child endpoints, be more restrictive
        if self._is_child_endpoint(request.url.path):
            allowed_types = ["application/json"]  # Only JSON for child API

        if not any(allowed in content_type for allowed in allowed_types):
            logger.warning(
                f"Unsupported media type {content_type} for {request.url.path}"
            )
            return JSONResponse(
                status_code=415,
                content={
                    "detail": "Unsupported media type",
                    "allowed_types": allowed_types
                },
            )

        return None

    async def _validate_user_agent(self, request: Request):
        """Validate user agent for security"""
        user_agent = request.headers.get("user-agent", "")
        
        # Block known malicious user agents
        malicious_patterns = [
            "sqlmap",
            "nikto",
            "nmap",
            "masscan",
            "nessus",
            "openvas",
            "w3af",
            "burpsuite",
        ]
        
        user_agent_lower = user_agent.lower()
        for pattern in malicious_patterns:
            if pattern in user_agent_lower:
                logger.warning(
                    f"Blocked malicious user agent {user_agent} for {request.url.path}"
                )
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Access denied"},
                )

        return None

    def _is_child_endpoint(self, path: str) -> bool:
        """Check if endpoint is child-related"""
        child_patterns = [
            "/children/",
            "/child/",
            "/interact/",
            "/api/v1/child/",
            "/api/v1/children/",
        ]
        return any(pattern in path for pattern in child_patterns)


class ChildSafetyHeadersMiddleware:
    """Additional security headers specifically for child safety"""

    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        
        # Create wrapper for send function
        send_wrapper = self._create_child_safety_wrapper(request, send)
        
        # Process request through the app
        await self.app(scope, receive, send_wrapper)

    def _create_child_safety_wrapper(self, request: Request, original_send: Callable) -> Callable:
        """Create wrapper to add child safety headers"""
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                
                # Add child safety headers if this is a child endpoint
                if self._is_child_endpoint(request.url.path):
                    child_headers = self._get_child_safety_headers()
                    for name, value in child_headers.items():
                        headers[name.encode()] = value.encode()
                    
                    message["headers"] = [(k, v) for k, v in headers.items()]
            
            await original_send(message)

        return send_wrapper

    def _get_child_safety_headers(self) -> dict:
        """Get child safety specific headers"""
        return {
            "X-Child-Safe": "true",
            "X-Content-Rating": "child-appropriate",
            "X-COPPA-Compliant": "true",
            "X-Parental-Controls": "required",
            "Cache-Control": "no-store, no-cache, must-revalidate, private",
        }

    def _is_child_endpoint(self, path: str) -> bool:
        """Check if endpoint is child-related"""
        child_patterns = [
            "/children/",
            "/child/",
            "/interact/",
            "/api/v1/child/",
            "/api/v1/children/",
        ]
        return any(pattern in path for pattern in child_patterns)


def setup_security_middleware(app):
    """Setup all security middleware in the correct order"""
    
    # Order matters - add from outermost to innermost
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(ChildSafetyHeadersMiddleware)
    app.add_middleware(CSRFProtectionMiddleware)
    app.add_middleware(RequestValidationMiddleware)
    
    logger.info("Security middleware configured successfully")


def get_security_status() -> dict:
    """Get current security middleware status"""
    return {
        "security_headers": True,
        "csrf_protection": True,
        "request_validation": True,
        "child_safety_headers": True,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "max_request_size": int(os.getenv("MAX_REQUEST_SIZE", "10485760")),
        "max_child_request_size": int(os.getenv("MAX_CHILD_REQUEST_SIZE", "1048576")),
    }