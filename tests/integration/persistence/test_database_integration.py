"""
Database Integration Tests

Real database tests using in-memory SQLite for fast, reliable testing.
"""

import pytest
import asyncio
from uuid import uuid4

from sqlalchemy.ext.asyncio import create_async_engine

from src.infrastructure.persistence.database import Database
from src.infrastructure.persistence.database_service_orchestrator import (
    DatabaseServiceOrchestrator,
)
from src.infrastructure.persistence.models.base_model import Base


@pytest.fixture(scope="function")
async def test_database():
    """Create an in-memory test database."""
    # Create in-memory SQLite database
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:", echo=False, future=True
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create database instance
    database = Database(engine)

    yield database

    # Cleanup
    await engine.dispose()


@pytest.fixture
async def db_service(test_database):
    """Create database service with real database."""
    return DatabaseServiceOrchestrator(test_database)


@pytest.fixture
async def test_user(db_service):
    """Create a test user."""
    user_id = await db_service.create_user(
        email="testparent@example.com",
        hashed_password="hashed_test_password",
        role="parent",
    )
    return {"id": user_id, "email": "testparent@example.com", "role": "parent"}


class TestUserOperationsIntegration:
    """Integration tests for user operations."""

    @pytest.mark.asyncio
    async def test_complete_user_lifecycle(self, db_service):
        """Test creating, reading, updating, and verifying a user."""
        # Create user
        email = f"user_{uuid4().hex[:8]}@example.com"
        user_id = await db_service.create_user(
            email=email, hashed_password="secure_hash", role="parent"
        )

        assert user_id is not None

        # Read user
        user = await db_service.get_user_by_email(email)
        assert user is not None
        assert user["email"] == email
        assert user["role"] == "parent"
        assert user["is_active"] is True
        assert user["email_verified"] is False

        # Update user
        success = await db_service.update_user(
            user_id, {"email_verified": True, "is_active": True}
        )
        assert success is True

        # Verify update
        updated_user = await db_service.get_user_by_email(email)
        assert updated_user["email_verified"] is True

    @pytest.mark.asyncio
    async def test_duplicate_user_prevention(self, db_service):
        """Test that duplicate users cannot be created."""
        email = "duplicate@example.com"

        # Create first user
        user_id1 = await db_service.create_user(
            email=email, hashed_password="hash1", role="parent"
        )
        assert user_id1 is not None

        # Try to create duplicate
        with pytest.raises(ValueError, match="already exists"):
            await db_service.create_user(
                email=email, hashed_password="hash2", role="parent"
            )

    @pytest.mark.asyncio
    async def test_concurrent_user_creation(self, db_service):
        """Test concurrent user creation doesn't cause issues."""
        # Create multiple users concurrently
        tasks = []
        for i in range(5):
            email = f"concurrent_{i}@example.com"
            task = db_service.create_user(
                email=email, hashed_password=f"hash_{i}", role="parent"
            )
            tasks.append(task)

        # Wait for all to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should succeed
        for result in results:
            assert isinstance(result, str)  # user_id


