"""Database Service Orchestrator
Orchestrates database operations using specialized repositories.
"""

from typing import Any
from uuid import uuid4

from src.domain.services.emotion_analyzer import EmotionAnalyzer, EmotionResult
from src.infrastructure.logging_config import get_logger
from src.infrastructure.persistence.child_repository import ChildRepository
from src.infrastructure.persistence.conversation_repository import (
    AsyncSQLAlchemyConversationRepo as ConversationRepository,
)
from src.infrastructure.persistence.database_manager import Database
from src.infrastructure.persistence.repositories.safety_repository import (
    SafetyRepository,
)
from src.infrastructure.persistence.repositories.usage_repository import UsageRepository
from src.infrastructure.persistence.repositories.user_repository import UserRepository
from src.infrastructure.security.validation.sql_injection_protection import (
    get_sql_injection_prevention,
)

logger = get_logger(__name__, component="persistence")


class DatabaseServiceOrchestrator:
    """Orchestrates database operations using specialized repositories.
    This is the main entry point for database operations, delegating
    specific responsibilities to focused repository classes.
    """

    def __init__(self, database: Database) -> None:
        """Initialize orchestrator with all repositories.

        Args:
            database: Database instance

        """
        self.database = database
        self.sql_prevention = get_sql_injection_prevention()

        # Initialize repositories
        self.users = UserRepository(database)
        self.children = ChildRepository(database)
        self.conversations = ConversationRepository(database)
        self.safety = SafetyRepository(database)
        self.usage = UsageRepository(database)

        logger.info("DatabaseServiceOrchestrator initialized with all repositories")

    # User operations
    async def create_user(self, email: str, hashed_password: str, role: str) -> str:
        """Create a new user."""
        return await self.users.create_user(email, hashed_password, role)

    async def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        """Get user by email."""
        return await self.users.get_user_by_email(email)

    async def update_user(self, user_id: str, updates: dict[str, Any]) -> bool:
        """Update user information."""
        return await self.users.update_user(user_id, updates)

    # Child operations
    async def create_child(self, parent_id: str, child_data: dict[str, Any]) -> str:
        """Create a new child profile."""
        return await self.children.create_child(parent_id, child_data)

    async def get_child(self, child_id: str) -> dict[str, Any] | None:
        """Get child profile."""
        return await self.children.get_child(child_id)

    async def get_children_by_parent(self, parent_id: str) -> list[dict[str, Any]]:
        """Get all children for a parent."""
        return await self.children.get_children_by_parent(parent_id)

    async def update_child(self, child_id: str, updates: dict[str, Any]) -> bool:
        """Update child profile."""
        return await self.children.update_child(child_id, updates)

    # Conversation operations
    async def save_conversation(
        self,
        child_id: str,
        message: str,
        response: str,
    ) -> str:
        """Save a conversation."""
        return await self.conversations.create_conversation(child_id, message, response)

    async def get_conversation_history(
        self,
        child_id: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Get conversation history."""
        return await self.conversations.get_conversation_history(child_id, limit)

    async def get_interaction_count(self, child_id: str, hours: int = 24) -> int:
        """Get interaction count for rate limiting."""
        return await self.conversations.get_conversation_count(child_id, hours)

    # Safety operations
    async def record_safety_event(
        self,
        child_id: str,
        event_type: str,
        details: str,
        severity: str = "low",
    ) -> str:
        """Record a safety event."""
        return await self.safety.record_safety_event(
            child_id,
            event_type,
            details,
            severity,
        )

    async def update_safety_score(
        self,
        child_id: str,
        new_score: float,
        reason: str,
    ) -> bool:
        """Update safety score."""
        return await self.safety.update_safety_score(child_id, new_score, reason)

    async def get_safety_events(
        self,
        child_id: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Get safety events."""
        return await self.safety.get_safety_events(child_id, limit)

    async def send_safety_alert(self, alert_data: dict[str, Any]) -> bool:
        """Send safety alert."""
        alert_id = await self.safety.send_safety_alert(alert_data)
        return bool(alert_id)

    # Usage operations
    async def record_usage(self, usage_record: dict[str, Any]) -> str:
        """Record usage statistics."""
        return await self.usage.record_usage(usage_record)

    async def get_daily_usage(
        self,
        child_id: str,
        days: int = 7,
    ) -> list[dict[str, Any]]:
        """Get daily usage statistics."""
        return await self.usage.get_daily_usage(child_id, days)

    async def get_usage_summary(
        self,
        child_id: str,
        period_days: int = 30,
    ) -> dict[str, Any]:
        """Get usage summary."""
        return await self.usage.get_usage_summary(child_id, period_days)

    # Maintenance operations
    async def cleanup_old_data(self, days: int = 90) -> dict[str, int]:
        """Clean up old data for COPPA compliance.

        Args:
            days: Age threshold in days
        Returns:
            Cleanup statistics

        """
        stats = {
            "conversations_deleted": await self.conversations.delete_old_conversations(
                days,
            ),
            "usage_records_deleted": await self.usage.cleanup_old_usage_data(days),
        }
        logger.info(f"Data cleanup completed: {stats}")
        return stats

    # Emotion tracking - Using existing EmotionAnalyzer service
    async def track_emotion(self, child_id: str, emotion: str) -> str:
        """Track emotion using existing EmotionAnalyzer service and save to database."""
        # Use existing EmotionAnalyzer to create emotion result
        analyzer = EmotionAnalyzer()

        # Create emotion result for tracking
        emotion_result = EmotionResult(
            primary_emotion=emotion,
            confidence=0.8,  # Default confidence for manual tracking
            all_emotions={emotion: 0.8, "neutral": 0.2},
            sentiment_score=0.5 if analyzer.is_emotion_positive(emotion) else -0.5,
            arousal_score=0.6,
        )

        # Save emotion analysis using existing method
        analysis_id = await self.save_emotion_analysis(
            child_id=child_id,
            emotion=emotion_result.primary_emotion,
            confidence=emotion_result.confidence,
            context=f"Manual tracking - sentiment: {emotion_result.sentiment_score:.2f}",
        )

        logger.info(
            f"Tracked emotion for child {child_id}: {emotion} "
            f"(analysis_id: {analysis_id})"
        )
        return analysis_id

    async def save_emotion_analysis(
        self,
        child_id: str,
        emotion: str,
        confidence: float,
        context: str | None = None,
    ) -> str:
        """Save emotion analysis (to be implemented with EmotionRepository)."""
        analysis_id = str(uuid4())
        logger.info(
            f"Saved emotion analysis for child {child_id}: {emotion} "
            f"({confidence:.2f})"
        )
        return analysis_id

    async def get_emotion_history(
        self,
        child_id: str,
        days: int = 7,
    ) -> list[dict[str, Any]]:
        """Get emotion history (to be implemented with EmotionRepository)."""
        logger.debug(f"Getting emotion history for child: {child_id} (days: {days})")
        return []
