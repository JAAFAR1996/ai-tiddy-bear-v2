"""CSRF Protection for AI Teddy Bear
Comprehensive Cross-Site Request Forgery protection with token-based validation
"""

import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass

from fastapi import HTTPException, Request, Response

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


@dataclass
class CSRFConfig:
    """Configuration for CSRF protection"""

    secret_key: str
    token_lifetime: int = 3600  # 1 hour
    cookie_name: str = "csrf_token"
    header_name: str = "X-CSRF-Token"
    safe_methods: set[str] = None
    require_https: bool = True
    same_site: str = "Strict"  # "Strict", "Lax", "None"

    def __post_init__(self):
        if self.safe_methods is None:
            self.safe_methods = {"GET", "HEAD", "OPTIONS", "TRACE"}


class CSRFTokenManager:
    """Manages CSRF token generation, validation, and storage
    Implements double-submit cookie pattern with cryptographic validation
    """

    def __init__(self, config: CSRFConfig) -> None:
        self.config = config
        self.token_cache: dict[str, dict] = {}  # In-memory cache for tokens
        if not config.secret_key or len(config.secret_key) < 32:
            raise ValueError("CSRF secret key must be at least 32 characters long")

    def generate_token(self, session_id: str, user_id: str = None) -> str:
        """Generate a cryptographically secure CSRF token
        Args: session_id: User session identifier
            user_id: Optional user identifier for additional security
        Returns: Base64-encoded CSRF token
        """
        try:
            # Create timestamp
            timestamp = str(int(time.time()))
            # Create random component
            random_bytes = secrets.token_bytes(16)
            # Combine components
            token_data = f"{session_id}:{user_id or 'anonymous'}:{timestamp}"
            # Create HMAC signature
            signature = hmac.new(
                self.config.secret_key.encode(),
                token_data.encode() + random_bytes,
                hashlib.sha256,
            ).hexdigest()
            # Combine all components
            full_token = f"{timestamp}.{secrets.token_urlsafe(16)}.{signature[:16]}"
            # Cache token for validation
            self.token_cache[full_token] = {
                "session_id": session_id,
                "user_id": user_id,
                "created_at": int(time.time()),
                "expires_at": int(time.time()) + self.config.token_lifetime,
            }
            # Clean expired tokens periodically
            self._cleanup_expired_tokens()
            logger.debug(f"Generated CSRF token for session {session_id}")
            return full_token
        except Exception as e:
            logger.error(f"Failed to generate CSRF token: {e}")
            raise

    def validate_token(self, token: str, session_id: str, user_id: str = None) -> bool:
        """Validate CSRF token against session and user
        Args: token: CSRF token to validate
            session_id: Current session identifier
            user_id: Current user identifier
        Returns: True if token is valid, False otherwise
        """
        try:
            if not token:
                logger.warning("Empty CSRF token provided")
                return False
            # Check if token exists in cache
            if token not in self.token_cache:
                logger.warning(f"CSRF token not found in cache: {token[:16]}...")
                return False
            token_data = self.token_cache[token]
            # Check expiration
            if int(time.time()) > token_data["expires_at"]:
                logger.warning(f"Expired CSRF token: {token[:16]}...")
                del self.token_cache[token]
                return False
            # Validate session match
            if token_data["session_id"] != session_id:
                logger.warning(f"CSRF token session mismatch: {token[:16]}...")
                return False
            # Validate user match (if provided)
            if user_id and token_data["user_id"] != user_id:
                logger.warning(f"CSRF token user mismatch: {token[:16]}...")
                return False
            logger.debug(f"CSRF token validated successfully: {token[:16]}...")
            return True
        except Exception as e:
            logger.error(f"CSRF token validation error: {e}")
            return False

    def invalidate_token(self, token: str) -> bool:
        """Invalidate a specific CSRF token
        Args: token: Token to invalidate
        Returns: True if token was found and invalidated
        """
        try:
            if token in self.token_cache:
                del self.token_cache[token]
                logger.debug(f"Invalidated CSRF token: {token[:16]}...")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to invalidate CSRF token: {e}")
            return False

    def invalidate_session_tokens(self, session_id: str) -> int:
        """Invalidate all tokens for a specific session
        Args: session_id: Session to invalidate tokens for Returns: Number of tokens invalidated
        """
        try:
            tokens_to_remove = [
                token
                for token, data in self.token_cache.items()
                if data["session_id"] == session_id
            ]
            for token in tokens_to_remove:
                del self.token_cache[token]
            logger.info(
                f"Invalidated {len(tokens_to_remove)} CSRF tokens for session {session_id}"
            )
            return len(tokens_to_remove)
        except Exception as e:
            logger.error(f"Failed to invalidate session tokens: {e}")
            return 0

    def _cleanup_expired_tokens(self) -> None:
        """Remove expired tokens from cache"""
        try:
            current_time = int(time.time())
            expired_tokens = [
                token
                for token, data in self.token_cache.items()
                if current_time > data["expires_at"]
            ]
            for token in expired_tokens:
                del self.token_cache[token]
            if expired_tokens:
                logger.debug(f"Cleaned up {len(expired_tokens)} expired CSRF tokens")
        except Exception as e:
            logger.error(f"Failed to cleanup expired tokens: {e}")

    def get_token_stats(self) -> dict[str, int]:
        """Get statistics about current tokens"""
        try:
            current_time = int(time.time())
            active_tokens = sum(
                1
                for data in self.token_cache.values()
                if current_time <= data["expires_at"]
            )
            expired_tokens = len(self.token_cache) - active_tokens
            return {
                "total_tokens": len(self.token_cache),
                "active_tokens": active_tokens,
                "expired_tokens": expired_tokens,
            }
        except Exception as e:
            logger.error(f"Failed to get token stats: {e}")
            return {}


