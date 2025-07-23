"""User Repository.

Handles all user-related database operations.
"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from src.infrastructure.logging_config import get_logger
from src.infrastructure.persistence.database_manager import Database
from src.infrastructure.persistence.models.user_model import UserModel
from src.infrastructure.validators.security.database_input_validator import (
    SecurityError,
    create_safe_database_session,
    database_input_validation,
    validate_database_operation,
)

logger = get_logger(__name__, component="persistence")


class UserRepository:
    """Repository for user-related database operations."""

    def __init__(self, database: Database) -> None:
        """Initialize user repository.

        Args:
            database: Database instance

        """
        self.database = database
        logger.info("UserRepository initialized")

    @database_input_validation("users")
    async def create_user(self, email: str, hashed_password: str, role: str) -> str:
        """Create a new user with comprehensive input validation.

        Args:
            email: User email
            hashed_password: Hashed password
            role: User role

        Returns:
            User ID

        Raises:
            ValueError: If user already exists or data is invalid

        """
        try:
            # Validate and sanitize input parameters
            user_data = {
                "email": email,
                "password_hash": hashed_password,
                "role": role,
            }
            # Validate operation
            validated_operation = validate_database_operation(
                "INSERT",
                "users",
                user_data,
            )
            validated_data = validated_operation["data"]

            async with self.database.get_session() as session:
                # Create safe database session
                safe_session = create_safe_database_session(session)

                # Check if user already exists
                existing_user = await safe_session.execute(
                    select(UserModel).where(UserModel.email == validated_data["email"]),
                )
                if existing_user.scalar_one_or_none():
                    raise ValueError("User with this email already exists")

                # Create new user
                user_id = str(uuid4())
                new_user = UserModel(
                    id=user_id,
                    email=validated_data["email"],
                    password_hash=validated_data["password_hash"],
                    role=validated_data["role"],
                    created_at=datetime.utcnow(),
                )
                safe_session.add(new_user)
                await safe_session.commit()
                logger.info(f"User created: {user_id}")
                return user_id
        except IntegrityError:
            logger.warning(f"Attempt to create duplicate user: {email}")
            raise ValueError("User with this email already exists")
        except SecurityError as e:
            logger.error(f"Security error creating user: {e}")
            raise ValueError("Invalid data provided for user creation")
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise

    @database_input_validation("users")
    async def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        """Get user by email.

        Args:
            email: User email

        Returns:
            User data or None if not found

        """
        try:
            async with self.database.get_session() as session:
                result = await session.execute(
                    select(UserModel).where(UserModel.email == email),
                )
                user = result.scalar_one_or_none()
                if user:
                    return {
                        "id": user.id,
                        "email": user.email,
                        "role": user.role,
                        "password_hash": user.password_hash,
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            raise

    @database_input_validation("users")
    async def update_user_role(self, user_id: str, new_role: str) -> bool:
        """Update user role.

        Args:
            user_id: User ID
            new_role: New role for the user

        Returns:
            True if successful, False otherwise

        """
        try:
            validated_operation = validate_database_operation(
                "UPDATE",
                "users",
                {"role": new_role},
            )
            validated_role = validated_operation["data"]["role"]

            async with self.database.get_session() as session:
                stmt = (
                    update(UserModel)
                    .where(UserModel.id == user_id)
                    .values(role=validated_role)
                )
                result = await session.execute(stmt)
                await session.commit()
                return result.rowcount > 0
        except SecurityError as e:
            logger.error(f"Security error updating user role: {e}")
            return False
        except Exception as e:
            logger.error(f"Error updating user role: {e}")
            return False
