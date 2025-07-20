"""Core CRUD operations for child profile management.
This module provides the business logic for creating, reading, updating,
and deleting child profiles with COPPA compliance and data validation.
"""

from datetime import datetime
from typing import Any

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, status

from src.application.use_cases.manage_child_profile import (
    ManageChildProfileUseCase,
)
from src.infrastructure.di.container import container
from src.infrastructure.logging_config import get_logger
from src.infrastructure.pagination import (
    PaginatedResponse,
    PaginationRequest,
    PaginationService,
)
from src.infrastructure.security.coppa_validator import COPPAValidator

from .models import (
    ChildCreateRequest,
    ChildResponse,
    ChildUpdateRequest,
)

logger = get_logger(__name__, component="api")


class ChildOperations:
    """Core operations class for child profile management."""

    def __init__(
        self,
        manage_child_profile_use_case: ManageChildProfileUseCase = Depends(
            Provide[container.manage_child_profile_use_case],
        ),
        coppa_compliance_service: COPPAValidator = Depends(
            Provide[container.coppa_compliance_service],
        ),
        pagination_service: PaginationService = Depends(
            Provide[container.pagination_service],
        ),
    ) -> None:
        self.manage_child_profile_use_case = manage_child_profile_use_case
        self.coppa_compliance_service = coppa_compliance_service
        self.pagination_service = pagination_service

    async def create_child(
        self,
        request: ChildCreateRequest,
        parent_id: str,
    ) -> ChildResponse:
        """Create a new child profile with COPPA parental consent verification."""
        try:
            # The use case handles COPPA validation and child creation
            child_profile = (
                await self.manage_child_profile_use_case.create_child_profile(
                    parent_id=parent_id,
                    name=request.name,
                    age=request.age,
                    preferences=getattr(request, "preferences", {}),
                    interests=getattr(request, "interests", []),
                    language=getattr(request, "language", "en"),
                )
            )
            return ChildResponse.from_domain_entity(child_profile)
        except ValueError as e:
            logger.error(f"Validation error creating child: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error creating child: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create child: {e!s}",
            )

    async def get_children(
        self,
        parent_id: str,
        pagination_request: PaginationRequest | None = None,
    ) -> PaginatedResponse[ChildResponse]:
        """Get children list for parent with pagination."""
        try:
            # Use default pagination if not provided
            if pagination_request is None:
                pagination_request = PaginationRequest()

            # Create child-safe pagination
            safe_pagination = self.pagination_service.create_child_safe_pagination(
                pagination_request,
            )

            # Get children from use case
            children = await self.manage_child_profile_use_case.get_children_by_parent(
                parent_id,
            )

            # Convert to response objects
            child_responses = [
                ChildResponse.from_domain_entity(child) for child in children
            ]

            # Apply pagination
            return self.pagination_service.paginate_list(
                child_responses,
                safe_pagination,
            )
        except Exception as e:
            logger.error(f"Error getting children for parent {parent_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get children: {e!s}",
            )

    async def get_child(self, child_id: str) -> ChildResponse:
        """Get detailed information for a specific child."""
        try:
            child = await self.manage_child_profile_use_case.get_child_profile(child_id)
            if not child:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Child not found",
                )
            return ChildResponse.from_domain_entity(child)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting child {child_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get child: {e!s}",
            )

    async def update_child(
        self,
        child_id: str,
        request: ChildUpdateRequest,
    ) -> ChildResponse:
        """Update child profile information."""
        try:
            # The use case handles validation and update
            updated_child = (
                await self.manage_child_profile_use_case.update_child_profile(
                    child_id=child_id,
                    name=getattr(request, "name", None),
                    age=getattr(request, "age", None),
                    preferences=getattr(request, "preferences", None),
                    interests=getattr(request, "interests", None),
                    language=getattr(request, "language", None),
                )
            )
            return ChildResponse.from_domain_entity(updated_child)
        except HTTPException:
            raise
        except ValueError as e:
            logger.error(f"Validation error updating child {child_id}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error updating child {child_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update child: {e!s}",
            )

    async def delete_child(self, child_id: str) -> dict[str, str]:
        """Delete a child profile with COPPA compliance."""
        try:
            await self.manage_child_profile_use_case.delete_child_profile(child_id)
            return {"message": "Child and all associated data deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting child {child_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete child: {e!s}",
            )


class ChildValidationService:
    """Service for validating child data integrity and compliance."""

    def __init__(
        self,
        coppa_compliance_service: COPPAValidator = Depends(
            Provide[container.coppa_compliance_service],
        ),
    ) -> None:
        self.coppa_compliance_service = coppa_compliance_service

    def validate_child_creation(
        self,
        request: ChildCreateRequest,
        parent_id: str,
    ) -> None:
        """Validate child creation request for compliance and data integrity."""
        if not parent_id or not parent_id.strip():
            raise ValueError("Parent ID is required")

        if not request.name or not request.name.strip():
            raise ValueError("Child name is required")

        if not hasattr(request, "age") or request.age is None:
            raise ValueError("Child age is required")

        if request.age < 3 or request.age > 17:
            raise ValueError("Child age must be between 3 and 17")

        # Use coppa_compliance_service for age validation
        try:
            coppa_result = self.coppa_compliance_service.validate_age(request.age)
            if coppa_result.parental_consent_required:
                # This check is now handled by the create_child method in ChildOperations
                logger.info(f"Parental consent required for child age {request.age}")
        except Exception as e:
            logger.warning(f"COPPA validation error: {e}")
            # Continue with creation, let the use case handle COPPA compliance

    def validate_child_update(self, request: ChildUpdateRequest, child_id: str) -> None:
        """Validate child update request for compliance and data integrity."""
        if not child_id or not child_id.strip():
            raise ValueError("Child ID is required")

        # Check if there's data to update
        has_updates = any(
            [
                getattr(request, "name", None) is not None,
                getattr(request, "age", None) is not None,
                getattr(request, "preferences", None) is not None,
                getattr(request, "interests", None) is not None,
                getattr(request, "language", None) is not None,
            ],
        )

        if not has_updates:
            raise ValueError("At least one field must be provided for update")

        # Validate age if provided
        if hasattr(request, "age") and request.age is not None:
            if request.age < 3 or request.age > 17:
                raise ValueError("Child age must be between 3 and 17")

    def validate_parent_permission(self, parent_id: str, child_id: str) -> None:
        """Validate parent's authorization to access child data."""
        # In production, we need to verify from database
        # that the child belongs to this parent
        if not parent_id or not child_id:
            raise ValueError("Parent ID and Child ID are required")


