from datetime import datetime
from typing import Any
from uuid import uuid4
from src.presentation.api.models.validation_models import ConversationRequest
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field, field_validator

from src.application.services.ai.ai_orchestration_service import (
    AIOrchestrationService,
)
from src.application.services.core.conversation_service import ConversationService
from src.application.use_cases.manage_child_profile import (
    ManageChildProfileUseCase,
)
from src.infrastructure.di.container import container
from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.auth.real_auth_service import ProductionAuthService
from src.infrastructure.security.child_safety.safety_monitor_service import (
    SafetyMonitorService,
)

logger = get_logger(__name__, component="api")

router = APIRouter(prefix="/conversations", tags=["Conversations"])
security = HTTPBearer()


async def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: ProductionAuthService = Depends(container.auth_service),
) -> dict[str, Any]:
    """Verify authentication for child conversation access - COPPA compliance required.

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
                detail="Access denied: Only parents/guardians can access child conversation data",
            )

        return {
            "user_id": payload.get("sub"),
            "role": user_role,
            "permissions": payload.get("permissions", []),
            "child_ids": payload.get("child_ids", []),  # Children this user can access
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication verification failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

