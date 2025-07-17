"""
from typing import Dict, Any
from src.infrastructure.config.settings import get_settings
"""Content Security Policy configurations for child safety.
Separated from main security headers middleware for better maintainability.
"""

class CSPPolicyBuilder:
    """Builds Content Security Policy headers for different environments."""
    
    def __init__(self) -> None:
        self.settings = get_settings()
        self.is_production = self.settings.application.ENVIRONMENT == "production"
    
    def get_production_csp(self) -> str:
        """Get strict CSP for production environment."""
        return (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "media-src 'self'; "
            "object-src 'none'; "
            "child-src 'none'; "
            "frame-src 'none'; "
            "worker-src 'none'; "
            "frame-ancestors 'none'; "
            "form-action 'self'; "
            "upgrade-insecure-requests; "
            "block-all-mixed-content"
        )
    
    def get_development_csp(self) -> str:
        """Get relaxed CSP for development environment."""
        return (
            "default-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "img-src 'self' data: blob:; "
            "connect-src 'self' ws: wss:; "
            "frame-ancestors 'none'"
        )
    
    def get_csp_policy(self) -> str:
        """Get appropriate CSP policy based on environment."""
        if self.is_production:
            return self.get_production_csp()
        else:
            return self.get_development_csp()
    
    def get_permissions_policy(self) -> str:
        """Get Permissions Policy for child safety."""
        permissions = [
            "geolocation=()",         # No location tracking
            "microphone=()",          # Controlled microphone access
            "camera=()",              # Controlled camera access
            "payment=()",             # No payment features
            "usb=()",                 # No USB access
            "magnetometer=()",        # No sensor access
            "gyroscope=()",           # No sensor access
            "accelerometer=()",       # No sensor access
            "speaker=*",              # Allow speaker for audio output
            "autoplay=*",             # Allow audio autoplay for responses
        ]
        return ", ".join(permissions)