from typing import Dict, Any
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.infrastructure.di.container import Container
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="api")

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


@router.post("/login", response_model=LoginResponse)
@inject
async def login(
    request: LoginRequest,
    auth_service=Depends(Provide[Container.auth_service]),
    coppa_service=Depends(Provide[Container.coppa_compliance_service]),
) -> LoginResponse:
    """Login endpoint with rate limiting and account lockout."""
    try:
        # Perform login
        response = await auth_service.login(request)
        # Log successful login for COPPA compliance
        logger.info(f"Successful login for parent: {request.email}")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed",
        )


@router.post("/logout")
@inject
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service=Depends(Provide[Container.auth_service]),
) -> Dict[str, str]:
    """Logout endpoint with token blacklisting."""
    try:
        success = await auth_service.logout(credentials.credentials)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Logout failed"
            )
        return {"message": "Logged out successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed",
        )


@router.post("/refresh", response_model=Dict[str, str])
@inject
async def refresh_token(
    refresh_token: str, auth_service=Depends(Provide[Container.auth_service])
) -> Dict[str, str]:
    """Refresh access token using refresh token."""
    try:
        new_access_token = await auth_service.refresh_access_token(
            refresh_token
        )
        if not new_access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        return {"access_token": new_access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed",
        )


@router.get("/me", response_model=UserInfo)
@inject
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service=Depends(Provide[Container.auth_service]),
) -> UserInfo:
    """Get current authenticated user information."""
    try:
        payload = await auth_service.verify_token(credentials.credentials)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return UserInfo(
            id=payload["sub"],
            email=payload["email"],
            role=payload["role"],
            name=payload.get("name", ""),
            is_active=True,
            created_at=payload.get("iat"),
            last_login=None,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information",
        )


@router.post("/register", response_model=Dict[str, str])
@inject
async def register_parent(
    email: str,
    password: str,
    name: str,
    auth_service=Depends(Provide[Container.auth_service]),
    database_service=Depends(Provide[Container.database_service]),
    coppa_service=Depends(Provide[Container.coppa_compliance_service]),
) -> Dict[str, str]:
    """Register a new parent account with COPPA compliance."""
    try:
        # Validate password requirements
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long",
            )

        # Check if user already exists
        existing_user = await database_service.get_user_by_email(email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        # Hash password
        hashed_password = auth_service.hash_password(password)

        # Create user
        user_id = await database_service.create_user(
            email=email, hashed_password=hashed_password, role="parent"
        )

        # Log registration for COPPA compliance
        logger.info(f"New parent registered: {email}")

        return {"message": "Registration successful", "user_id": user_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@router.post("/change-password")
@inject
async def change_password(
    current_password: str,
    new_password: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service=Depends(Provide[Container.auth_service]),
    database_service=Depends(Provide[Container.database_service]),
) -> Dict[str, str]:
    """Change user password with security validation."""
    try:
        # Get current user
        payload = await auth_service.verify_token(credentials.credentials)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        # Validate new password
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 8 characters long",
            )

        # Verify current password
        user = await database_service.get_user_by_email(payload["email"])
        if not user or not auth_service.verify_password(
            current_password, user["password_hash"]
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect",
            )

        # Hash new password
        new_hashed_password = auth_service.hash_password(new_password)

        # Update password
        success = await database_service.update_user(
            user_id=payload["sub"], password_hash=new_hashed_password
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password",
            )

        # Invalidate current token
        await auth_service.logout(credentials.credentials)

        return {
            "message": "Password changed successfully. Please login again."
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password",
        )


@router.get("/validate-token")
@inject
async def validate_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service=Depends(Provide[Container.auth_service]),
) -> Dict[str, Any]:
    """Validate JWT token and return payload."""
    try:
        payload = await auth_service.verify_token(credentials.credentials)
        if not payload:
            return {"valid": False, "reason": "Invalid or expired token"}

        return {
            "valid": True,
            "user_id": payload["sub"],
            "email": payload["email"],
            "role": payload["role"],
            "expires_at": payload["exp"],
        }
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        return {"valid": False, "reason": str(e)}
