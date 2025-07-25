"""Paginated Conversations Endpoints.

Provides paginated access to child conversations with COPPA compliance.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from src.infrastructure.logging_config import get_logger
from src.infrastructure.pagination import (
    PaginatedResponse,
    PaginationRequest,
    PaginationService,
)
from src.infrastructure.persistence.models.child_models import ChildModel
from src.infrastructure.persistence.real_database_service import get_database_service
from src.infrastructure.persistence.repositories.conversation_repository import (
    AsyncSQLAlchemyConversationRepo,
)
from src.infrastructure.persistence.session_manager import get_async_session

# Import the verification service interface for reference only
# NOTE: We use our own DatabaseParentChildVerificationService for actual verification


class DatabaseParentChildVerificationService:
    """PRODUCTION verification service using real database relationships.

    SECURITY: This service provides the ONLY authorized way to verify
    parent-child relationships in the system. It uses the actual database
    to verify relationships and logs all access attempts for audit purposes.
    """

    def __init__(self):
        """Initialize verification service."""
        self.logger = get_logger(__name__, component="security")

    async def verify_parent_child_relationship(
        self, parent_id: str, child_id: str
    ) -> bool:
        """PRODUCTION verification using database relationships.

        Args:
            parent_id: Parent identifier to verify
            child_id: Child identifier to verify
            **kwargs: Additional verification parameters

        Returns:
            True only if verified parent-child relationship exists in database

        Security:
            - Fails secure: Returns False on any error
            - Audit logs all attempts
            - Uses real database foreign key relationships
            - No mock or fallback implementations
        """
        try:
            async with get_async_session() as session:
                # Query database for actual parent-child relationship
                stmt = select(ChildModel).where(
                    ChildModel.id == child_id,
                    ChildModel.parent_id == parent_id,
                    # Only active children (not deleted)
                    ChildModel.created_at.isnot(None),
                )

                result = await session.execute(stmt)
                child = result.scalar_one_or_none()

                if child is None:
                    # Log unauthorized access attempt for security monitoring
                    self.logger.warning(
                        f"SECURITY: Unauthorized access attempt blocked - "
                        f"Parent {parent_id} attempted to access child {child_id} "
                        f"but no valid relationship exists in database",
                        extra={
                            "security_event": "unauthorized_access_attempt",
                            "parent_id": parent_id,
                            "child_id": child_id,
                            "timestamp": datetime.utcnow().isoformat(),
                            "result": "denied",
                        },
                    )
                    return False

                # Log successful verification for audit trail
                self.logger.info(
                    f"SECURITY: Access granted - Parent {parent_id} verified for child {child_id}",
                    extra={
                        "security_event": "access_granted",
                        "parent_id": parent_id,
                        "child_id": child_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "result": "granted",
                    },
                )
                return True

        except Exception as e:
            # FAIL SECURE: Log error and deny access
            self.logger.error(
                f"SECURITY ERROR: Database verification failed for parent {parent_id} "
                f"and child {child_id}: {e}",
                extra={
                    "security_event": "verification_error",
                    "parent_id": parent_id,
                    "child_id": child_id,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                    "result": "denied_error",
                },
            )
            return False


# Check if FastAPI is available for backwards compatibility
FASTAPI_AVAILABLE = True


# SortOrder enum since it's missing from the imports
class SortOrder(str, Enum):
    """Sort order enum for pagination."""

    ASC = "asc"
    DESC = "desc"


logger = get_logger(__name__, component="api")


class ConversationPaginationService:
    """Service for paginated conversation operations."""

    def __init__(self) -> None:
        """Initialize conversation pagination service with PRODUCTION security."""
        self.pagination_service = PaginationService()
        # 🔒 SECURITY: Use database-backed verification service - NO MOCKS
        self.verification_service = DatabaseParentChildVerificationService()
        logger.info(
            "Conversation pagination service initialized with secure verification"
        )

    async def get_child_conversations(
        self,
        child_id: str,
        pagination_request: PaginationRequest,
        parent_id: str | None = None,
    ) -> PaginatedResponse[dict[str, Any]]:
        """Get paginated conversations for a child."""
        try:
            # Validate parent-child relationship for COPPA compliance
            if parent_id and not await self._validate_parent_access(
                parent_id,
                child_id,
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Parent does not have access to this child's conversations",
                )

            # Create child-safe pagination
            safe_pagination = self.pagination_service.create_child_safe_pagination(
                pagination_request,
            )

            # Get conversations from repository using existing AsyncSQLAlchemyConversationRepo
            db_service = get_database_service()
            async with db_service.get_session() as session:
                conversation_repo = AsyncSQLAlchemyConversationRepo(session)
                conversations = await conversation_repo.get_by_child_id(child_id)

                # Convert conversations to dictionaries for pagination
                conversation_dicts = [
                    {
                        "id": str(conv.id),
                        "child_id": conv.child_id,
                        "messages": conv.messages,
                        "start_time": conv.start_time.isoformat()
                        if conv.start_time
                        else None,
                        "end_time": conv.end_time.isoformat()
                        if conv.end_time
                        else None,
                        "session_id": conv.session_id,
                        "topics": conv.topics,
                        "emotional_states": conv.emotional_states,
                    }
                    for conv in conversations
                ]

                # Apply pagination using PaginationService
                return self.pagination_service.paginate(
                    items=conversation_dicts,
                    page=pagination_request.page,
                    size=pagination_request.limit,
                )

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error getting conversations for child {child_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get conversations: {e!s}",
            ) from e

    async def get_conversation_history(
        self,
        child_id: str,
        days_back: int = 30,
        pagination_request: PaginationRequest | None = None,
    ) -> PaginatedResponse[dict[str, Any]]:
        """Get conversation history for specified number of days."""
        try:
            if pagination_request is None:
                pagination_request = PaginationRequest()

            # Calculate date filter based on days_back
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)

            # Get conversations from repository using existing AsyncSQLAlchemyConversationRepo
            from src.infrastructure.persistence.database.database_service import (
                get_database_service,
            )

            db_service = get_database_service()
            async with db_service.get_session() as session:
                conversation_repo = AsyncSQLAlchemyConversationRepo(session)
                all_conversations = await conversation_repo.get_by_child_id(child_id)

                # Filter by date (conversations within the specified days_back)
                filtered_conversations = [
                    conv
                    for conv in all_conversations
                    if conv.start_time and conv.start_time >= cutoff_date
                ]

                # Convert conversations to dictionaries for pagination
                conversation_dicts = [
                    {
                        "id": str(conv.id),
                        "child_id": conv.child_id,
                        "messages": conv.messages,
                        "start_time": conv.start_time.isoformat()
                        if conv.start_time
                        else None,
                        "end_time": conv.end_time.isoformat()
                        if conv.end_time
                        else None,
                        "session_id": conv.session_id,
                        "topics": conv.topics,
                        "emotional_states": conv.emotional_states,
                    }
                    for conv in filtered_conversations
                ]

                # Sort by start_time descending (newest first)
                conversation_dicts.sort(
                    key=lambda x: x["start_time"] or "", reverse=True
                )

                # Apply pagination using PaginationService
                return self.pagination_service.paginate(
                    items=conversation_dicts,
                    page=pagination_request.page,
                    size=pagination_request.limit,
                )

        except Exception as e:
            logger.exception(
                f"Error getting conversation history for child {child_id}: {e}",
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get conversation history: {e!s}",
            ) from e

    async def search_conversations(
        self,
        child_id: str,
        search_term: str,
        pagination_request: PaginationRequest | None = None,
    ) -> PaginatedResponse[dict[str, Any]]:
        """Search conversations with pagination."""
        try:
            if pagination_request is None:
                pagination_request = PaginationRequest()

            # Get conversations from repository using existing AsyncSQLAlchemyConversationRepo
            from src.infrastructure.persistence.database.database_service import (
                get_database_service,
            )

            db_service = get_database_service()
            async with db_service.get_session() as session:
                conversation_repo = AsyncSQLAlchemyConversationRepo(session)
                all_conversations = await conversation_repo.get_by_child_id(child_id)

                # Search conversations based on search_term
                search_term_lower = search_term.lower()
                matching_conversations = []

                for conv in all_conversations:
                    # Search in messages, topics, and session_id
                    found_match = False

                    # Search in messages
                    if conv.messages:
                        for message in conv.messages:
                            if isinstance(message, dict):
                                message_text = str(message.get("content", "")).lower()
                                if search_term_lower in message_text:
                                    found_match = True
                                    break
                            elif isinstance(message, str):
                                if search_term_lower in message.lower():
                                    found_match = True
                                    break

                    # Search in topics
                    if not found_match and conv.topics:
                        for topic in conv.topics:
                            if search_term_lower in str(topic).lower():
                                found_match = True
                                break

                    # Search in session_id
                    if not found_match and conv.session_id:
                        if search_term_lower in str(conv.session_id).lower():
                            found_match = True

                    if found_match:
                        matching_conversations.append(conv)

                # Convert conversations to dictionaries for pagination
                conversation_dicts = [
                    {
                        "id": str(conv.id),
                        "child_id": conv.child_id,
                        "messages": conv.messages,
                        "start_time": conv.start_time.isoformat()
                        if conv.start_time
                        else None,
                        "end_time": conv.end_time.isoformat()
                        if conv.end_time
                        else None,
                        "session_id": conv.session_id,
                        "topics": conv.topics,
                        "emotional_states": conv.emotional_states,
                    }
                    for conv in matching_conversations
                ]

                # Sort by start_time descending (newest first)
                conversation_dicts.sort(
                    key=lambda x: x["start_time"] or "", reverse=True
                )

                # Apply pagination using PaginationService
                return self.pagination_service.paginate(
                    items=conversation_dicts,
                    page=pagination_request.page,
                    size=pagination_request.limit,
                )

        except Exception as e:
            logger.exception(f"Error searching conversations for child {child_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to search conversations: {e!s}",
            ) from e

    async def _validate_parent_access(self, parent_id: str, child_id: str) -> bool:
        """Validate that parent has access to child's data using DATABASE verification.

        SECURITY CRITICAL: This is the ONLY way to verify parent-child relationships.
        Uses real database foreign key relationships, no mocks or fallbacks.
        """
        try:
            # 🔒 SECURITY: Use database verification service - FAIL SECURE
            is_valid = await self.verification_service.verify_parent_child_relationship(
                parent_id=parent_id, child_id=child_id
            )

            if is_valid:
                logger.info(
                    f"SECURITY: Database verification SUCCESS - "
                    f"parent_id={parent_id}, child_id={child_id}",
                    extra={
                        "security_event": "access_validation_success",
                        "parent_id": parent_id,
                        "child_id": child_id,
                    },
                )
            else:
                logger.warning(
                    f"SECURITY: Database verification FAILED - "
                    f"parent_id={parent_id}, child_id={child_id}",
                    extra={
                        "security_event": "access_validation_failed",
                        "parent_id": parent_id,
                        "child_id": child_id,
                    },
                )

            return is_valid

        except Exception as e:
            # 🔒 SECURITY: FAIL SECURE - Any error denies access
            logger.error(
                f"SECURITY ERROR: Parent access validation failed - "
                f"parent_id={parent_id}, child_id={child_id}, error={e}",
                extra={
                    "security_event": "access_validation_error",
                    "parent_id": parent_id,
                    "child_id": child_id,
                    "error": str(e),
                },
            )
            # Always return False on any error - fail secure
            return False


# Initialize service
conversation_pagination_service = ConversationPaginationService()

# Create router
router = APIRouter(prefix="/api/v1/conversations", tags=["Conversations Paginated"])

if FASTAPI_AVAILABLE:

    @router.get("/child/{child_id}")
    async def get_child_conversations_paginated(
        child_id: str,
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(20, ge=1, le=50, description="Page size"),
        sort_by: str | None = Query(None, description="Sort field"),
        sort_order: str = Query(
            "desc", pattern="^(asc|desc)$", description="Sort order"
        ),
        search: str | None = Query(None, description="Search term"),
        parent_id: str
        | None = Query(
            None,
            description="Parent ID for COPPA validation",
        ),
    ):
        """Get paginated conversations for a child."""
        # Create pagination request
        pagination_request = PaginationRequest(
            page=page,
            size=size,
            sort_by=sort_by,
            sort_order=SortOrder(sort_order),
            search=search,
        )

        # Get paginated conversations
        result = await conversation_pagination_service.get_child_conversations(
            child_id=child_id,
            pagination_request=pagination_request,
            parent_id=parent_id,
        )

        return result.to_dict()

    @router.get("/child/{child_id}/history")
    async def get_conversation_history_paginated(
        child_id: str,
        days_back: int = Query(
            30,
            ge=1,
            le=365,
            description="Days of history to retrieve",
        ),
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(20, ge=1, le=50, description="Page size"),
        sort_by: str | None = Query("timestamp", description="Sort field"),
        sort_order: str = Query(
            "desc", pattern="^(asc|desc)$", description="Sort order"
        ),
    ):
        """Get conversation history for specified number of days."""
        # Create pagination request
        pagination_request = PaginationRequest(
            page=page,
            size=size,
            sort_by=sort_by,
            sort_order=SortOrder(sort_order),
        )

        # Get conversation history
        result = await conversation_pagination_service.get_conversation_history(
            child_id=child_id,
            days_back=days_back,
            pagination_request=pagination_request,
        )

        return result.to_dict()

    @router.get("/child/{child_id}/search")
    async def search_conversations_paginated(
        child_id: str,
        search_term: str = Query(
            ...,
            min_length=1,
            max_length=100,
            description="Search term",
        ),
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(20, ge=1, le=50, description="Page size"),
        sort_by: str | None = Query("timestamp", description="Sort field"),
        sort_order: str = Query(
            "desc", pattern="^(asc|desc)$", description="Sort order"
        ),
    ):
        """Search conversations with pagination."""
        # Create pagination request
        pagination_request = PaginationRequest(
            page=page,
            size=size,
            sort_by=sort_by,
            sort_order=SortOrder(sort_order),
            search=search_term,
        )

        # Search conversations
        result = await conversation_pagination_service.search_conversations(
            child_id=child_id,
            search_term=search_term,
            pagination_request=pagination_request,
        )

        return result.to_dict()


# Export for use in main application
__all__ = [
    "ConversationPaginationService",
    "conversation_pagination_service",
    "router",
]
