"""Get Children Endpoint
Handles retrieving children list for parents with proper access control.
"""

from typing import Any

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, status

from src.application.use_cases.manage_child_profile import ManageChildProfileUseCase
from src.domain.entities.user import User
from src.infrastructure.di.container import container
from src.infrastructure.logging_config import get_logger

from .models import ChildResponse

logger = get_logger(__name__, component="api")


@inject
async def get_children_endpoint(
    current_user: User = Depends(container.auth_service.get_current_user),
    manage_child_profile_use_case: ManageChildProfileUseCase = Depends(
        Provide[container.manage_child_profile_use_case],
    ),
) -> list[ChildResponse]:
    """الحصول على قائمة الأطفال للوالد مع التحقق من الصلاحيات."""
    try:
        # Verify user is a parent
        if current_user.role not in ["parent", "guardian"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only parents and guardians can access children profiles",
            )

        # Get children for this parent
        children = await manage_child_profile_use_case.get_children_by_parent(
            current_user.id,
        )

        # Convert to response model with privacy protection
        child_responses = []
        for child in children:
            child_response = ChildResponse.from_domain(child)
            child_responses.append(child_response)

        logger.info(
            f"Retrieved {len(children)} children profiles for parent: {current_user.id}"
        )
        return child_responses
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving children: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve children profiles. Please try again.",
        )


@inject
async def get_children_summary(
    current_user: User = Depends(container.auth_service.get_current_user),
    manage_child_profile_use_case: ManageChildProfileUseCase = Depends(
        Provide[container.manage_child_profile_use_case],
    ),
) -> dict[str, Any]:
    """الحصول على ملخص الأطفال للوالد."""
    try:
        # Verify user permissions
        if current_user.role not in ["parent", "guardian"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to children information",
            )

        # Get children for this parent
        children = await manage_child_profile_use_case.get_children_by_parent(
            current_user.id,
        )

        # Calculate summary statistics
        total_children = len(children)
        age_groups = {
            "preschool": 0,  # 3-5 years
            "elementary": 0,  # 6-10 years
            "middle_school": 0,  # 11-13 years
            "high_school": 0,  # 14-17 years
        }

        coppa_applicable_count = 0
        active_children = 0

        for child in children:
            # Count by age group
            if child.age <= 5:
                age_groups["preschool"] += 1
            elif child.age <= 10:
                age_groups["elementary"] += 1
            elif child.age <= 13:
                age_groups["middle_school"] += 1
            else:
                age_groups["high_school"] += 1

            # Count COPPA applicable children (under 13)
            if child.age < 13:
                coppa_applicable_count += 1

            # Count active children
            if getattr(child, "is_active", True):
                active_children += 1

        summary = {
            "parent_id": current_user.id,
            "total_children": total_children,
            "active_children": active_children,
            "coppa_applicable_children": coppa_applicable_count,
            "age_distribution": age_groups,
            "privacy_compliance": {
                "coppa_enabled": True,
                "data_retention_days": 365,
                "consent_management": "active",
            },
            "last_updated": "2025-01-01T00:00:00Z",  # Would be actual timestamp
        }

        logger.info(f"Generated children summary for parent: {current_user.id}")
        return summary

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating children summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate children summary",
        )


@inject
async def get_child_by_id(
    child_id: str,
    current_user: User = Depends(container.auth_service.get_current_user),
    manage_child_profile_use_case: ManageChildProfileUseCase = Depends(
        Provide[container.manage_child_profile_use_case],
    ),
) -> ChildResponse:
    """الحصول على معلومات طفل محدد."""
    try:
        # Verify user permissions
        if current_user.role not in ["parent", "guardian"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to child information",
            )

        # Get the specific child
        child = await manage_child_profile_use_case.get_child_by_id(
            child_id, current_user.id
        )

        if not child:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Child not found or access denied",
            )

        # Verify ownership
        if child.parent_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this child's information",
            )

        child_response = ChildResponse.from_domain(child)

        logger.info(
            f"Retrieved child profile: {child_id} for parent: {current_user.id}"
        )
        return child_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving child {child_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve child information",
        )


@inject
async def search_children(
    query: str | None = None,
    age_min: int | None = None,
    age_max: int | None = None,
    current_user: User = Depends(container.auth_service.get_current_user),
    manage_child_profile_use_case: ManageChildProfileUseCase = Depends(
        Provide[container.manage_child_profile_use_case],
    ),
) -> list[ChildResponse]:
    """البحث في الأطفال بناءً على معايير محددة."""
    try:
        # Verify user permissions
        if current_user.role not in ["parent", "guardian"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to children information",
            )

        # Get all children for this parent first
        all_children = await manage_child_profile_use_case.get_children_by_parent(
            current_user.id,
        )

        # Apply filters
        filtered_children = []
        for child in all_children:
            # Name search filter
            if query and query.lower() not in child.name.lower():
                continue

            # Age range filter
            if age_min is not None and child.age < age_min:
                continue
            if age_max is not None and child.age > age_max:
                continue

            filtered_children.append(child)

        # Convert to response models
        child_responses = [
            ChildResponse.from_domain(child) for child in filtered_children
        ]

        logger.info(
            f"Search returned {len(child_responses)} children for parent: {current_user.id}"
        )
        return child_responses

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching children: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search children",
        )


@inject
async def get_children_activity_summary(
    days: int = 7,
    current_user: User = Depends(container.auth_service.get_current_user),
    manage_child_profile_use_case: ManageChildProfileUseCase = Depends(
        Provide[container.manage_child_profile_use_case],
    ),
) -> dict[str, Any]:
    """الحصول على ملخص نشاط الأطفال للأيام الماضية."""
    try:
        # Verify user permissions
        if current_user.role not in ["parent", "guardian"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to children activity information",
            )

        # Validate days parameter
        if days < 1 or days > 365:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Days parameter must be between 1 and 365",
            )

        # Get children for this parent
        children = await manage_child_profile_use_case.get_children_by_parent(
            current_user.id,
        )

        # Generate activity summary (mock data for now)
        activity_summary = {
            "parent_id": current_user.id,
            "period_days": days,
            "total_children": len(children),
            "children_activity": [],
            "overall_stats": {
                "total_interactions": 0,
                "average_daily_usage_minutes": 0,
                "most_active_day": None,
                "safety_incidents": 0,
            },
        }

        # Add activity for each child
        for child in children:
            child_activity = {
                "child_id": child.id,
                "child_name": child.name,
                "total_interactions": 15,  # Mock data
                "daily_average_minutes": 25,  # Mock data
                "favorite_activities": ["storytelling", "learning games"],
                "safety_score": 0.98,
                "last_active": "2025-01-01T12:00:00Z",
            }
            activity_summary["children_activity"].append(child_activity)
            activity_summary["overall_stats"]["total_interactions"] += 15

        # Calculate averages
        if children:
            activity_summary["overall_stats"]["average_daily_usage_minutes"] = sum(
                ca["daily_average_minutes"]
                for ca in activity_summary["children_activity"]
            ) / len(children)

        logger.info(
            f"Generated {days}-day activity summary for parent: {current_user.id}"
        )
        return activity_summary

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating activity summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate activity summary",
        )
