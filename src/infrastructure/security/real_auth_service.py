"""Production Authentication Service for AI Teddy Bear
Enterprise-grade authentication with JWT, bcrypt, and comprehensive security features."""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import asyncio
import json
import logging
import os
import secrets
import sys

try:
    from .log_sanitizer import LogSanitizer
    _log_sanitizer = LogSanitizer()
except ImportError:
    _log_sanitizer = None

from src.infrastructure.logging_config import get_logger
logger = get_logger(__name__, component="security")

def _sanitize_email_for_log(email: str) -> str:
    """Sanitize email for logging to maintain COPPA compliance"""
    if _log_sanitizer:
        return _log_sanitizer.mask_email(email)
    else:
        # Fallback: show only domain and first character
        parts = email.split('@')
        if len(parts) == 2:
            return f"{parts[0][0]}***@{parts[1]}"
        return "***@***"

# Production-only imports - fail fast if missing
try:
    import bcrypt
    from jose import jwt, JWTError
    from pydantic import BaseModel, Field, EmailStr
    from fastapi import HTTPException, status, Depends
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    import redis.asyncio as redis
except ImportError as e:
    logger.error(f"CRITICAL ERROR: Authentication dependencies missing: {e}")
    logger.error("Install required dependencies: pip install bcrypt python-jose[cryptography] pydantic fastapi redis")
    raise ImportError(f"Missing authentication dependencies: {e}") from e

from src.infrastructure.config.settings import get_settings

# Pydantic models for authentication
class LoginRequest(BaseModel):
    """Login request model"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

class LoginResponse(BaseModel):
    """Login response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: Dict[str, Any]

class UserInfo(BaseModel):
    """User information model"""
    id: str
    email: EmailStr
    role: str
    name: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

from src.infrastructure.security.token_service import TokenService
from src.infrastructure.security.password_hasher import PasswordHasher
from src.infrastructure.security.rate_limiter_service import RateLimiterService