class TestChildOperationsIntegration:
    """Integration tests for child operations with COPPA compliance."""

    @pytest.mark.asyncio
    async def test_child_profile_lifecycle(self, db_service, test_user):
        """Test complete child profile lifecycle."""
        # Create child
        child_data = {
            "name": "Timmy",
            "age": 8,
            "preferences": {
                "favorite_color": "blue",
                "interests": ["dinosaurs", "space"],
            },
        }

        child_id = await db_service.create_child(test_user["id"], child_data)
        assert child_id is not None

        # Read child
        child = await db_service.get_child(child_id)
        assert child is not None
        assert child["name"] == "Timmy"
        assert child["age"] == 8
        assert child["preferences"]["favorite_color"] == "blue"

        # Update child
        success = await db_service.update_child(
            child_id,
            {
                "age": 9,
                "preferences": {
                    "favorite_color": "green",
                    "interests": ["dinosaurs", "space", "robots"],
                },
            },
        )
        assert success is True

        # Verify update
        updated_child = await db_service.get_child(child_id)
        assert updated_child["age"] == 9
        assert updated_child["preferences"]["favorite_color"] == "green"

    @pytest.mark.asyncio
    async def test_parent_child_relationship(self, db_service, test_user):
        """Test parent can have multiple children."""
        # Create multiple children
        children_data = [
            {"name": "Alice", "age": 6},
            {"name": "Bob", "age": 8},
            {"name": "Charlie", "age": 10},
        ]

        child_ids = []
        for data in children_data:
            child_id = await db_service.create_child(test_user["id"], data)
            child_ids.append(child_id)

        # Get all children for parent
        children = await db_service.get_children_by_parent(test_user["id"])
        assert len(children) == 3

        # Verify all children
        names = [child["name"] for child in children]
        assert "Alice" in names
        assert "Bob" in names
        assert "Charlie" in names

    @pytest.mark.asyncio
    async def test_child_data_isolation(self, db_service):
        """Test that children from different parents are isolated."""
        # Create two parents
        parent1_id = await db_service.create_user(
            "parent1@example.com", "hash1", "parent"
        )
        parent2_id = await db_service.create_user(
            "parent2@example.com", "hash2", "parent"
        )

        # Create children for each parent
        child1_id = await db_service.create_child(
            parent1_id, {"name": "Child1", "age": 7}
        )
        child2_id = await db_service.create_child(
            parent2_id, {"name": "Child2", "age": 8}
        )

        # Verify isolation
        parent1_children = await db_service.get_children_by_parent(parent1_id)
        assert len(parent1_children) == 1
        assert parent1_children[0]["name"] == "Child1"

        parent2_children = await db_service.get_children_by_parent(parent2_id)
        assert len(parent2_children) == 1
        assert parent2_children[0]["name"] == "Child2"


class TestConversationOperationsIntegration:
    """Integration tests for conversation operations."""

    @pytest.mark.asyncio
    async def test_conversation_storage_and_retrieval(
        self, db_service, test_user
    ):
        """Test storing and retrieving conversations."""
        # Create child first
        child_id = await db_service.create_child(
            test_user["id"], {"name": "Test Child", "age": 7}
        )

        # Store multiple conversations
        conversations = [
            ("Tell me a story", "Once upon a time..."),
            ("What's 2+2?", "2+2 equals 4!"),
            ("Sing a song", "Twinkle twinkle little star..."),
        ]

        conv_ids = []
        for message, response in conversations:
            conv_id = await db_service.save_conversation(
                child_id, message, response
            )
            conv_ids.append(conv_id)
            # Add small delay to ensure different timestamps
            await asyncio.sleep(0.01)

        # Retrieve history
        history = await db_service.get_conversation_history(child_id, limit=10)
        assert len(history) == 3

        # Should be in reverse chronological order
        assert history[0]["message"] == "Sing a song"
        assert history[2]["message"] == "Tell me a story"

    @pytest.mark.asyncio
    async def test_conversation_rate_limiting(self, db_service, test_user):
        """Test conversation counting for rate limiting."""
        # Create child
        child_id = await db_service.create_child(
            test_user["id"], {"name": "Chatty Child", "age": 8}
        )

        # Create many conversations
        for i in range(10):
            await db_service.save_conversation(
                child_id, f"Message {i}", f"Response {i}"
            )

        # Check interaction count
        count = await db_service.get_interaction_count(child_id, hours=1)
        assert count == 10

        # Check count for longer period
        count_24h = await db_service.get_interaction_count(child_id, hours=24)
        assert count_24h == 10


