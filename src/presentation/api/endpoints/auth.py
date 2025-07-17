"""from datetime import datetime
from typing import Dict, Any
import logging
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from src.infrastructure.persistence.database import Database
from src.infrastructure.security.real_auth_service import ProductionAuthService, UserInfo
from src.infrastructure.security.rate_limiter_service import RateLimiterService
from src.infrastructure.di.container import container
from src.presentation.api.decorators.rate_limit import strict_limit, moderate_limit.
"""

"""API endpoints for authentication and authorization"""

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="api")

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security scheme
security = HTTPBearer()

# Global service instances - REMOVED
# settings = get_settings()
# auth_service = create_auth_service()
# database = Database(settings.DATABASE_URL)


async def get_client_ip(request: Request) -> str:
    """Extract client IP for rate limiting."""
    # Check common proxy headers
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    # Direct IP
    return request.client.host if request.client else "unknown"


# Request/Response Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    role: str = "parent"


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    role: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/login", response_model=AuthResponse)
@strict_limit()
async def login(
    request: LoginRequest,
    client_ip: str = Depends(get_client_ip),
    auth_service: ProductionAuthService = Depends(container.auth_service),
    rate_limiter_service: RateLimiterService = Depends(
        container.rate_limiter_service
    ),
):
    """User login with rate limiting protection
    Authenticate user credentials and return JWT tokens with comprehensive security measures.
    """
    # Rate limiting (5 attempts per minute)
    rate_limit_result = await rate_limiter_service.check_rate_limit(
        request.email,
        client_ip,
    )
    if not rate_limit_result["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=rate_limit_result["message"],
            headers={
                "Retry-After": (
                    str(rate_limit_result["retry_after"])
                    if rate_limit_result.get("retry_after")
                    else ""
                ),
            },
        )

    user = await auth_service.authenticate_user(
        request.email, request.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = auth_service.create_access_token(
        {"id": user.id, "email": user.email, "role": user.role},
    )
    refresh_token = auth_service.create_refresh_token(
        {"id": user.id, "email": user.email},
    )

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        email=user.email,
        role=user.role,
    )


@router.post("/register", response_model=AuthResponse)
@strict_limit()
async def register(
    request: RegisterRequest,
    client_ip: str = Depends(get_client_ip),
    auth_service: ProductionAuthService = Depends(container.auth_service),
    rate_limiter_service: RateLimiterService = Depends(
        container.rate_limiter_service
    ),
):
    """Register a new user."""
    # Rate limiting for registration (stricter than login)
    rate_limit_result = await rate_limiter_service.check_rate_limit(
        client_ip,
        client_ip,
    )  # Using client_ip as email for simplicity here
    if not rate_limit_result["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=rate_limit_result["message"],
            headers={
                "Retry-After": (
                    str(rate_limit_result["retry_after"])
                    if rate_limit_result.get("retry_after")
                    else ""
                ),
            },
        )

    # Verify password match
    if request.password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )

    # For production, implement proper user creation with database
    # This is a simplified example
    try:
        # Create user
        auth_service.hash_password(request.password)

        # Create user in database (simplified for demo)
        user_id = f"user_{datetime.now().timestamp()}"

        # Create tokens
        access_token = auth_service.create_access_token(
            {"id": user_id, "email": request.email, "role": request.role},
        )
        refresh_token = auth_service.create_refresh_token(
            {"id": user_id, "email": request.email},
        )

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user_id,
            email=request.email,
            role=request.role,
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@router.post("/refresh", response_model=AuthResponse)
@moderate_limit()
async def refresh_token(
    request: RefreshTokenRequest,
    client_ip: str = Depends(get_client_ip),
    auth_service: ProductionAuthService = Depends(container.auth_service),
    rate_limiter_service: RateLimiterService = Depends(
        container.rate_limiter_service
    ),
):
    """Refresh access token."""
    # Rate limiting for token refresh (10 attempts per hour per IP)
    rate_limit_result = await rate_limiter_service.check_rate_limit(
        client_ip,
        client_ip,
    )  # Using client_ip as email for simplicity here
    if not rate_limit_result["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=rate_limit_result["message"],
            headers={
                "Retry-After": (
                    str(rate_limit_result["retry_after"])
                    if rate_limit_result.get("retry_after")
                    else ""
                ),
            },
        )

    # Verify refresh token validity
    payload = await auth_service.verify_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # For production, implement proper user lookup with database
    # This is a simplified example
    try:
        user_id = payload["sub"]
        user_email = payload["email"]
        user_role = payload.get("role", "parent")

        # Create new tokens
        access_token = auth_service.create_access_token(
            {"id": user_id, "email": user_email, "role": user_role},
        )
        new_refresh_token = auth_service.create_refresh_token(
            {"id": user_id, "email": user_email},
        )

        return AuthResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            user_id=user_id,
            email=user_email,
            role=user_role,
        )
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed",
        )
