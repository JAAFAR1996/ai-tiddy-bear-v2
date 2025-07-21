"""Child Creation Endpoint
Handles creating new child profiles with COPPA compliance.
"""

from typing import Any

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, status

from src.application.use_cases.manage_child_profile import ManageChildProfileUseCase
from src.domain.entities.user import User
from src.infrastructure.di.container import container
from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.child_safety.safety_monitor_service import SafetyMonitorService

from .compliance import COPPAIntegration
from .models import ChildCreateRequest, ChildResponse

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
        consent_id = await coppa_integration.validate_child_creation(request, parent_id)
        logger.info(f"COPPA consent obtained for new child profile: {consent_id}")

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
                "consent_id": consent_id,
            },
        )

        logger.info(
            f"Child profile created successfully: {child.id} for parent: {parent_id}"
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


@inject
async def validate_child_creation_request(
    request: ChildCreateRequest,
    current_user: User = Depends(container.auth_service.get_current_user),
) -> dict[str, Any]:
    """التحقق من صحة طلب إنشاء طفل قبل المعالجة."""
    try:
        # التحقق من صلاحيات المستخدم
        if current_user.role not in ["parent", "guardian"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only parents or guardians can create child profiles",
            )

        # التحقق من صحة البيانات
        validation_errors = []

        # التحقق من العمر
        if request.age < 3 or request.age > 17:
            validation_errors.append("Child age must be between 3 and 17 years")

        # التحقق من الاسم
        if not request.name or len(request.name.strip()) < 2:
            validation_errors.append("Child name must be at least 2 characters long")

        # التحقق من الاسم المكرر للوالد نفسه
        existing_children = await _get_parent_children(current_user.id)
        if any(
            child.name.lower() == request.name.lower() for child in existing_children
        ):
            validation_errors.append(
                "A child with this name already exists for this parent"
            )

        if validation_errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Validation errors found",
                    "errors": validation_errors,
                },
            )

        return {
            "valid": True,
            "parent_id": current_user.id,
            "coppa_applicable": request.age < 13,
            "message": "Child creation request is valid",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating child creation request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate child creation request",
        )


@inject
async def get_child_creation_requirements(
    child_age: int,
    coppa_integration: COPPAIntegration = Depends(
        Provide[container.coppa_integration_service],
    ),
) -> dict[str, Any]:
    """الحصول على متطلبات إنشاء طفل حسب العمر."""
    try:
        coppa_applicable = child_age < 13

        requirements = {
            "age": child_age,
            "coppa_applicable": coppa_applicable,
            "parental_consent_required": coppa_applicable,
            "data_restrictions": {
                "personal_info": coppa_applicable,
                "voice_recordings": coppa_applicable,
                "interaction_history": coppa_applicable,
                "preferences": coppa_applicable,
            },
            "required_fields": ["name", "age", "parent_id"],
            "optional_fields": ["interests", "preferences", "avatar_url", "nickname"],
        }

        if coppa_applicable:
            requirements["compliance_steps"] = [
                "Obtain verified parental consent",
                "Implement data minimization",
                "Enable easy data deletion",
                "Provide clear privacy notices",
            ]

        return requirements

    except Exception as e:
        logger.error(f"Error getting child creation requirements: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get child creation requirements",
        )


async def _get_parent_children(parent_id: str) -> list:
    """الحصول على قائمة الأطفال للوالد - دالة مساعدة."""
    try:
        # في التطبيق الحقيقي، سيتم استعلام قاعدة البيانات
        # هنا نعيد قائمة فارغة كمثال
        return []
    except Exception as e:
        logger.error(f"Error getting parent children: {e}")
        return []


@inject
async def check_child_limit(
    current_user: User = Depends(container.auth_service.get_current_user),
) -> dict[str, Any]:
    """التحقق من حد الأطفال المسموح للوالد."""
    try:
        max_children = 10  # الحد الأقصى للأطفال لكل والد

        existing_children = await _get_parent_children(current_user.id)
        current_count = len(existing_children)

        can_create_more = current_count < max_children

        return {
            "parent_id": current_user.id,
            "current_children_count": current_count,
            "max_children_allowed": max_children,
            "can_create_more": can_create_more,
            "remaining_slots": max_children - current_count if can_create_more else 0,
        }

    except Exception as e:
        logger.error(f"Error checking child limit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check child limit",
        )