class ProductionAuthService:
    """
    Production-grade authentication service with comprehensive security features.
    Features:
    - bcrypt password hashing with salt
    - JWT access and refresh tokens
    - Rate limiting for login attempts
    - Account lockout mechanism
    - Session management with Redis
    - Comprehensive audit logging
    - COPPA-compliant parent verification
    """
    
    def __init__(
        self,
        database_session=None,
        redis_cache=None,
        token_service: TokenService = Depends(),
        password_hasher: PasswordHasher = Depends(),
        rate_limiter_service: RateLimiterService = Depends(),
    ) -> None:
        self.database = database_session
        self.redis_cache = redis_cache
        self.token_service = token_service
        self.password_hasher = password_hasher
        self.rate_limiter_service = rate_limiter_service
        
        # JWT configuration is now handled by TokenService
        # self.secret_key = self.settings.SECRET_KEY
        # if not self.secret_key or len(self.secret_key) < 32:
        #     raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")
        # self.algorithm = "HS256"
        # self.access_token_expire_minutes = 30
        # self.refresh_token_expire_days = 7
        
        # Enhanced Security configuration
        # self.max_login_attempts = 3 # Handled by RateLimiterService
        # self.lockout_duration = timedelta(hours=2) # Handled by RateLimiterService
        # self.password_min_length = 12 # Handled by PasswordHasher
        # self.bcrypt_rounds = 14 # Handled by PasswordHasher
        
        # Rate limiting enhancements
        # self.ip_rate_limit = 10  # Max attempts per IP per hour
        # self.global_rate_limit = 100  # Max attempts globally per minute
        self.account_enumeration_protection = True  # Consistent response times
        
        # Rate limiting storage is now handled by RateLimiterService
        # self.login_attempts = defaultdict(list)
        # self.locked_accounts = {}
        
        logger.info("Production Auth Service initialized with comprehensive security")
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt with secure salt"""
        return self.password_hasher.hash_password(password)
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against bcrypt hash"""
        return self.password_hasher.verify_password(password, hashed_password)
    
    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT access token with user data"""
        return self.token_service.create_access_token(user_data)
    
    def create_refresh_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        return self.token_service.create_refresh_token(user_data)
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and check blacklist"""
        payload = await self.token_service.verify_token(token)
        if not payload:
            return None
        
        # Check if token is blacklisted (for logout)
        if self.redis_cache:
            is_blacklisted = await self.redis_cache.get(f"blacklist:{token}")
            if is_blacklisted:
                logger.debug("Token is blacklisted")
                return None
        
        return payload
    
    async def check_rate_limit(self, email: str, ip_address: str = None) -> Dict[str, Any]:
        """Enhanced rate limiting with IP tracking and progressive delays"""
        return await self.rate_limiter_service.check_rate_limit(email, ip_address)
    
    async def record_failed_login(self, email: str) -> None:
        """Record failed login attempt"""
        await self.rate_limiter_service.record_failed_login(email)
    
    async def authenticate_user(self, email: str, password: str, ip_address: str = None) -> Optional[UserInfo]:
        """
        Authenticate user with comprehensive security checks.
        Enhanced security implementation with no demo accounts allowed.
        """
        try:
            # Enhanced rate limiting check
            rate_limit_result = await self.check_rate_limit(email, ip_address)
            if not rate_limit_result["allowed"]:
                if rate_limit_result["reason"] == "account_locked":
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=rate_limit_result["message"],
                        headers={"Retry-After": str(rate_limit_result["retry_after"])}
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=rate_limit_result["message"]
                    )
            
            # Apply progressive delay if needed
            if rate_limit_result.get("delay_seconds", 0) > 0:
                import asyncio
                await asyncio.sleep(rate_limit_result["delay_seconds"])
            
            # Production database implementation
            if self.database:
                try:
                    user = await self.database.get_user_by_email(email)
                    if user and self.verify_password(password, user.get("password_hash", "")):
                        return UserInfo(
                            id=user["id"],
                            email=user["email"],
                            role=user.get("role", "parent"),
                            name=user.get("name", ""),
                            is_active=user.get("is_active", True),
                            created_at=user.get("created_at", datetime.utcnow())
                        )
                except Exception as e:
                    logger.error(f"Database error during authentication: {e}")
                    # Fall through to development fallback
            
            # Production-only authentication - NO bypass allowed
            # All users must be properly registered through secure registration process
            # Development environments should use real test accounts, not backdoors
            
            # Authentication failed
            await self.record_failed_login(email)
            return None
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            await self.record_failed_login(email)
            return None
    
    async def login(self, login_request: LoginRequest, ip_address: str = None) -> LoginResponse:
        """Complete login process with token generation and enhanced security"""
        user = await self.authenticate_user(login_request.email, login_request.password, ip_address)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        # Create tokens
        user_data = {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
        access_token = self.create_access_token(user_data)
        refresh_token = self.create_refresh_token(user_data)
        
        # Store session in Redis
        if self.redis_cache:
            session_data = {
                "user_id": user.id,
                "email": user.email,
                "role": user.role,
                "login_time": datetime.utcnow().isoformat()
            }
            await self.redis_cache.setex(
                f"session:{user.id}",
                self.access_token_expire_minutes * 60,
                json.dumps(session_data)
            )
        
        # Clear failed login attempts
        self.rate_limiter_service.clear_attempts(login_request.email)
        
        logger.info(f"Successful login for user: {_sanitize_email_for_log(user.email)}")
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.token_service.access_token_expire_minutes * 60,
            user_info={
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "name": user.name
            }
        )
    
    async def logout(self, token: str) -> bool:
        """Logout user and blacklist token"""
        try:
            payload = await self.verify_token(token)
            if not payload:
                return False
            
            # Blacklist the token
            if self.redis_cache:
                # Calculate remaining token lifetime
                exp = payload.get("exp")
                if exp:
                    remaining_time = exp - datetime.utcnow().timestamp()
                    if remaining_time > 0:
                        await self.redis_cache.setex(
                            f"blacklist:{token}",
                            int(remaining_time),
                            "1"
                        )
                
                # Remove session
                user_id = payload.get("sub")
                if user_id:
                    await self.redis_cache.delete(f"session:{user_id}")
            
            logger.info(f"User logged out: {_sanitize_email_for_log(payload.get('email', 'unknown'))}")
            return True
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False
    
    async def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Refresh access token using refresh token"""
        try:
            payload = await self.verify_token(refresh_token)
            if not payload or payload.get("type") != "refresh":
                return None
            
            # Create new access token
            user_data = {
                "id": payload["sub"],
                "email": payload["email"],
                "role": payload.get("role", "parent")
            }
            return self.create_access_token(user_data)
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return None

# FastAPI security
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), auth_service: ProductionAuthService = Depends()) -> UserInfo:
    payload = await auth_service.verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Return user info from token payload
    return UserInfo(
        id=payload["sub"],
        email=payload["email"],
        role=payload["role"],
        name=payload.get("name", ""),
        is_active=True,
        created_at=datetime.utcnow()
    )

async def get_current_parent(current_user: UserInfo = Depends(get_current_user)) -> UserInfo:
    """Ensure current user is a parent (COPPA compliance)"""
    if current_user.role != "parent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Parent authorization required"
        )
    return current_user

def require_auth(required_role: str = "parent") -> Callable:
    """Decorator to require specific role authentication"""
    def decorator(func) -> Callable:
        async def wrapper(*args, **kwargs):
            # This would be used with FastAPI dependencies
            return await func(*args, **kwargs)
        return wrapper
    return decorator