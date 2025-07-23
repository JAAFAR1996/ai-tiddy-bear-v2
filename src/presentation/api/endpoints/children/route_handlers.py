"""Individual route handlers extracted from the monolithic setup_routes function.
Each handler is focused on a single responsibility for better maintainability.
"""

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

from src.application.use_cases.manage_child_profile import (
    ManageChildProfileUseCase,
)
from src.domain.entities.user import User
from src.infrastructure.di.container import container
from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.core.real_auth_service import ProductionAuthService
from src.infrastructure.security.child_safety.safety_monitor_service import (
    SafetyMonitorService,
)
from src.presentation.api.endpoints.children.compliance import COPPAIntegration

from .models import (
    ChildCreateRequest,
    ChildDeleteResponse,
    ChildResponse,
    ChildUpdateRequest,
)

logger = get_logger(__name__, component="api")

security = HTTPBearer()


class ChildRouteHandlers:
    """Centralized route handlers for child-related endpoints."""

    @inject
    def __init__(
        self,
        manage_child_profile_use_case: ManageChildProfileUseCase = Depends(
            Provide[container.manage_child_profile_use_case],
        ),
        coppa_integration: COPPAIntegration = Depends(
            Provide[container.coppa_integration_service],
        ),
        safety_monitor: SafetyMonitorService = Depends(
            Provide[container.safety_monitor],
        ),
        auth_service: ProductionAuthService = Depends(Provide[container.auth_service]),
    ) -> None:
        self.manage_child_profile_use_case = manage_child_profile_use_case
        self.coppa_integration = coppa_integration
        self.safety_monitor = safety_monitor
        self.auth_service = auth_service

    async def create_child_handler(
        self,
        request: ChildCreateRequest,
        current_user: User = Depends(container.auth_service.get_current_user),
    ) -> ChildResponse:
        """Create a new child profile with COPPA compliance.
        This endpoint creates a new child profile under parental supervision,
        ensuring full COPPA compliance and child safety protocols.

        Args:
            request: Child creation request containing name, age, and preferences
            current_user: Authenticated parent user (required)

        Returns:
            ChildResponse: Created child profile with safety metadata

        Raises:
            HTTPException: 403 if user is not a parent
            HTTPException: 422 if child data validation fails
            HTTPException: 400 if COPPA compliance checks fail

        Security:
            - Requires valid JWT authentication
            - Parent role verification
            - COPPA age verification (< 13 years)
            - Parental consent documentation

        """
        # Verify user is a parent
        if current_user.role != "parent":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only parents can create child profiles",
            )

        parent_id = current_user.id
        try:
            # COPPA compliance validation
            consent_id = await self.coppa_integration.validate_child_creation(
                request,
                parent_id,
            )
            logger.info(f"COPPA consent obtained: {consent_id}")

            # Create the child
            child = await self.manage_child_profile_use_case.create_child(
                request,
                parent_id,
            )

            # Record safety event
            await self.safety_monitor.record_safety_event(
                child.id,
                "child_created",
                {
                    "parent_id": parent_id,
                    "child_age": request.age,
                    "consent_id": consent_id,
                },
            )

            return child
        except Exception as e:
            logger.error(f"Error creating child: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create child: {e!s}",
            )

    @staticmethod
    async def get_children_handler(
        self,
        current_user: User = Depends(container.auth_service.get_current_user),
    ) -> list[ChildResponse]:
        """Retrieve all child profiles for authenticated parent.
        Returns a list of all children associated with the authenticated parent,
        including safety summaries and compliance status for each child.

        Args:
            current_user: Authenticated parent user (required)

        Returns:
            List[ChildResponse]: List of child profiles with safety metadata

        Raises:
            HTTPException: 403 if user is not a parent
            HTTPException: 500 if database retrieval fails

        Security:
            - Requires valid JWT authentication
            - Parent role verification
            - Logs data access for audit trail

        """
        # Verify user is a parent
        if current_user.role != "parent":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only parents can access child profiles",
            )

        try:
            parent_id = current_user.id
            children = await self.manage_child_profile_use_case.get_children_by_parent(
                parent_id,
            )

            # Log data access for each child
            for child in children:
                await self.safety_monitor.record_safety_event(
                    child.id,
                    "data_access",
                    {"parent_id": parent_id, "access_type": "list_children"},
                )

            return children
        except Exception as e:
            logger.error(f"Error getting children: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get children: {e!s}",
            )

    @staticmethod
    async def get_child_handler(
        self,
        child_id: str,
        current_user: User = Depends(container.auth_service.get_current_user),
    ) -> ChildResponse:
        """Handle retrieval of a specific child's profile."""
        # Verify user is a parent
        if current_user.role != "parent":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only parents can access child profiles",
            )

        try:
            # Verify parent-child relationship
            parent_id = current_user.id
            can_access = await self.coppa_integration.validate_data_access(
                child_id,
                parent_id,
                "profile",
            )

            if not can_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: Child not associated with this parent",
                )

            child = await self.manage_child_profile_use_case.get_child(child_id)

            # Record data access
            await self.safety_monitor.record_safety_event(
                child_id,
                "data_access",
                {"access_type": "get_child_details"},
            )

            return child
        except Exception as e:
            logger.error(f"Error getting child {child_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get child: {e!s}",
            )

    @staticmethod
    async def update_child_handler(
        self,
        child_id: str,
        request: ChildUpdateRequest,
        current_user: User = Depends(container.auth_service.get_current_user),
    ) -> ChildResponse:
        """Handle child profile updates with compliance checks."""
        # Verify user is a parent
        if current_user.role != "parent":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only parents can modify child profiles",
            )

        try:
            parent_id = current_user.id

            # Verify modification permissions
            can_modify = await self.coppa_integration.validate_data_access(
                child_id,
                parent_id,
                "preferences",
            )

            if not can_modify:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: Cannot modify this child's profile",
                )

            # Update the child
            updated_child = await self.manage_child_profile_use_case.update_child(
                child_id,
                request,
            )

            # Record modification event
            await self.safety_monitor.record_safety_event(
                child_id,
                "profile_modified",
                {
                    "parent_id": parent_id,
                    "modified_fields": list(request.dict(exclude_unset=True).keys()),
                    "modification_time": updated_child.updated_at,
                },
            )

            return updated_child
        except Exception as e:
            logger.error(f"Error updating child {child_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update child: {e!s}",
            )

    @staticmethod
    async def delete_child_handler(
        self,
        child_id: str,
        current_user: User = Depends(container.auth_service.get_current_user),
    ) -> ChildDeleteResponse:
        """Handle child profile deletion with COPPA compliance."""
        # Verify user is a parent
        if current_user.role != "parent":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only parents can delete child profiles",
            )

        try:
            parent_id = current_user.id

            # Verify deletion permissions
            can_delete = await self.coppa_integration.validate_data_access(
                child_id,
                parent_id,
                "deletion",
            )

            if not can_delete:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: Cannot delete this child's profile",
                )

            # Handle compliant deletion
            deletion_result = await self.coppa_integration.handle_child_deletion(
                child_id,
                parent_id,
            )

            return ChildDeleteResponse(
                child_id=child_id,
                deleted=True,
                deletion_timestamp=deletion_result["deletion_timestamp"],
                data_retention_notice=deletion_result["retention_notice"],
            )
        except Exception as e:
            logger.error(f"Error deleting child {child_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete child: {e!s}",
            )

    @staticmethod
    async def get_child_safety_summary_handler(
        self,
        child_id: str,
        current_user: User = Depends(container.auth_service.get_current_user),
    ):
        """Handle retrieval of child safety summary."""
        # Verify user is a parent
        if current_user.role != "parent":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only parents can access safety summaries",
            )

        try:
            parent_id = current_user.id

            # Verify access permissions
            can_access = await self.coppa_integration.validate_data_access(
                child_id,
                parent_id,
                "safety_data",
            )

            if not can_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: Cannot access this child's safety data",
                )

            safety_summary = await self.safety_monitor.get_child_safety_summary(
                child_id,
            )

            # Record safety data access
            await self.safety_monitor.record_safety_event(
                child_id,
                "safety_data_accessed",
                {"parent_id": parent_id, "access_type": "safety_summary"},
            )

            return safety_summary
        except Exception as e:
            logger.error(f"Error getting safety summary for child {child_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get safety summary: {e!s}",
            )

    @staticmethod
    async def get_child_usage_monitor_handler(
        self,
        child_id: str,
        current_user: User = Depends(container.auth_service.get_current_user),
        usage_monitor: UsageMonitor = Depends(Provide[container.usage_monitor_service]),
    ):
        """Handle retrieval of child usage monitoring data."""
        # Verify user is a parent
        if current_user.role != "parent":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only parents can access usage monitoring data",
            )

        try:
            parent_id = current_user.id

            # Verify access permissions
            can_access = await self.coppa_integration.validate_data_access(
                child_id,
                parent_id,
                "usage_data",
            )

            if not can_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: Cannot access this child's usage data",
                )

            usage_data = await usage_monitor.get_child_usage_data(child_id)

            # Record usage data access
            await self.safety_monitor.record_safety_event(
                child_id,
                "usage_data_accessed",
                {"parent_id": parent_id, "access_type": "usage_monitoring"},
            )

            return usage_data
        except Exception as e:
            logger.error(f"Error getting usage data for child {child_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get usage data: {e!s}",
            )

    @staticmethod
    async def request_consent_handler(
        self,
        child_id: str,
        current_user: User = Depends(container.auth_service.get_current_user),
        parental_consent_manager: ParentalConsentManager = Depends(
            Provide[container.parental_consent_manager_service],
        ),
    ):
        """Handle parental consent requests."""
        # Verify user is a parent
        if current_user.role != "parent":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only parents can manage consent",
            )

        try:
            parent_id = current_user.id

            # Verify parent-child relationship
            can_consent = await self.coppa_integration.validate_data_access(
                child_id,
                parent_id,
                "consent",
            )

            if not can_consent:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: Cannot manage consent for this child",
                )

            consent_result = await parental_consent_manager.request_consent(
                child_id,
                parent_id,
            )

            # Record consent request
            await self.safety_monitor.record_safety_event(
                child_id,
                "consent_requested",
                {
                    "parent_id": parent_id,
                    "consent_type": consent_result["consent_type"],
                    "request_id": consent_result["request_id"],
                },
            )

            return consent_result
        except Exception as e:
            logger.error(f"Error requesting consent for child {child_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to request consent: {e!s}",
            )
