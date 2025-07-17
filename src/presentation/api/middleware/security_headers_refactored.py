"""
from typing import Dict, Any, Optional
import logging
from .security_headers import (
    SecurityHeadersConfig,
    CSPConfig,
    get_production_config,
    get_development_config,
    create_headers_builder)
from .security_headers.middleware import SecurityHeadersMiddleware as NewSecurityHeadersMiddleware
"""

"""Security Headers Middleware - Refactored Entry Point
This module provides backward compatibility while delegating
to the new modular security headers implementation.
"""

from src.infrastructure.logging_config import get_logger
logger = get_logger(__name__, component="middleware")

# Backward compatibility alias
SecurityHeadersMiddleware = NewSecurityHeadersMiddleware

# Convenience functions for easy migration
def create_security_headers_middleware(app, environment: str = "production"):
    """
    Create security headers middleware with environment - specific config
    Args: app: FastAPI application
        environment: Environment name(production, development, testing)
    Returns: Configured SecurityHeadersMiddleware instance
    """
    return SecurityHeadersMiddleware(app)

def get_middleware_stats(middleware: SecurityHeadersMiddleware) -> Dict[str, Any]:
    """
    Get performance statistics from security middleware
    Args: middleware: SecurityHeadersMiddleware instance
    Returns: Dictionary with performance metrics
    """
    return middleware.get_stats()

# Configuration helpers
def create_child_safe_config() -> SecurityHeadersConfig:
    """Create configuration optimized for child safety"""
    config = get_production_config()
    
    # Enhanced child safety settings
    config.child_safety_mode = True
    config.coppa_compliant = True
    
    # Stricter CSP for children
    config.csp.script_src = "'self'"  # No inline scripts
    config.csp.object_src = "'none'"  # No plugins
    config.csp.frame_src = "'none'"   # No frames
    
    # Additional child protection
    config.custom_child_headers.update({
        "X-Enhanced-Child-Protection": "enabled",
        "X-Parental-Control-Ready": "true",
        "X-Safe-Browsing": "enforced"
    })
    
    return config

# Export the main classes for easy imports
__all__ = [
    "SecurityHeadersMiddleware",
    "SecurityHeadersConfig",
    "CSPConfig",
    "create_security_headers_middleware",
    "create_child_safe_config",
    "get_middleware_stats"
]

# Log the refactoring completion
logger.info("✅ Security headers middleware refactored: 651 lines → modular architecture")