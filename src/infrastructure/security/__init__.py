"""Security infrastructure organized by concern.

Structure:
- auth/: Authentication and authorization
- audit/: Audit logging and monitoring
- child_safety/: Child protection and COPPA
- core/: Core security services
- encryption/: Encryption and hashing
- key_management/: Key rotation and management
- rate_limiter/: Rate limiting services
- validation/: Input validation and sanitization
- web/: Web security (CORS, CSRF, Headers)
"""

# Re-export commonly used items for backward compatibility
from .auth.real_auth_service import RealAuthService
from .core.main_security_service import MainSecurityService, get_security_service
from .rate_limiter.service import ComprehensiveRateLimiter as RateLimiter
from .password_hasher import PasswordHasher
from .token_service import TokenService

__all__ = [
    "MainSecurityService",
    "get_security_service",
    "RateLimiter",
    "PasswordHasher",
    "TokenService",
    "RealAuthService",
]
