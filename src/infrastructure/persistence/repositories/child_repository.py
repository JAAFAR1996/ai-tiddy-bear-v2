"""
Child Repository

Handles all child-related database operations with COPPA compliance.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.infrastructure.logging_config import get_logger
from src.infrastructure.persistence.database import Database
from src.infrastructure.persistence.models.child_model import ChildModel
from src.infrastructure.security.coppa import get_consent_manager
from src.infrastructure.security.database_input_validator import (
    SecurityError,
    create_safe_database_session,
    database_input_validation,
    validate_database_operation,
)

logger = get_logger(__name__, component="persistence")


class ChildRepository:
    """Repository for child-related database operations."""

    def __init__(self, database: Database) -> None:
        """Initialize child repository.

        Args:
            database: Database instance
        """
        self.database = database
        self.consent_manager = get_consent_manager()
        logger.info("ChildRepository initialized with COPPA compliance")

    @database_input_validation("children")
    async def create_child(
        self, parent_id: str, child_data: Dict[str, Any]
    ) -> str:
        """Create a new child profile with COPPA compliance.

        Args:
            parent_id: Parent user ID
            child_data: Child profile data

        Returns:
            Child ID

        Raises:
            ValueError: If data is invalid or parent lacks consent
        """
        try:
            # Verify parental consent
            if not self.consent_manager.has_consent(parent_id):
                raise ValueError("Parent has not provided COPPA consent")

            # Validate child data
            validated_operation = validate_database_operation(
                "INSERT", "children", child_data
            )
            validated_data = validated_operation["data"]
            child_id = str(uuid4())

            async with self.database.get_session() as session:
                new_child = ChildModel(
                    id=child_id,
                    parent_id=parent_id,
                    name=validated_data["name"],
                    age=validated_data["age"],
                    preferences=validated_data.get("preferences", {}),
                    created_at=datetime.utcnow(),
                )
                session.add(new_child)
                await session.commit()
                logger.info(f"Child profile created: {child_id}")
                return child_id
        except SecurityError as e:
            logger.error(f"Security error creating child: {e}")
            raise ValueError("Invalid data provided for child creation")
        except Exception as e:
            logger.error(f"Error creating child: {e}")
            raise

    @database_input_validation("children")
    async def get_child_by_id(self, child_id: str) -> Optional[Dict[str, Any]]:
        """Get child profile by ID.

        Args:
            child_id: Child ID

        Returns:
            Child profile data or None if not found
        """
        try:
            async with self.database.get_session() as session:
                result = await session.execute(
                    select(ChildModel).where(ChildModel.id == child_id)
                )
                child = result.scalar_one_or_none()
                if child:
                    return {
                        "id": child.id,
                        "parent_id": child.parent_id,
                        "name": child.name,
                        "age": child.age,
                        "preferences": child.preferences,
                        "created_at": child.created_at,
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting child by ID: {e}")
            raise

    @database_input_validation("children")
    async def update_child_preferences(
        self, child_id: str, preferences: Dict[str, Any]
    ) -> bool:
        """Update child preferences.

        Args:
            child_id: Child ID
            preferences: New preferences

        Returns:
            True if successful, False otherwise
        """
        try:
            validated_operation = validate_database_operation(
                "UPDATE", "children", {"preferences": preferences}
            )
            validated_preferences = validated_operation["data"]["preferences"]

            async with self.database.get_session() as session:
                stmt = (
                    update(ChildModel)
                    .where(ChildModel.id == child_id)
                    .values(preferences=validated_preferences)
                )
                result = await session.execute(stmt)
                await session.commit()
                return result.rowcount > 0
        except SecurityError as e:
            logger.error(f"Security error updating child preferences: {e}")
            return False
        except Exception as e:
            logger.error(f"Error updating child preferences: {e}")
            return False