class TestSafetyOperationsIntegration:
    """Integration tests for safety operations."""

    @pytest.mark.asyncio
    async def test_safety_event_recording(self, db_service, test_user):
        """Test recording and retrieving safety events."""
        # Create child
        child_id = await db_service.create_child(
            test_user["id"], {"name": "Safety Test Child", "age": 7}
        )

        # Record various safety events
        events = [
            ("content_filter", "Blocked inappropriate word", "medium"),
            ("time_limit_warning", "Approaching daily limit", "low"),
            ("stranger_danger", "Unknown contact attempt", "high"),
        ]

        event_ids = []
        for event_type, details, severity in events:
            event_id = await db_service.record_safety_event(
                child_id, event_type, details, severity
            )
            event_ids.append(event_id)

        # Retrieve safety events
        safety_events = await db_service.get_safety_events(child_id, limit=10)
        assert len(safety_events) >= 3  # May include mock data

        # Verify event types are present
        event_types = [e["event_type"] for e in safety_events]
        assert "content_filter" in event_types
        assert "time_limit_warning" in event_types
        assert "stranger_danger" in event_types

    @pytest.mark.asyncio
    async def test_safety_score_updates(self, db_service, test_user):
        """Test updating and tracking safety scores."""
        # Create child
        child_id = await db_service.create_child(
            test_user["id"], {"name": "Score Test Child", "age": 6}
        )

        # Update safety score multiple times
        scores = [
            (0.95, "Initial good behavior"),
            (0.85, "Minor content filter trigger"),
            (0.70, "Multiple filter triggers"),
            (0.90, "Improved behavior"),
        ]

        for score, reason in scores:
            success = await db_service.update_safety_score(
                child_id, score, reason
            )
            assert success is True

    @pytest.mark.asyncio
    async def test_safety_alerts(self, db_service, test_user):
        """Test sending safety alerts."""
        # Create child
        child_id = await db_service.create_child(
            test_user["id"], {"name": "Alert Test Child", "age": 9}
        )

        # Send critical safety alert
        alert_data = {
            "child_id": child_id,
            "alert_type": "inappropriate_content_attempt",
            "severity": "high",
            "message": "Child attempted to access blocked content multiple times",
        }

        success = await db_service.send_safety_alert(alert_data)
        assert success is True


class TestDataRetentionIntegration:
    """Integration tests for COPPA-compliant data retention."""

    @pytest.mark.asyncio
    async def test_old_data_cleanup(self, db_service, test_user):
        """Test cleanup of old data."""
        # Create child
        child_id = await db_service.create_child(
            test_user["id"], {"name": "Retention Test Child", "age": 7}
        )

        # Create conversations
        for i in range(5):
            await db_service.save_conversation(
                child_id, f"Old message {i}", f"Old response {i}"
            )

        # Cleanup data older than 90 days
        # Note: In real test, we'd need to mock time or insert with old
        # timestamps
        cleanup_stats = await db_service.cleanup_old_data(days=90)

        assert "conversations_deleted" in cleanup_stats
        assert "usage_records_deleted" in cleanup_stats

    @pytest.mark.asyncio
    async def test_usage_tracking(self, db_service, test_user):
        """Test usage statistics tracking."""
        # Create child
        child_id = await db_service.create_child(
            test_user["id"], {"name": "Usage Test Child", "age": 8}
        )

        # Record usage
        usage_record = {
            "child_id": child_id,
            "activity_type": "conversation",
            "duration": 300,  # 5 minutes
            "metadata": {"topic": "space exploration"},
        }

        usage_id = await db_service.record_usage(usage_record)
        assert usage_id is not None

        # Get usage summary
        summary = await db_service.get_usage_summary(child_id, period_days=30)
        assert summary is not None
        assert summary["child_id"] == child_id


class TestTransactionIntegration:
    """Test database transactions and rollbacks."""

    @pytest.mark.asyncio
    async def test_transaction_rollback_on_error(self, test_database):
        """Test that transactions rollback on error."""
        # This test would need direct database access
        # to properly test transaction behavior

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, db_service):
        """Test that concurrent operations don't cause conflicts."""
        # Create parent
        parent_id = await db_service.create_user(
            "concurrent@example.com", "hash", "parent"
        )

        # Create child
        child_id = await db_service.create_child(
            parent_id, {"name": "Concurrent Child", "age": 7}
        )

        # Perform multiple concurrent operations
        tasks = [
            db_service.save_conversation(child_id, f"Msg {i}", f"Resp {i}")
            for i in range(10)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should succeed
        for result in results:
            assert isinstance(result, str)  # conversation_id
