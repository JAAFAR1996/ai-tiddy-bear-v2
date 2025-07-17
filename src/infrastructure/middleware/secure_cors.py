"""
CORS Middleware with Security Controls
"""

from typing import List, Union
import logging
import os
import re
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from src.infrastructure.logging_config import get_logger
logger = get_logger(__name__, component="infrastructure")

class SecureCORSMiddleware:
    """
    Features: 
    - Strict origin validation 
    - Environment - specific allowed origins 
    - Security headers integration 
    - Preflight request handling
    """
    def __init__(self, app) -> None:
        self.app = app
        self.allowed_origins = self._get_allowed_origins()
        self.allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allowed_headers = [
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRF-Token",
            "X-Request-ID",
            "Accept",
            "Origin",
            "User-Agent"
        ]
        self.expose_headers = ["X-Request-ID", "X-Rate-Limit-Remaining"]
        self.max_age = 86400  # 24 hours
        self.allow_credentials = True

    def _get_allowed_origins(self) -> List[str]:
        """Get environment - specific allowed origins for CORS."""
        environment = os.getenv('ENVIRONMENT', 'development')
        if environment == 'development':
            return [
                "http://localhost:3000",  # React dev server
                "http://localhost:8080",  # Alternative dev port
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8080"
            ]
        elif environment == 'staging':
            return [
                "https://staging.aiteddybear.com",
                "https://staging-api.aiteddybear.com"
            ]
        else:  # production
            return [
                "https://aiteddybear.com",
                "https://www.aiteddybear.com",
                "https://app.aiteddybear.com",
                "https://api.aiteddybear.com"
            ]

    async def __call__(self, scope, receive, send):
        """ASGI middleware entry point for handling CORS requests."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # Handle CORS
        if request.method == "OPTIONS":
            response = await self._handle_preflight(request)
            await response(scope, receive, send)
        else:
            await self._handle_actual_request(scope, receive, send, request)

    async def _handle_preflight(self, request: Request) -> Response:
        """Handle CORS preflight OPTIONS requests with security validation."""
        origin = request.headers.get("origin")
        if not self._is_origin_allowed(origin):
            logger.warning(f"CORS preflight rejected for origin: {origin}")
            return Response(status_code=403)
        
        # Check requested method
        requested_method = request.headers.get("access-control-request-method")
        if requested_method not in self.allowed_methods:
            logger.warning(f"CORS method not allowed: {requested_method}")
            return Response(status_code=405)
        
        # Check requested headers
        requested_headers = request.headers.get("access-control-request-headers", "")
        if requested_headers:
            headers_list = [h.strip().lower() for h in requested_headers.split(",")]
            allowed_headers_lower = [h.lower() for h in self.allowed_headers]
            for header in headers_list:
                if header not in allowed_headers_lower:
                    logger.warning(f"CORS header not allowed: {header}")
                    return Response(status_code=400)
        
        # Build preflight response
        headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": ", ".join(self.allowed_methods),
            "Access-Control-Allow-Headers": ", ".join(self.allowed_headers),
            "Access-Control-Max-Age": str(self.max_age),
        }
        
        if self.allow_credentials:
            headers["Access-Control-Allow-Credentials"] = "true"
        
        return Response(status_code=200, headers=headers)

    async def _handle_actual_request(self, scope, receive, send, request: Request):
        """Handle actual HTTP requests by adding appropriate CORS headers."""
        origin = request.headers.get("origin")
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                
                # Add CORS headers for allowed origins
                if self._is_origin_allowed(origin):
                    cors_headers = {
                        "Access-Control-Allow-Origin": origin,
                        "Access-Control-Expose-Headers": ", ".join(self.expose_headers),
                    }
                    
                    if self.allow_credentials:
                        cors_headers["Access-Control-Allow-Credentials"] = "true"
                    
                    for name, value in cors_headers.items():
                        headers[name.encode()] = value.encode()
                
                message["headers"] = list(headers.items())
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)

    def _is_origin_allowed(self, origin: str) -> bool:
        """Check if the provided origin is in the allowed origins list."""
        if not origin:
            return False
        
        # Exact match
        if origin in self.allowed_origins:
            return True
        
        # Pattern matching for subdomains (production only)
        if os.getenv('ENVIRONMENT') == 'production':
            for allowed in self.allowed_origins:
                if self._match_subdomain_pattern(origin, allowed):
                    return True
        
        logger.warning(f"Origin not allowed: {origin}")
        return False

    def _match_subdomain_pattern(self, origin: str, pattern: str) -> bool:
        """Match subdomain patterns safely"""
        # Only allow specific subdomain patterns for security
        if "aiteddybear.com" in pattern:
            # Allow subdomains of aiteddybear.com
            if origin.endswith(".aiteddybear.com") and origin.startswith("https://"):
                return True
        
        return False

def setup_cors_middleware(app) -> None:
    """Setup CORS middleware for the application"""
    # Add the secure CORS middleware
    app.add_middleware(SecureCORSMiddleware)
    
    # Also add FastAPI's built-in CORS middleware as backup
    # (it will be processed after our custom middleware)
    environment = os.getenv('ENVIRONMENT', 'development')
    if environment == 'development':
        allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
    else:
        allowed_origins = [
            "https://aiteddybear.com",
            "https://www.aiteddybear.com",
            "https://app.aiteddybear.com"
        ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRF-Token",
            "Accept"
        ],
        expose_headers=["X-Request-ID"],
        max_age=86400
    )