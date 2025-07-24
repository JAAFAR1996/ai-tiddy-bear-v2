"""Children routes with dependency injection for child profile management."""

from typing import Any
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from src.application.use_cases.manage_child_profile import ManageChildProfileUseCase
from src.domain.models.children_models_ext import (
    ChildCreateRequest,
    ChildDeleteResponse,
    ChildResponse,
    ChildUpdateRequest,
)
from src.infrastructure.di.container import Container
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="api")

router = APIRouter(prefix="/api/v1/children", tags=["Children v1 DI"])


@router.post("/", response_model=ChildResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_child(
    request: ChildCreateRequest,
    current_parent=Depends(Container.auth_service.get_current_parent),
    manage_child_use_case: ManageChildProfileUseCase = Depends(
        Provide[Container.manage_child_profile_use_case],
    ),
    coppa_service=Depends(Provide[Container.coppa_compliance_service]),
    safety_monitor=Depends(Provide[Container.safety_monitor]),
) -> ChildResponse:
    """Create a new child profile with COPPA compliance."""
    try:
        # Validate COPPA compliance
        age_validation = await coppa_service.validate_child_age(request.age)
        if not age_validation.get("compliant", True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=age_validation.get("reason", "Age validation failed"),
            )

        # Create consent record
        consent_data = {
            "parent_id": current_parent.id,
            "parent_name": getattr(current_parent, "name", "Unknown"),
            "parent_email": getattr(current_parent, "email", "unknown@example.com"),
            "child_name": request.name,
            "child_age": request.age,
            "data_collection_consent": True,
            "safety_monitoring_consent": True,
        }

        await coppa_service.create_consent_record(
            consent_data,
            ip_address=None,  # Would get from request in production
        )

        # Create child profile
        child_id = await manage_child_use_case.create_child(
            parent_id=current_parent.id,
            name=request.name,
            age=request.age,
            preferences=(
                request.preferences.dict()
                if hasattr(request, "preferences") and request.preferences
                else {}
            ),
            interests=getattr(request, "interests", []),
            language=getattr(request, "language", "en"),
        )

        # Record safety event
        await safety_monitor.record_safety_event(
            child_id=str(child_id),
            event_type="child_created",
            details=f"Child profile created for {request.name}",
            severity="info",
        )

        # Get created child for response
        child = await manage_child_use_case.get_child(child_id)

        return ChildResponse(
            id=str(child.id),
            name=child.name,
            age=child.age,
            preferences=getattr(child, "preferences", {}),
            interests=getattr(child, "interests", []),
            language=getattr(child, "language", "en"),
            safety_score=getattr(child, "safety_score", 100.0),
            parent_id=current_parent.id,
            created_at=getattr(child, "created_at", None),
            updated_at=getattr(child, "updated_at", None),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating child profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create child profile",
        )


@router.get("/", response_model=list[ChildResponse])
@inject
async def list_children(
    current_parent=Depends(Container.auth_service.get_current_parent),
    manage_child_use_case: ManageChildProfileUseCase = Depends(
        Provide[Container.manage_child_profile_use_case],
    ),
) -> list[ChildResponse]:
    """List all children for the current parent."""
    try:
        children = await manage_child_use_case.get_children_by_parent(current_parent.id)

        return [
            ChildResponse(
                id=str(child.id),
                name=child.name,
                age=child.age,
                preferences=getattr(child, "preferences", {}),
                interests=getattr(child, "interests", []),
                language=getattr(child, "language", "en"),
                safety_score=getattr(child, "safety_score", 100.0),
                parent_id=current_parent.id,
                created_at=getattr(child, "created_at", None),
                updated_at=getattr(child, "updated_at", None),
            )
            for child in children
        ]
    except Exception as e:
        logger.error(f"Error listing children: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list children",
        )


@router.get("/{child_id}", response_model=ChildResponse)
@inject
async def get_child(
    child_id: UUID,
    current_parent=Depends(Container.auth_service.get_current_parent),
    manage_child_use_case: ManageChildProfileUseCase = Depends(
        Provide[Container.manage_child_profile_use_case],
    ),
) -> ChildResponse:
    """Get a specific child profile."""
    try:
        child = await manage_child_use_case.get_child(child_id)

        # Verify parent ownership
        if getattr(child, "parent_id", None) != current_parent.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this child profile",
            )

        return ChildResponse(
            id=str(child.id),
            name=child.name,
            age=child.age,
            preferences=getattr(child, "preferences", {}),
            interests=getattr(child, "interests", []),
            language=getattr(child, "language", "en"),
            safety_score=getattr(child, "safety_score", 100.0),
            parent_id=current_parent.id,
            created_at=getattr(child, "created_at", None),
            updated_at=getattr(child, "updated_at", None),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting child {child_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not found",
        )


@router.put("/{child_id}", response_model=ChildResponse)
@inject
async def update_child(
    child_id: UUID,
    request: ChildUpdateRequest,
    current_parent=Depends(Container.auth_service.get_current_parent),
    manage_child_use_case: ManageChildProfileUseCase = Depends(
        Provide[Container.manage_child_profile_use_case],
    ),
    coppa_service=Depends(Provide[Container.coppa_compliance_service]),
    safety_monitor=Depends(Provide[Container.safety_monitor]),
) -> ChildResponse:
    """Update a child profile."""
    try:
        # Get existing child
        child = await manage_child_use_case.get_child(child_id)

        # Verify parent ownership
        if getattr(child, "parent_id", None) != current_parent.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this child profile",
            )

        # Validate age if being updated
        if hasattr(request, "age") and request.age and request.age != child.age:
            age_validation = await coppa_service.validate_child_age(request.age)
            if not age_validation.get("compliant", True):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=age_validation.get("reason", "Age validation failed"),
                )

        # Prepare update data
        update_data = {}
        if hasattr(request, "name") and request.name:
            update_data["name"] = request.name
        if hasattr(request, "age") and request.age:
            update_data["age"] = request.age
        if hasattr(request, "preferences") and request.preferences:
            update_data["preferences"] = (
                request.preferences.dict()
                if hasattr(request.preferences, "dict")
                else request.preferences
            )
        if hasattr(request, "interests") and request.interests is not None:
            update_data["interests"] = request.interests
        if hasattr(request, "language") and request.language:
            update_data["language"] = request.language

        # Update child
        await manage_child_use_case.update_child(child_id, **update_data)

        # Record safety event
        await safety_monitor.record_safety_event(
            child_id=str(child_id),
            event_type="child_updated",
            details=f"Child profile updated: {list(update_data.keys())}",
            severity="info",
        )

        # Get updated child
        updated_child = await manage_child_use_case.get_child(child_id)

        return ChildResponse(
            id=str(updated_child.id),
            name=updated_child.name,
            age=updated_child.age,
            preferences=getattr(updated_child, "preferences", {}),
            interests=getattr(updated_child, "interests", []),
            language=getattr(updated_child, "language", "en"),
            safety_score=getattr(updated_child, "safety_score", 100.0),
            parent_id=current_parent.id,
            created_at=getattr(updated_child, "created_at", None),
            updated_at=getattr(updated_child, "updated_at", None),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating child {child_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update child profile",
        )


@router.delete("/{child_id}", response_model=ChildDeleteResponse)
@inject
async def delete_child(
    child_id: UUID,
    current_parent=Depends(Container.auth_service.get_current_parent),
    manage_child_use_case: ManageChildProfileUseCase = Depends(
        Provide[Container.manage_child_profile_use_case],
    ),
    coppa_service=Depends(Provide[Container.coppa_compliance_service]),
    safety_monitor=Depends(Provide[Container.safety_monitor]),
) -> ChildDeleteResponse:
    """Delete a child profile with COPPA compliance."""
    try:
        # Get existing child
        child = await manage_child_use_case.get_child(child_id)

        # Verify parent ownership
        if getattr(child, "parent_id", None) != current_parent.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this child profile",
            )

        # Schedule COPPA-compliant data deletion
        deletion_policy = await coppa_service.schedule_data_deletion(str(child_id))

        # Delete child profile
        await manage_child_use_case.delete_child(child_id)

        # Record safety event
        await safety_monitor.record_safety_event(
            child_id=str(child_id),
            event_type="child_deleted",
            details="Child profile deleted with data retention policy",
            severity="info",
        )

        return ChildDeleteResponse(
            success=True,
            id=str(child_id),
            message="Child profile deleted successfully",
            deletion_scheduled=deletion_policy.get("scheduled_deletion_date", None),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting child {child_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete child profile",
        )


@router.get("/{child_id}/safety-summary")
@inject
async def get_child_safety_summary(
    child_id: UUID,
    current_parent=Depends(Container.auth_service.get_current_parent),
    manage_child_use_case: ManageChildProfileUseCase = Depends(
        Provide[Container.manage_child_profile_use_case],
    ),
    safety_monitor=Depends(Provide[Container.safety_monitor]),
    database_service=Depends(Provide[Container.database_service]),
) -> dict[str, Any]:
    """Get safety summary for a child."""
    try:
        # Verify parent ownership
        child = await manage_child_use_case.get_child(child_id)
        if getattr(child, "parent_id", None) != current_parent.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this child's safety data",
            )

        # Get safety events
        try:
            safety_events = await database_service.get_safety_events(
                str(child_id),
                limit=50,
            )
        except Exception as e:
            logger.warning(f"Could not fetch safety events: {e}")
            safety_events = []

        # Get usage statistics
        try:
            daily_usage = await database_service.get_daily_usage(str(child_id))
            usage_stats = await database_service.get_usage_statistics(
                str(child_id), days=7
            )
        except Exception as e:
            logger.warning(f"Could not fetch usage statistics: {e}")
            daily_usage = 0
            usage_stats = {}

        # Calculate safety metrics
        high_severity_count = sum(
            1 for event in safety_events if event.get("severity") == "high"
        )
        medium_severity_count = sum(
            1 for event in safety_events if event.get("severity") == "medium"
        )

        safety_score = 100.0
        if high_severity_count > 0:
            safety_score -= high_severity_count * 10
        if medium_severity_count > 0:
            safety_score -= medium_severity_count * 5

        safety_score = max(0.0, safety_score)

        # Filter out None values from recommendations
        recommendations = [
            "Continue monitoring child interactions",
            "Review high severity events with child",
        ]

        if high_severity_count > 2:
            recommendations.append("Consider adjusting content filters")

        return {
            "child_id": str(child_id),
            "safety_score": safety_score,
            "recent_events": safety_events[:10],
            "event_summary": {
                "total": len(safety_events),
                "high_severity": high_severity_count,
                "medium_severity": medium_severity_count,
                "low_severity": len(safety_events)
                - high_severity_count
                - medium_severity_count,
            },
            "usage_summary": {
                "daily_minutes": daily_usage,
                "weekly_stats": usage_stats,
            },
            "recommendations": recommendations,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting safety summary for child {child_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get safety summary",
        )


@router.get("/{child_id}/interactions")
@inject
async def get_child_interactions(
    child_id: UUID,
    limit: int = 50,
    current_parent=Depends(Container.auth_service.get_current_parent),
    manage_child_use_case: ManageChildProfileUseCase = Depends(
        Provide[Container.manage_child_profile_use_case],
    ),
    database_service=Depends(Provide[Container.database_service]),
) -> dict[str, Any]:
    """Get recent interactions for a child."""
    try:
        # Verify parent ownership
        child = await manage_child_use_case.get_child(child_id)
        if getattr(child, "parent_id", None) != current_parent.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this child's interaction data",
            )

        # Get interactions
        try:
            interactions = await database_service.get_child_interactions(
                str(child_id), limit=min(limit, 100)
            )  # Cap at 100
        except Exception as e:
            logger.warning(f"Could not fetch interactions: {e}")
            interactions = []

        return {
            "child_id": str(child_id),
            "interactions": interactions,
            "total_count": len(interactions),
            "limit": limit,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting interactions for child {child_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get child interactions",
        )
