"""Conversation Repository.

Handles all conversation and interaction-related database operations.
"""

from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from sqlalchemy import and_
from sqlalchemy.future import select
from sqlalchemy.sql import func

from src.infrastructure.logging_config import get_logger
from src.infrastructure.persistence.database import Database
from src.infrastructure.persistence.models.conversation_model import (
    ConversationModel,
)
from src.infrastructure.security.database_input_validator import (
    SecurityError,
    database_input_validation,
    validate_database_operation,
)

logger = get_logger(__name__, component="persistence")


class ConversationRepository:
    """Repository for conversation-related database operations."""

    def __init__(self, database: Database) -> None:
        """Initialize conversation repository.

        Args:
            database: Database instance

        """
        self.database = database
        logger.info("ConversationRepository initialized")

    @database_input_validation("conversations")
    async def create_conversation(
        self,
        child_id: str,
        message: str,
        response: str,
    ) -> str:
        """Create a new conversation record.

        Args:
            child_id: Child ID
            message: User message
            response: AI response

        Returns:
            Conversation ID

        """
        try:
            conversation_data = {
                "child_id": child_id,
                "message": message,
                "response": response,
            }
            validated_operation = validate_database_operation(
                "INSERT",
                "conversations",
                conversation_data,
            )
            validated_data = validated_operation["data"]
            conversation_id = str(uuid4())

            async with self.database.get_session() as session:
                new_conversation = ConversationModel(
                    id=conversation_id,
                    child_id=validated_data["child_id"],
                    message=validated_data["message"],
                    response=validated_data["response"],
                    created_at=datetime.utcnow(),
                )
                session.add(new_conversation)
                await session.commit()
                logger.info(f"Conversation created: {conversation_id}")
                return conversation_id
        except SecurityError as e:
            logger.error(f"Security error creating conversation: {e}")
            raise ValueError("Invalid data for conversation")
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            raise

    @database_input_validation("conversations")
    async def get_conversations_by_child_id(
        self,
        child_id: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get conversations for a child.

        Args:
            child_id: Child ID
            limit: Max number of conversations to return

        Returns:
            List of conversation records

        """
        try:
            async with self.database.get_session() as session:
                result = await session.execute(
                    select(ConversationModel)
                    .where(ConversationModel.child_id == child_id)
                    .order_by(ConversationModel.created_at.desc())
                    .limit(limit),
                )
                conversations = result.scalars().all()
                return [
                    {
                        "id": c.id,
                        "message": c.message,
                        "response": c.response,
                        "created_at": c.created_at,
                    }
                    for c in conversations
                ]
        except Exception as e:
            logger.error(f"Error getting conversations: {e}")
            raise

    @database_input_validation("conversations")
    async def get_recent_conversation_summary(
        self,
        child_id: str,
        days: int = 7,
    ) -> dict[str, Any]:
        """Get a summary of recent conversations.

        Args:
            child_id: Child ID
            days: Number of days to look back

        Returns:
            Summary of conversation statistics

        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            async with self.database.get_session() as session:
                result = await session.execute(
                    select(
                        func.count(ConversationModel.id),
                        func.avg(
                            func.length(ConversationModel.message)
                            + func.length(ConversationModel.response),
                        ),
                    ).where(
                        and_(
                            ConversationModel.child_id == child_id,
                            ConversationModel.created_at >= start_date,
                        ),
                    ),
                )
                count, avg_length = result.one()
                return {
                    "total_conversations": count or 0,
                    "average_length": avg_length or 0,
                    "period_days": days,
                }
        except Exception as e:
            logger.error(f"Error getting conversation summary: {e}")
            raise
