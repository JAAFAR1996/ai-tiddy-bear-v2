"""Auth endpoints router - REAL AUTHENTICATION IMPLEMENTATION."""

from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.di.fastapi_dependencies import get_database
from src.infrastructure.logging_config import get_logger
from src.infrastructure.persistence.database_manager import Database
from src.infrastructure.security.auth.real_auth_service import RealAuthService
from src.presentation.api.decorators.rate_limit import (
    auth_rate_limit,
    registration_rate_limit,
)

logger = get_logger(__name__, component="api")

router = APIRouter(prefix="/auth", tags=["auth"])


async def get_db_session(
    database: Database = Depends(get_database),
) -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency for FastAPI endpoints."""
    async for session in database.get_session():
        yield session


@router.get("/status")
async def get_auth_status():
    """Get authentication service status."""
    return {"status": "available", "service": "auth"}


@router.post("/login")
@auth_rate_limit()
async def login_endpoint(
    credentials: dict,
    db: AsyncSession = Depends(get_db_session),
    auth_service: RealAuthService = Depends(),
) -> dict:
    """Real user login endpoint with database authentication."""
    try:
        email = credentials.get("email")
        password = credentials.get("password")

        if not email or not password:
            raise HTTPException(
                status_code=400, detail="Email and password are required"
            )

        # Authenticate user
        user = await auth_service.authenticate(email, password, db)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Create JWT tokens
        user_data = {
            "id": user.id,
            "email": user.email,
            "role": user.role,
        }

        access_token = auth_service.token_service.create_access_token(user_data)
        refresh_token = auth_service.token_service.create_refresh_token(user_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Login error: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error during login"
        ) from None


@router.post("/logout")
@auth_rate_limit()
async def logout_endpoint(
    token_data: dict,
    auth_service: RealAuthService = Depends(),
) -> dict:
    """Real user logout endpoint with token blacklisting."""
    try:
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")

        if not access_token:
            raise HTTPException(status_code=400, detail="Access token is required")

        # Blacklist the tokens
        await auth_service.blacklist_token(access_token)
        if refresh_token:
            await auth_service.blacklist_token(refresh_token)

        return {"message": "Successfully logged out", "status": "success"}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Logout error: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error during logout"
        ) from None


@router.post("/register")
@registration_rate_limit()
async def register_endpoint(
    user_data: dict,
    db: AsyncSession = Depends(get_db_session),
    auth_service: RealAuthService = Depends(),
) -> dict:
    """User registration endpoint with rate limiting."""
    try:
        email = user_data.get("email")
        password = user_data.get("password")
        role = user_data.get("role", "parent")  # Default to parent role

        if not email or not password:
            raise HTTPException(
                status_code=400, detail="Email and password are required"
            )

        # Register user
        user = await auth_service.register_user(email, password, role, db)
        if not user:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

        return {
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Registration error: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error during registration"
        ) from None


@router.post("/refresh")
@auth_rate_limit()
async def refresh_token_endpoint(
    token_data: dict,
    auth_service: RealAuthService = Depends(),
) -> dict:
    """Refresh access token endpoint with rate limiting."""
    try:
        refresh_token = token_data.get("refresh_token")

        if not refresh_token:
            raise HTTPException(status_code=400, detail="Refresh token is required")

        # Verify and refresh token
        new_tokens = await auth_service.refresh_tokens(refresh_token)
        if not new_tokens:
            raise HTTPException(
                status_code=401, detail="Invalid or expired refresh token"
            )

        return {
            "access_token": new_tokens["access_token"],
            "refresh_token": new_tokens["refresh_token"],
            "token_type": "bearer",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error during token refresh"
        ) from None
