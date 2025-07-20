from abc import abstractmethod
from src.domain.interfaces import IConversationRepository
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, update as sql_update, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.domain.entities.conversation import Conversation
from src.infrastructure.persistence.models.conversation_models import ConversationModel


class ConversationRepository(IConversationRepository):
    """Async repository interface for conversation operations."""
    pass







class AsyncSQLAlchemyConversationRepo(ConversationRepository):
    """Async SQLAlchemy implementation of ConversationRepository."""

    def __init__(self, session: AsyncSession):
        """Initialize the repository with an async session.
        
        Args:
            session: The async SQLAlchemy session for database operations.
        """
        self.session = session

    async def get_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """Retrieve a conversation by its ID.
        
        Args:
            conversation_id: The ID of the conversation to retrieve.
            
        Returns:
            The Conversation entity if found, None otherwise.
        """
        try:
            result = await self.session.execute(
                select(ConversationModel).where(ConversationModel.id == conversation_id)
            )
            conversation_model = result.scalar_one_or_none()
            
            if conversation_model:
                return conversation_model.to_entity()
            return None
        except SQLAlchemyError as e:
            raise ValueError(f"Database error while retrieving conversation: {str(e)}")

    async def get_all(self) -> List[Conversation]:
        """Retrieve all conversations.
        
        Returns:
            A list of all Conversation entities.
        """
        try:
            result = await self.session.execute(select(ConversationModel))
            conversation_models = result.scalars().all()
            
            return [model.to_entity() for model in conversation_models]
        except SQLAlchemyError as e:
            raise ValueError(f"Database error while retrieving conversations: {str(e)}")

    async def create(self, conversation: Conversation) -> Conversation:
        """Create a new conversation in the database.
        
        Args:
            conversation: The Conversation entity to create.
            
        Returns:
            The created Conversation entity.
        """
        try:
            conversation_model = ConversationModel.from_entity(conversation)
            self.session.add(conversation_model)
            await self.session.commit()
            await self.session.refresh(conversation_model)
            
            return conversation_model.to_entity()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ValueError(f"Database error while creating conversation: {str(e)}")

    async def update(self, conversation_id: str, data: dict) -> Optional[Conversation]:
        """Update a conversation with the provided data.
        
        Args:
            conversation_id: The ID of the conversation to update.
            data: Dictionary containing the fields to update.
            
        Returns:
            The updated Conversation entity if found, None otherwise.
        """
        try:
            # Filter out None values and convert UUIDs to strings if present
            update_data = {}
            for key, value in data.items():
                if value is not None:
                    if isinstance(value, UUID):
                        update_data[key] = str(value)
                    else:
                        update_data[key] = value
            
            if update_data:
                await self.session.execute(
                    sql_update(ConversationModel)
                    .where(ConversationModel.id == conversation_id)
                    .values(**update_data)
                )
                await self.session.commit()
            
            # Retrieve the updated conversation
            return await self.get_by_id(conversation_id)
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ValueError(f"Database error while updating conversation: {str(e)}")

    async def delete(self, conversation_id: str) -> None:
        """Delete a conversation by its ID.
        
        Args:
            conversation_id: The ID of the conversation to delete.
        """
        try:
            await self.session.execute(
                sql_delete(ConversationModel).where(ConversationModel.id == conversation_id)
            )
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ValueError(f"Database error while deleting conversation: {str(e)}")

    # Implement the abstract methods from ConversationRepository
    async def add(self, conversation: Conversation) -> None:
        """Add a new conversation to the database.
        
        Args:
            conversation: The Conversation entity to add.
        """
        await self.create(conversation)

    async def get_by_child_id(self, child_id: str) -> List[Conversation]:
        """Retrieve all conversations for a specific child.
        
        Args:
            child_id: The ID of the child.
            
        Returns:
            A list of Conversation entities for the specified child.
        """
        try:
            result = await self.session.execute(
                select(ConversationModel).where(ConversationModel.child_id == child_id)
            )
            conversation_models = result.scalars().all()
            
            return [model.to_entity() for model in conversation_models]
        except SQLAlchemyError as e:
            raise ValueError(f"Database error while retrieving conversations by child_id: {str(e)}")
