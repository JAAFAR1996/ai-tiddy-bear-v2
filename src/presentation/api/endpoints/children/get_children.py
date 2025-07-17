"""
from typing import List
import logging
from fastapi import HTTPException, Depends, status
from dependency_injector.wiring import inject, Provide
from .models import ChildResponse
from src.domain.entities.user import User
from src.infrastructure.di.container import container
from src.application.use_cases.manage_child_profile import ManageChildProfileUseCase
"""

"""Get Children Endpoint
Handles retrieving children list for parents with proper access control."""

from src.infrastructure.logging_config import get_logger
logger = get_logger(__name__, component="api")

@inject
async def get_children_endpoint(
    current_user: User = Depends(container.auth_service.get_current_user),
    manage_child_profile_use_case: ManageChildProfileUseCase = Depends(Provide[container.manage_child_profile_use_case]),
) -> List[ChildResponse]:
    """الحصول على قائمة الأطفال للوالد مع التحقق من الصلاحيات"""
    try:
        # Verify user is a parent
        if current_user.role not in ["parent", "guardian"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only parents and guardians can access children profiles"
            )
        
        # Get children for this parent
        children = await manage_child_profile_use_case.get_children_by_parent(current_user.id)
        
        # Convert to response model with privacy protection
        child_responses = []
        for child in children:
            child_response = ChildResponse.from_domain(child)
            child_responses.append(child_response)
        
        logger.info(f"Retrieved {len(children)} children profiles for parent")
        return child_responses
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving children: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve children profiles. Please try again."
        )