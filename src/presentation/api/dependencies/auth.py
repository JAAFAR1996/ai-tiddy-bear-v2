from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.infrastructure.di.container import container
from src.infrastructure.security.core.real_auth_service import ProductionAuthService

security = HTTPBearer()


async def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: ProductionAuthService = Depends(container.auth_service),
) -> dict[str, Any]:
    """Verify authentication for child audio access - COPPA compliance required.

    Returns:
        Dict containing authenticated user data including parent verification
    Raises:
        HTTPException: If authentication fails or user not authorized for child data

    """
    try:
        token = credentials.credentials
        payload = await auth_service.verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_role = payload.get("role", "")
        if user_role not in ["parent", "guardian", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Only parents/guardians can access child audio data",
            )
        return {
            "user_id": payload.get("sub"),
            "role": user_role,
            "permissions": payload.get("permissions", []),
            "child_ids": payload.get("child_ids", []),  # Children this user can access
        }
    except HTTPException:
        raise
    except Exception as e:
        # Generic exception handling for unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication processing error: {e}",
        )