class CSRFProtection:
    """Main CSRF protection class Provides middleware and utilities for CSRF protection"""

    def __init__(self, config: CSRFConfig) -> None:
        self.config = config
        self.token_manager = CSRFTokenManager(config)

    def generate_token_for_request(self, request: Request) -> str:
        """Generate CSRF token for current request"""
        session_id = self._get_session_id(request)
        user_id = self._get_user_id(request)
        return self.token_manager.generate_token(session_id, user_id)

    def validate_request(self, request: Request) -> bool:
        """Validate CSRF protection for request
        Args: request: FastAPI request object
        Returns: True if request is valid or doesn't require CSRF protection
        """
        try:
            # Skip CSRF for safe methods
            if request.method in self.config.safe_methods:
                return True
            # Get session and user information
            session_id = self._get_session_id(request)
            user_id = self._get_user_id(request)
            # Get CSRF token from header or form data
            csrf_token = self._get_csrf_token_from_request(request)
            if not csrf_token:
                logger.warning(
                    f"Missing CSRF token for {request.method} {request.url.path}"
                )
                return False
            # Validate token
            is_valid = self.token_manager.validate_token(
                csrf_token, session_id, user_id
            )
            if not is_valid:
                logger.warning(
                    f"Invalid CSRF token for {request.method} {request.url.path} "
                    f"from {request.client.host if request.client else 'unknown'}"
                )
            return is_valid
        except Exception as e:
            logger.error(f"CSRF validation error: {e}")
            return False

    def set_csrf_cookie(self, response: Response, token: str) -> None:
        """Set CSRF token as HTTP-only cookie"""
        try:
            response.set_cookie(
                key=self.config.cookie_name,
                value=token,
                max_age=self.config.token_lifetime,
                httponly=True,
                secure=self.config.require_https,
                samesite=self.config.same_site,
            )
        except Exception as e:
            logger.error(f"Failed to set CSRF cookie: {e}")

    def _get_session_id(self, request: Request) -> str:
        """Extract session ID from request"""
        # Try to get from session cookie or generate one
        session_id = request.cookies.get("session_id")
        if not session_id:
            # Generate temporary session ID based on client info
            client_info = f"{request.client.host if request.client else 'unknown'}"
            session_id = hashlib.sha256(client_info.encode()).hexdigest()[:16]
        return session_id

    def _get_user_id(self, request: Request) -> str | None:
        """Extract user ID from request(if authenticated)"""
        try:
            # Try to get from request state (set by auth middleware)
            user = getattr(request.state, "user", None)
            if user and isinstance(user, dict):
                return user.get("user_id")
            return None
        except Exception as e:
            logger.debug(f"Could not extract user ID: {e}")
            return None

    def _get_csrf_token_from_request(self, request: Request) -> str | None:
        """Extract CSRF token from request headers or form data"""
        try:
            # Try header first
            token = request.headers.get(self.config.header_name)
            if token:
                return token
            # Try cookie (for double-submit pattern)
            token = request.cookies.get(self.config.cookie_name)
            if token:
                return token
            return None
        except Exception as e:
            logger.error(f"Failed to extract CSRF token: {e}")
            return None


# Middleware for automatic CSRF protection
class CSRFMiddleware:
    """ASGI middleware for automatic CSRF protection"""

    def __init__(self, app, config: CSRFConfig) -> None:
        self.app = app
        self.csrf_protection = CSRFProtection(config)

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            # Validate CSRF for unsafe methods
            if not self.csrf_protection.validate_request(request):
                # Return 403 Forbidden
                response = Response(
                    content="CSRF token validation failed",
                    status_code=403,
                    headers={"Content-Type": "text/plain"},
                )
                await response(scope, receive, send)
                return
        # Continue with the application
        await self.app(scope, receive, send)


# Global CSRF protection instance
_csrf_protection: CSRFProtection | None = None


def get_csrf_protection() -> CSRFProtection:
    """Get global CSRF protection instance"""
    global _csrf_protection
    if _csrf_protection is None:
        # Default configuration - should be overridden in production
        config = CSRFConfig(
            secret_key=secrets.token_urlsafe(32),
            require_https=False,  # Set to True in production
        )
        _csrf_protection = CSRFProtection(config)
        logger.warning(
            "Using default CSRF configuration - configure properly for production"
        )
    return _csrf_protection


def init_csrf_protection(secret_key: str, **kwargs) -> CSRFProtection:
    """Initialize CSRF protection with custom configuration"""
    global _csrf_protection
    config = CSRFConfig(secret_key=secret_key, **kwargs)
    _csrf_protection = CSRFProtection(config)
    logger.info("CSRF protection initialized with custom configuration")
    return _csrf_protection


# Decorator for protecting individual endpoints
def csrf_protect(func):
    """Decorator to add CSRF protection to individual endpoints"""

    async def wrapper(*args, **kwargs):
        # Find request object in arguments
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        if not request:
            raise HTTPException(
                status_code=500,
                detail="CSRF protection requires Request object",
            )
        # Validate CSRF
        csrf = get_csrf_protection()
        if not csrf.validate_request(request):
            raise HTTPException(status_code=403, detail="CSRF token validation failed")
        return await func(*args, **kwargs)

    return wrapper
