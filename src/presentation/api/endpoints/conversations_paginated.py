"""Paginated Conversations Endpoints
Provides paginated access to child conversations with COPPA compliance.
"""

from datetime import datetime, timedelta
from typing import Any

from src.infrastructure.logging_config import get_logger
from src.infrastructure.pagination import (
    PaginatedResponse,
    PaginationRequest,
    PaginationService,
    SortOrder,
)

logger = get_logger(__name__, component="api")

# Import FastAPI dependencies
try:
    from fastapi import APIRouter, HTTPException, Query, status

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    logger.warning("FastAPI not available, using mock classes")

    class APIRouter:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def get(self, path: str, **kwargs):
            def decorator(func):
                return func

            return decorator


# Mock conversation data for demonstration
def create_mock_conversations(
    child_id: str, count: int = 100
) -> list[dict[str, Any]]:
    """Create mock conversation data for pagination testing."""
    conversations = []
    for i in range(count):
        conversation_time = datetime.utcnow() - timedelta(days=i, hours=i % 24)
        conversations.append(
            {
                "conversation_id": f"conv_{child_id}_{i:03d}",
                "child_id": child_id,
                "timestamp": conversation_time.isoformat(),
                "child_message": f"Hello teddy! This is message {i + 1}",
                "ai_response": f"Hello! I'm happy to talk with you. This is response {i + 1}",
                "safety_flags": ["appropriate_content"] if i % 10 == 0 else [],
                "emotion_detected": ["happy", "curious", "excited", "calm"][
                    i % 4
                ],
                "session_duration_minutes": (i % 30) + 5,
                "created_at": conversation_time.isoformat(),
                "updated_at": conversation_time.isoformat(),
            },
        )
    return conversations


class ConversationPaginationService:
    """Service for paginated conversation operations."""

    def __init__(self) -> None:
        """Initialize conversation pagination service."""
        self.pagination_service = PaginationService()
        self.mock_data = {}  # Cache for mock data
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
            safe_pagination = (
                self.pagination_service.create_child_safe_pagination(
                    pagination_request,
                )
            )

            # Get conversations (mock data for now)
            if child_id not in self.mock_data:
                self.mock_data[child_id] = create_mock_conversations(child_id)
            conversations = self.mock_data[child_id]

            # Apply pagination
            result = self.pagination_service.paginate_list(
                conversations,
                safe_pagination,
            )

            logger.info(
                f"Retrieved {len(result.items)} conversations for child {child_id}",
            )
            return result
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Error getting conversations for child {child_id}: {e}"
            )
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

            # Filter conversations by date
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)

            # Get all conversations
            if child_id not in self.mock_data:
                self.mock_data[child_id] = create_mock_conversations(child_id)
            all_conversations = self.mock_data[child_id]

            # Filter by date
            recent_conversations = [
                conv
                for conv in all_conversations
                if datetime.fromisoformat(conv["timestamp"]) >= cutoff_date
            ]

            # Apply pagination
            safe_pagination = (
                self.pagination_service.create_child_safe_pagination(
                    pagination_request,
                )
            )
            result = self.pagination_service.paginate_list(
                recent_conversations,
                safe_pagination,
            )

            logger.info(
                f"Retrieved {len(result.items)} recent conversations for child {child_id}",
            )
            return result
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

            # Set search term in pagination request
            pagination_request.search = search_term

            # Get conversations
            if child_id not in self.mock_data:
                self.mock_data[child_id] = create_mock_conversations(child_id)
            conversations = self.mock_data[child_id]

            # Apply pagination with search
            safe_pagination = (
                self.pagination_service.create_child_safe_pagination(
                    pagination_request,
                )
            )
            result = self.pagination_service.paginate_list(
                conversations,
                safe_pagination,
            )

            logger.info(
                f"Found {len(result.items)} conversations matching '{search_term}' for child {child_id}",
            )
            return result
        except Exception as e:
            logger.error(
                f"Error searching conversations for child {child_id}: {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to search conversations: {e!s}",
            )

    async def _validate_parent_access(
        self, parent_id: str, child_id: str
    ) -> bool:
        """Validate that parent has access to child's data."""
        # Mock validation - in production this would check the database
        logger.info(
            f"Validating parent {parent_id} access to child {child_id}"
        )
        return True  # Mock approval


# Initialize service
conversation_pagination_service = ConversationPaginationService()

# Create router
router = APIRouter(
    prefix="/api/v1/conversations", tags=["Conversations Paginated"]
)

if FASTAPI_AVAILABLE:

    @router.get("/child/{child_id}")
    async def get_child_conversations_paginated(
        child_id: str,
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(20, ge=1, le=50, description="Page size"),
        sort_by: str | None = Query(None, description="Sort field"),
        sort_order: str = Query(
            "desc", regex="^(asc|desc)$", description="Sort order"
        ),
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
        sort_order: str = Query(
            "desc", regex="^(asc|desc)$", description="Sort order"
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
        result = (
            await conversation_pagination_service.get_conversation_history(
                child_id=child_id,
                days_back=days_back,
                pagination_request=pagination_request,
            )
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
            "desc", regex="^(asc|desc)$", description="Sort order"
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
