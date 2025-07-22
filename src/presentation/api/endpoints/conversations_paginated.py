"""Paginated Conversations Endpoints
Provides paginated access to child conversations with COPPA compliance.
"""

from fastapi import APIRouter, HTTPException, Query, status
from datetime import datetime, timedelta
from typing import Any

from src.infrastructure.logging_config import get_logger
from src.infrastructure.pagination import (
    PaginatedResponse,
    PaginationRequest,
    PaginationService,
    SortOrder,
)
from src.domain.services.conversation_service import ConversationService
from src.infrastructure.persistence.repositories.conversation_repository import ConversationRepository

logger = get_logger(__name__, component="api")


class ConversationPaginationService:
    """Service for paginated conversation operations."""

    def __init__(self) -> None:
        """Initialize conversation pagination service."""
        self.pagination_service = PaginationService()
        self.conversation_service = ConversationService(
            repository=ConversationRepository()
        )
        logger.info("Conversation pagination service initialized")

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

            # جلب المحادثات من repository الفعلي
            logger.error(f"Conversations repository not implemented yet for child {child_id}")
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Conversations repository not implemented yet"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting conversations for child {child_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get conversations: {e!s}",
            )

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

            # جلب المحادثات من repository الفعلي
            logger.error(f"Conversations repository not implemented yet for child {child_id}")
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Conversations repository not implemented yet"
            )
        except Exception as e:
            logger.error(
                f"Error getting conversation history for child {child_id}: {e}",
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get conversation history: {e!s}",
            )

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

            # جلب المحادثات من repository الفعلي
            logger.error(f"Conversations repository not implemented yet for child {child_id}")
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Conversations repository not implemented yet"
            )
        except Exception as e:
            logger.error(f"Error searching conversations for child {child_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to search conversations: {e!s}",
            )

    async def _validate_parent_access(self, parent_id: str, child_id: str) -> bool:
        """Validate that parent has access to child's data."""
        logger.error(f"Parent access validation not implemented for parent {parent_id} and child {child_id}")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Parent access validation not implemented"
        )


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
        sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
        search: str | None = Query(None, description="Search term"),
        parent_id: str | None = Query(
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
        sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
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
        sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
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
