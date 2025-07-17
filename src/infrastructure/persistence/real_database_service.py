"""Database Service for AI Teddy Bear."""

"""Production Database Service for AI Teddy Bear
Enterprise-grade database service with SQL Injection prevention and comprehensive security"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import delete, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from src.infrastructure.logging_config import get_logger
from src.infrastructure.persistence.database import Database
from src.infrastructure.persistence.models.child_model import ChildModel
from src.infrastructure.persistence.models.conversation_model import ConversationModel
from src.infrastructure.persistence.models.user_model import UserModel

logger = get_logger(__name__, component="persistence")


class DatabaseService:
    """Production database service with comprehensive SQL injection prevention."""

    def __init__(self, database: Database) -> None:
        self.database = database
        self.sql_prevention = get_sql_injection_prevention()
        logger.info("DatabaseService initialized with SQL injection prevention")

    @database_input_validation("users")
    async def create_user(self, email: str, hashed_password: str, role: str) -> str:
        """Create a new user with comprehensive input validation and SQL injection prevention."""
        try:
            # Validate and sanitize input parameters
            user_data = {"email": email, "password_hash": hashed_password, "role": role}
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
                # Check if user already exists using safe query
                existing_users = await safe_session.safe_select(
                    "users",
                    ["id"],
                    {"email": validated_data["email"]},
                    limit=1,
                )
                if existing_users.rowcount > 0:
                    raise ValueError(
                        f"User with email {validated_data['email']} already exists",
                    )
                # Create new user with validated data
                user_id = str(uuid4())
                new_user = UserModel(
                    id=user_id,
                    email=validated_data["email"],
                    password_hash=validated_data["password_hash"],
                    role=validated_data["role"],
                    is_active=True,
                    email_verified=False,
                    created_at=datetime.utcnow(),
                )
                session.add(new_user)
                await session.commit()
                logger.info(
                    f"Created user: {validated_data['email']} with role: {validated_data['role']}",
                )
                return user_id
        except SecurityError as e:
            logger.error(f"Security violation creating user: {e}")
            raise ValueError(f"Invalid input data: {e}")
        except IntegrityError as e:
            logger.error(f"Database integrity error creating user {email}: {e}")
            raise ValueError("User creation failed: database constraint violation")
        except Exception as e:
            logger.error(f"Failed to create user {email}: {e}")
            raise RuntimeError(f"User creation failed: {e}") from e

    async def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        """Retrieve user by email with SQL injection prevention."""
        try:
            # Validate and sanitize email input
            email_sanitization = self.sql_prevention.sanitize_input(email, "email")
            if not email_sanitization.safe:
                logger.warning(
                    f"Unsafe email input detected: {email_sanitization.threats_found}",
                )
                return None
            sanitized_email = email_sanitization.sanitized_input
            async with self.database.get_session() as session:
                # Create safe database session
                safe_session = create_safe_database_session(session)
                # Use safe query execution
                users = await safe_session.safe_select(
                    "users",
                    [
                        "id",
                        "email",
                        "password_hash",
                        "role",
                        "is_active",
                        "email_verified",
                        "created_at",
                        "last_login",
                    ],
                    {"email": sanitized_email},
                    limit=1,
                )
                user = users.first() if users else None
                if user:
                    return {
                        "id": user.id,
                        "email": user.email,
                        "password_hash": user.password_hash,
                        "role": user.role,
                        "is_active": user.is_active,
                        "email_verified": user.email_verified,
                        "created_at": (
                            user.created_at.isoformat() if user.created_at else None
                        ),
                        "last_login": (
                            user.last_login.isoformat() if user.last_login else None
                        ),
                    }
                logger.debug(f"User not found: {sanitized_email}")
                return None
        except SecurityError as e:
            logger.error(f"Security violation getting user by email: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            raise RuntimeError(f"User lookup failed: {e}") from e

    async def create_child(
        self,
        name: str,
        age: int,
        preferences: dict[str, Any],
        parent_id: str,
    ) -> str:
        """Create a new child profile with COPPA compliance verification."""
        # ✅ Verify COPPA compliance before creating child profile
        if age <= 13:
            # For children 13 and under, require explicit data collection
            # consent
            consent_manager = get_consent_manager()
            has_consent = await consent_manager.verify_parental_consent(
                parent_id=parent_id,
                child_id="new_child",  # Will be replaced with actual child_id
                consent_type="data_collection",
            )
            if not has_consent:
                raise ValueError(
                    "Parental consent required for data collection (COPPA compliance)",
                )
        async with self.database.get_session() as session:
            # Generate UUID string for SQLite compatibility
            child_id = str(uuid4())
            child = ChildModel(
                id=child_id,
                name=name,
                age=age,
                preferences=preferences,
                parent_id=parent_id,
                created_at=datetime.utcnow(),
            )
            session.add(child)
            await session.commit()
            logger.info(
                f"Created child: {name} (ID: {child_id}) for parent: {parent_id}",
            )
            return child_id

    async def get_child_by_id(self, child_id: str) -> dict[str, Any] | None:
        """Retrieve child by ID."""
        async with self.database.get_session() as session:
            result = await session.execute(
                select(ChildModel).filter(ChildModel.id == child_id),
            )
            child = result.scalars().first()
            if child:
                return {
                    "id": child.id,
                    "name": child.name,
                    "age": child.age,
                    "preferences": child.preferences,
                    "parent_id": child.parent_id,
                    "created_at": (
                        child.created_at.isoformat() if child.created_at else None
                    ),
                }
            return None

    async def update_child(self, child_id: str, updates: dict[str, Any]) -> bool:
        """Update child profile."""
        async with self.database.get_session() as session:
            result = await session.execute(
                update(ChildModel).where(ChildModel.id == child_id).values(**updates),
            )
            await session.commit()
            return result.rowcount > 0

    async def delete_child(self, child_id: str) -> bool:
        """Delete child profile."""
        async with self.database.get_session() as session:
            result = await session.execute(
                delete(ChildModel).where(ChildModel.id == child_id),
            )
            await session.commit()
            return result.rowcount > 0

    async def create_conversation(
        self,
        child_id: str,
        parent_id: str,
        transcript: list[dict[str, str]],
    ) -> str:
        """Create a new conversation record."""
        async with self.database.get_session() as session:
            conversation_id = str(uuid4())
            conversation = ConversationModel(
                id=conversation_id,
                child_id=child_id,
                parent_id=parent_id,
                transcript=transcript,
                created_at=datetime.utcnow(),
            )
            session.add(conversation)
            await session.commit()
            return conversation_id

    async def get_conversations_by_child_id(
        self,
        child_id: str,
    ) -> list[dict[str, Any]]:
        """Retrieve conversation history for a child."""
        async with self.database.get_session() as session:
            result = await session.execute(
                select(ConversationModel)
                .filter(ConversationModel.child_id == child_id)
                .order_by(ConversationModel.created_at),
            )
            conversations = result.scalars().all()
            return [
                {
                    "id": conv.id,
                    "child_id": conv.child_id,
                    "parent_id": conv.parent_id,
                    "transcript": conv.transcript,
                    "created_at": (
                        conv.created_at.isoformat() if conv.created_at else None
                    ),
                }
                for conv in conversations
            ]

    async def init_db(self):
        """Initialize the database schema."""
        await self.database.init_db()

    async def close(self):
        """Close the database connection."""
        await self.database.close()
