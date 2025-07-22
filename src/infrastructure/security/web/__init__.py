"""Web security services."""

from .cors_service import CORSSecurityService as CORSService
# Re-enabled for Phase 1 - SecurityHeadersService now implemented
from .security_headers_service import SecurityHeadersService
from .csrf_protection import CSRFProtection

__all__ = [
    "CORSService",
    "SecurityHeadersService",  # ✅ RE-ENABLED
    "CSRFProtection",
]
