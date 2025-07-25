import asyncio
import hashlib
import json
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet

from src.infrastructure.validators.security.path_validator import (
    get_secure_file_operations,
)

"""Production - ready SQLite conversation repository with COPPA compliance"""

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="persistence")


class ConversationSQLiteRepository:
    """Production - grade conversation repository with comprehensive safety and privacy controls.
    Implements COPPA - compliant data handling with encryption and automatic cleanup.
    """

    def __init__(self, db_path: str = "conversations.db") -> None:
        self.db_path = Path(db_path)
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        self.max_conversation_age_days = 90  # COPPA compliance
        self.max_conversations_per_child = 1000  # Safety limit
        self._init_database()

    def _get_or_create_encryption_key(self) -> bytes:
        secure_ops = get_secure_file_operations()
        key_filename = "conversation_key.key"
        try:
            if secure_ops.safe_exists(key_filename):
                with secure_ops.safe_open(key_filename, "rb") as f:
                    return f.read()
        except Exception as e:
            logger.warning(f"Failed to read encryption key: {e}")
        # Generate new key
        key = Fernet.generate_key()
        try:
            with secure_ops.safe_open(key_filename, "wb") as f:
                f.write(key)
            # Set secure permissions
            key_file = secure_ops.validator.get_safe_path(key_filename)
            if key_file:
                os.chmod(key_file, 0o600)
        except Exception as e:
            logger.warning(f"Failed to save encryption key: {e}")
        return key

    def _init_database(self):
        """Initialize database with proper schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        child_id TEXT NOT NULL,
                        conversation_hash TEXT UNIQUE NOT NULL,
                        encrypted_content BLOB NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        safety_score REAL DEFAULT 1.0,
                        parent_approved BOOLEAN DEFAULT FALSE,
                        expires_at DATETIME NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )
                # Index for performance and COPPA compliance
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_child_timestamp ON conversations(child_id, timestamp)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_expires_at ON conversations(expires_at)"
                )
                # Trigger for automatic cleanup
                conn.execute(
                    """
                    CREATE TRIGGER IF NOT EXISTS cleanup_expired_conversations
                    AFTER INSERT ON conversations
                    BEGIN
                        DELETE FROM conversations WHERE expires_at < datetime('now');
                    END
                """
                )
                conn.commit()
                logger.info("Conversation database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize conversation database: {e}")
            raise RuntimeError(f"Database initialization failed: {e}")

    async def save_conversation(
        self, conversation_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Save conversation with comprehensive validation and encryption.

        Args:
            conversation_data: Dictionary containing conversation details
        Returns:
            Dict with save status and conversation ID
        Raises:
            ValueError: If conversation data is invalid
            RuntimeError: If save operation fails
        """
        # Input validation
        if not conversation_data or not isinstance(conversation_data, dict):
            raise ValueError("Valid conversation data required")
        required_fields = ["child_id", "message", "response"]
        for field in required_fields:
            if field not in conversation_data:
                raise ValueError(f"Missing required field: {field}")
        child_id = conversation_data["child_id"]
        # Validate child_id format
        if not child_id or len(child_id) < 8 or not child_id.replace("-", "").isalnum():
            raise ValueError("Invalid child_id format")

        # Safety checks
        await self._validate_conversation_safety(conversation_data)

        # Check conversation limit for child
        current_count = await self._get_conversation_count(child_id)
        if current_count >= self.max_conversations_per_child:
            logger.warning(f"Conversation limit reached for child {child_id}")
            await self._cleanup_old_conversations(child_id, keep_latest=500)

        # Prepare conversation for storage
        conversation_hash = self._generate_conversation_hash(conversation_data)
        encrypted_content = self.cipher.encrypt(json.dumps(conversation_data).encode())
        expires_at = datetime.utcnow() + timedelta(days=self.max_conversation_age_days)

        try:

            def _save_to_db():
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        """
                        INSERT OR REPLACE INTO conversations
                        (child_id, conversation_hash, encrypted_content, safety_score, expires_at)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (
                            child_id,
                            conversation_hash,
                            encrypted_content,
                            conversation_data.get("safety_score", 1.0),
                            expires_at.isoformat(),
                        ),
                    )
                    return cursor.lastrowid

            # Run database operation in thread pool to maintain async compatibility
            loop = asyncio.get_event_loop()
            conversation_id = await loop.run_in_executor(None, _save_to_db)
            logger.info(
                f"Conversation saved successfully for child {child_id}: ID {conversation_id}"
            )
            return {
                "success": True,
                "conversation_id": conversation_id,
                "child_id": child_id,
                "hash": conversation_hash,
                "expires_at": expires_at.isoformat(),
                "saved_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to save conversation for child {child_id}: {e}")
            raise RuntimeError(f"Conversation save failed: {e}")

    async def get_conversations(
        self, child_id: str, limit: int = 50, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Get conversations for a child with decryption and safety filtering."""
        if not child_id or limit <= 0 or limit > 100:
            raise ValueError("Invalid parameters")

        def _get_from_db():
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT id, conversation_hash, encrypted_content, timestamp, safety_score, parent_approved
                    FROM conversations
                    WHERE child_id = ? AND expires_at > datetime('now')
                    ORDER BY timestamp DESC
                    LIMIT ? OFFSET ?
                """,
                    (child_id, limit, offset),
                )
                return cursor.fetchall()

        try:
            loop = asyncio.get_event_loop()
            rows = await loop.run_in_executor(None, _get_from_db)
            conversations = []
            for row in rows:
                try:
                    # Decrypt conversation content
                    decrypted_data = json.loads(
                        self.cipher.decrypt(row["encrypted_content"]).decode()
                    )
                    conversations.append(
                        {
                            "id": row["id"],
                            "hash": row["conversation_hash"],
                            "content": decrypted_data,
                            "timestamp": row["timestamp"],
                            "safety_score": row["safety_score"],
                            "parent_approved": bool(row["parent_approved"]),
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to decrypt conversation {row['id']}: {e}")
                    continue
            return conversations
        except Exception as e:
            logger.error(f"Failed to retrieve conversations for child {child_id}: {e}")
            raise RuntimeError(f"Conversation retrieval failed: {e}")

    async def delete_child_conversations(self, child_id: str) -> dict[str, Any]:
        """Delete all conversations for a child (COPPA right to deletion)."""
        if not child_id:
            raise ValueError("Valid child_id required")

        def _delete_from_db():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "DELETE FROM conversations WHERE child_id = ?", (child_id,)
                )
                return cursor.rowcount

        try:
            loop = asyncio.get_event_loop()
            deleted_count = await loop.run_in_executor(None, _delete_from_db)
            logger.info(f"Deleted {deleted_count} conversations for child {child_id}")
            return {
                "success": True,
                "child_id": child_id,
                "deleted_count": deleted_count,
                "deleted_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to delete conversations for child {child_id}: {e}")
            raise RuntimeError(f"Conversation deletion failed: {e}")

    async def _validate_conversation_safety(self, conversation_data: dict[str, Any]):
        """Validate conversation content for child safety."""
        message = conversation_data.get("message", "")
        response = conversation_data.get("response", "")

        # Basic safety checks
        unsafe_patterns = [
            "personal information",
            "address",
            "phone number",
            "meet me",
            "where do you live",
            "send photo",
            "password",
            "secret",
        ]
        for pattern in unsafe_patterns:
            if (
                pattern.lower() in message.lower()
                or pattern.lower() in response.lower()
            ):
                raise ValueError(f"Unsafe content detected: {pattern}")

        # Length validation
        if len(message) > 1000 or len(response) > 2000:
            raise ValueError("Message or response too long")

    def _generate_conversation_hash(self, conversation_data: dict[str, Any]) -> str:
        """Generate unique hash for conversation to prevent duplicates."""
        content = f"{conversation_data['child_id']}{conversation_data['message']}{conversation_data['response']}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    async def _get_conversation_count(self, child_id: str) -> int:
        """Get current conversation count for a child."""

        def _count_from_db():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM conversations WHERE child_id = ? AND expires_at > datetime('now')",
                    (child_id,),
                )
                return cursor.fetchone()[0]

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _count_from_db)

    async def _cleanup_old_conversations(self, child_id: str, keep_latest: int = 500):
        """Clean up old conversations to maintain performance."""

        def _cleanup_from_db():
            with sqlite3.connect(self.db_path) as conn:
                # Keep only the latest N conversations for the child
                conn.execute(
                    """
                    DELETE FROM conversations
                    WHERE child_id = ? AND id NOT IN (
                        SELECT id FROM conversations
                        WHERE child_id = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    )
                """,
                    (child_id, child_id, keep_latest),
                )
                return conn.total_changes

        loop = asyncio.get_event_loop()
        deleted_count = await loop.run_in_executor(None, _cleanup_from_db)
        logger.info(
            f"Cleaned up {deleted_count} old conversations for child {child_id}"
        )
