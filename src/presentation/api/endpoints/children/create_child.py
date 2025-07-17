"""from typing import Dict, Any
import logging
from fastapi import HTTPException, Depends, status
from dependency_injector.wiring import inject, Provide
from .models import ChildCreateRequest, ChildResponse
from src.domain.entities.user import User
from src.infrastructure.di.container import container
from src.application.use_cases.manage_child_profile import ManageChildProfileUseCase
from src.presentation.api.endpoints.children.compliance import COPPAIntegration
from src.infrastructure.security.safety_monitor_service import SafetyMonitorService.
"""

"""Child Creation Endpoint
Handles creating new child profiles with COPPA compliance."""

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="api")


@inject
async def create_child_endpoint(
    request: ChildCreateRequest,
    current_user: User = Depends(container.auth_service.get_current_user),
    manage_child_profile_use_case: ManageChildProfileUseCase = Depends(
        Provide[container.manage_child_profile_use_case],
    ),
    coppa_integration: COPPAIntegration = Depends(
        Provide[container.coppa_integration_service],
    ),
    safety_monitor: SafetyMonitorService = Depends(Provide[container.safety_monitor]),
) -> ChildResponse:
    """إنشاء ملف طفل جديد مع الامتثال لـ COPPA."""
    try:
        # Verify user is a parent
        if current_user.role != "parent":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only parents can create child profiles",
            )

        parent_id = current_user.id

        # التحقق من الامتثال لـ COPPA
        await coppa_integration.validate_child_creation(request, parent_id)
        logger.info("COPPA consent obtained for new child profile")

        # إنشاء الطفل
        child = await manage_child_profile_use_case.create_child(request, parent_id)

        # تسجيل حدث الإنشاء
        await safety_monitor.record_safety_event(
            child.id,
            "child_created",
            {
                "parent_id": parent_id,
                "child_age": request.age,
                "consent_obtained": True,
            },
        )

        return child
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating child profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create child profile. Please try again.",
        )