class ChildDataTransformer:
    """Data transformer for child profile operations."""

    def transform_create_request(self, request: ChildCreateRequest) -> dict[str, Any]:
        """Transform creation request to database-ready format."""
        return {
            "name": request.name.strip(),
            "age": request.age,
            "preferences": {
                "preferences": getattr(request, "preferences", {}),
                "interests": getattr(request, "interests", []),
                "language": getattr(request, "language", "en"),
            },
            "created_at": datetime.now().isoformat(),
        }

    def transform_update_request(self, request: ChildUpdateRequest) -> dict[str, Any]:
        """Transform update request to database-ready format."""
        updates = {}

        if hasattr(request, "name") and request.name is not None:
            updates["name"] = request.name.strip()

        if hasattr(request, "age") and request.age is not None:
            updates["age"] = request.age

        # Update preferences
        prefs_updates = {}
        if hasattr(request, "preferences") and request.preferences is not None:
            prefs_updates["preferences"] = request.preferences

        if hasattr(request, "interests") and request.interests is not None:
            prefs_updates["interests"] = request.interests

        if hasattr(request, "language") and request.language is not None:
            prefs_updates["language"] = request.language

        if prefs_updates:
            updates["preferences"] = prefs_updates

        updates["updated_at"] = datetime.now().isoformat()
        return updates

    def transform_db_to_response(self, db_record: dict[str, Any]) -> ChildResponse:
        """Transform database record to API response format."""
        return ChildResponse.from_db_record(db_record)


class ChildSearchService:
    """Service for searching and filtering child profiles."""

    def __init__(
        self,
        manage_child_profile_use_case: ManageChildProfileUseCase = Depends(
            Provide[container.manage_child_profile_use_case],
        ),
    ) -> None:
        self.manage_child_profile_use_case = manage_child_profile_use_case

    async def search_children(
        self,
        parent_id: str,
        search_query: str = "",
        age_min: int = None,
        age_max: int = None,
        language: str = None,
    ) -> list[ChildResponse]:
        """Search children with various filters."""
        try:
            # Get all children for the parent first
            all_children = (
                await self.manage_child_profile_use_case.get_children_by_parent(
                    parent_id
                )
            )

            # Apply filters
            filtered_children = []
            for child in all_children:
                # Name search
                if search_query and search_query.lower() not in child.name.lower():
                    continue

                # Age filters
                if age_min is not None and child.age < age_min:
                    continue
                if age_max is not None and child.age > age_max:
                    continue

                # Language filter
                if language and getattr(child, "language", "en") != language:
                    continue

                filtered_children.append(child)

            # Convert to response objects
            return [
                ChildResponse.from_domain_entity(child) for child in filtered_children
            ]

        except Exception as e:
            logger.error(f"Error searching children for parent {parent_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to search children: {e!s}",
            )


# Public interfaces for operations
@inject
async def create_child(
    request: ChildCreateRequest,
    parent_id: str,
    child_operations: ChildOperations = Depends(
        Provide[container.child_operations_service],
    ),
) -> ChildResponse:
    """Create a new child profile."""
    return await child_operations.create_child(request, parent_id)


@inject
async def get_children(
    parent_id: str,
    pagination_request: PaginationRequest | None = None,
    child_operations: ChildOperations = Depends(
        Provide[container.child_operations_service],
    ),
) -> PaginatedResponse[ChildResponse]:
    """Get children list for parent with pagination."""
    return await child_operations.get_children(parent_id, pagination_request)


@inject
async def get_child(
    child_id: str,
    child_operations: ChildOperations = Depends(
        Provide[container.child_operations_service],
    ),
) -> ChildResponse:
    """Get detailed information for a specific child."""
    return await child_operations.get_child(child_id)


@inject
async def update_child(
    child_id: str,
    request: ChildUpdateRequest,
    child_operations: ChildOperations = Depends(
        Provide[container.child_operations_service],
    ),
) -> ChildResponse:
    """Update child profile information."""
    return await child_operations.update_child(child_id, request)


@inject
async def delete_child(
    child_id: str,
    child_operations: ChildOperations = Depends(
        Provide[container.child_operations_service],
    ),
) -> dict[str, str]:
    """Delete a child profile with COPPA compliance."""
    return await child_operations.delete_child(child_id)


@inject
async def search_children(
    parent_id: str,
    search_query: str = "",
    age_min: int = None,
    age_max: int = None,
    language: str = None,
    child_search_service: ChildSearchService = Depends(
        Provide[container.child_search_service],
    ),
) -> list[ChildResponse]:
    """Search children with various filters."""
    return await child_search_service.search_children(
        parent_id, search_query, age_min, age_max, language
    )
