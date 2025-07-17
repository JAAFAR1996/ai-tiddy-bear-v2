from domain.events.conversation_updated import ConversationUpdated
from domain.events.conversation_started import ConversationStarted
from domain.events.child_profile_updated import ChildProfileUpdated
from domain.events.child_registered import ChildRegistered
from domain.events.domain_events import DomainEvent
from uuid import uuid4
from datetime import datetime
from pathlib import Path
import sys


class MockConversationStarted:
    def __init__(
        self, conversation_id, child_id, initial_message, metadata=None
    ):
        self.conversation_id = conversation_id
        self.child_id = child_id
        self.initial_message = initial_message
        self.metadata = metadata or {}
        self.started_at = "2024-01-01T00:00:00Z"


ConversationStarted = MockConversationStarted


# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

"""Tests for domain events."""

try:
    import pytest
except ImportError:
    try:
        from common.mock_pytest import pytest
    except ImportError:
        pass

    # Mock pytest when not available
    class MockPytest:
        def fixture(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

        def mark(self):
            class MockMark:
                def parametrize(self, *args, **kwargs):
                    def decorator(func):
                        return func

                    return decorator

                def asyncio(self, func):
                    return func

                def slow(self, func):
                    return func

                def skip(self, reason=""):
                    def decorator(func):
                        return func

                    return decorator

            return MockMark()

        def raises(self, exception):
            class MockRaises:
                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    return False

            return MockRaises()

        def skip(self, reason=""):
            def decorator(func):
                return func

            return decorator

    pytest = MockPytest()


class TestDomainEvent:
    """Test base DomainEvent functionality."""

    def test_domain_event_creation(self):
        """Test creating a domain event."""
        aggregate_id = uuid4()
        event = DomainEvent(aggregate_id=aggregate_id)

        assert event.aggregate_id == aggregate_id
        assert isinstance(event.occurred_at, datetime)
        assert event.version == 1

    def test_domain_event_with_custom_version(self):
        """Test creating domain event with custom version."""
        aggregate_id = uuid4()
        event = DomainEvent(aggregate_id=aggregate_id, version=5)

        assert event.version == 5

    def test_domain_event_equality(self):
        """Test domain event equality."""
        aggregate_id = uuid4()
        event1 = DomainEvent(aggregate_id=aggregate_id)
        event2 = DomainEvent(aggregate_id=aggregate_id)

        # Different events even with same aggregate_id
        assert event1 != event2
        assert event1.aggregate_id == event2.aggregate_id

    def test_domain_event_string_representation(self):
        """Test domain event string representation."""
        aggregate_id = uuid4()
        event = DomainEvent(aggregate_id=aggregate_id)

        str_repr = str(event)
        assert "DomainEvent" in str_repr
        assert str(aggregate_id) in str_repr


class TestChildRegistered:
    """Test ChildRegistered event."""

    def test_child_registered_creation(self):
        """Test creating ChildRegistered event."""
        child_id = uuid4()
        name = "Alice"
        age = 7
        preferences = {"language": "en", "interests": ["animals"]}

        event = ChildRegistered.create(
            child_id=child_id, name=name, age=age, preferences=preferences
        )

        assert event.child_id == child_id
        assert event.name == name
        assert event.age == age
        assert event.preferences == preferences
        assert isinstance(event.timestamp, datetime)

    def test_child_registered_with_complex_preferences(self):
        """Test ChildRegistered with complex preferences."""
        child_id = uuid4()
        complex_preferences = {
            "language": "es",
            "interests": ["dinosaurs", "space", "music"],
            "learning_style": "visual",
            "difficulty_level": "intermediate",
            "favorite_characters": ["princess", "robot"],
            "voice_settings": {
                "speed": "normal",
                "pitch": "child-friendly",
                "accent": "neutral",
            },
        }

        event = ChildRegistered.create(
            child_id=child_id,
            name="María",
            age=8,
            preferences=complex_preferences,
        )

        assert event.preferences["language"] == "es"
        assert len(event.preferences["interests"]) == 3
        assert event.preferences["voice_settings"]["speed"] == "normal"

    def test_child_registered_minimal_data(self):
        """Test ChildRegistered with minimal required data."""
        child_id = uuid4()

        event = ChildRegistered.create(
            child_id=child_id, name="Bob", age=5, preferences={}
        )

        assert event.name == "Bob"
        assert event.age == 5
        assert event.preferences == {}

    def test_child_registered_string_representation(self):
        """Test ChildRegistered string representation."""
        child_id = uuid4()
        event = ChildRegistered.create(
            child_id=child_id,
            name="Test Child",
            age=6,
            preferences={"language": "en"},
        )

        str_repr = str(event)
        assert "ChildRegistered" in str_repr
        assert "Test Child" in str_repr
        assert "6" in str_repr


class TestChildProfileUpdated:
    """Test ChildProfileUpdated event."""

    def test_child_profile_updated_creation(self):
        """Test creating ChildProfileUpdated event."""
        child_id = uuid4()
        new_name = "Updated Name"
        new_age = 8
        new_preferences = {"language": "fr", "updated": True}

        event = ChildProfileUpdated.create(
            child_id=child_id,
            name=new_name,
            age=new_age,
            preferences=new_preferences,
        )

        assert event.child_id == child_id
        assert event.name == new_name
        assert event.age == new_age
        assert event.preferences == new_preferences

    def test_child_profile_updated_partial_update(self):
        """Test ChildProfileUpdated with partial updates."""
        child_id = uuid4()

        # Only update name
        event = ChildProfileUpdated.create(
            child_id=child_id, name="New Name", age=None, preferences=None
        )

        assert event.name == "New Name"
        assert event.age is None
        assert event.preferences is None

    def test_child_profile_updated_preferences_only(self):
        """Test updating only preferences."""
        child_id = uuid4()
        updated_preferences = {
            "interests": ["updated_interest"],
            "new_setting": "value",
        }

        event = ChildProfileUpdated.create(
            child_id=child_id,
            name=None,
            age=None,
            preferences=updated_preferences,
        )

        assert event.preferences == updated_preferences
        assert event.name is None
        assert event.age is None


class TestConversationStarted:
    """Test ConversationStarted event."""

    def test_conversation_started_creation(self):
        """Test creating ConversationStarted event."""
        conversation_id = uuid4()
        child_id = uuid4()
        initial_message = "Hello Teddy!"

        event = ConversationStarted(
            aggregate_id=conversation_id,
            conversation_id=conversation_id,
            child_id=child_id,
            initial_message=initial_message,
        )

        assert event.aggregate_id == conversation_id
        assert event.conversation_id == conversation_id
        assert event.child_id == child_id
        assert event.initial_message == initial_message
        assert isinstance(event.occurred_at, datetime)

    def test_conversation_started_with_long_message(self):
        """Test ConversationStarted with long initial message."""
        conversation_id = uuid4()
        child_id = uuid4()
        long_message = "This is a very long initial message that a child might say when they start talking to their teddy bear about many different things including their day at school and what they learned."

        event = ConversationStarted(
            aggregate_id=conversation_id,
            conversation_id=conversation_id,
            child_id=child_id,
            initial_message=long_message,
        )

        assert event.initial_message == long_message
        assert len(event.initial_message) > 100

    def test_conversation_started_empty_message(self):
        """Test ConversationStarted with empty message."""
        conversation_id = uuid4()
        child_id = uuid4()

        event = ConversationStarted(
            aggregate_id=conversation_id,
            conversation_id=conversation_id,
            child_id=child_id,
            initial_message="",
        )

        assert event.initial_message == ""


class TestConversationUpdated:
    """Test ConversationUpdated event."""

    def test_conversation_updated_creation(self):
        """Test creating ConversationUpdated event."""
        conversation_id = uuid4()
        emotion = "happy"
        sentiment = 0.8
        safety_score = 0.95

        event = ConversationUpdated(
            aggregate_id=conversation_id,
            conversation_id=conversation_id,
            emotion=emotion,
            sentiment=sentiment,
            safety_score=safety_score,
        )

        assert event.aggregate_id == conversation_id
        assert event.conversation_id == conversation_id
        assert event.emotion == emotion
        assert event.sentiment == sentiment
        assert event.safety_score == safety_score

    def test_conversation_updated_negative_emotion(self):
        """Test ConversationUpdated with negative emotion."""
        conversation_id = uuid4()

        event = ConversationUpdated(
            aggregate_id=conversation_id,
            conversation_id=conversation_id,
            emotion="sad",
            sentiment=-0.3,
            safety_score=0.9,
        )

        assert event.emotion == "sad"
        assert event.sentiment == -0.3
        assert event.safety_score == 0.9

    def test_conversation_updated_edge_case_scores(self):
        """Test ConversationUpdated with edge case scores."""
        conversation_id = uuid4()

        # Test maximum positive sentiment
        event = ConversationUpdated(
            aggregate_id=conversation_id,
            conversation_id=conversation_id,
            emotion="excited",
            sentiment=1.0,
            safety_score=1.0,
        )

        assert event.sentiment == 1.0
        assert event.safety_score == 1.0

    def test_conversation_updated_optional_fields(self):
        """Test ConversationUpdated with optional fields."""
        conversation_id = uuid4()

        event = ConversationUpdated(
            aggregate_id=conversation_id,
            conversation_id=conversation_id,
            emotion=None,
            sentiment=None,
            safety_score=None,
        )

        assert event.emotion is None
        assert event.sentiment is None
        assert event.safety_score is None

    def test_conversation_updated_string_representation(self):
        """Test ConversationUpdated string representation."""
        conversation_id = uuid4()
        event = ConversationUpdated(
            aggregate_id=conversation_id,
            conversation_id=conversation_id,
            emotion="curious",
            sentiment=0.6,
            safety_score=0.98,
        )

        str_repr = str(event)
        assert "ConversationUpdated" in str_repr
        assert "curious" in str_repr


class TestEventTimestamps:
    """Test event timestamp functionality."""

    def test_events_have_unique_timestamps(self):
        """Test that events created at different times have different timestamps."""
        import time

        child_id = uuid4()
        event1 = ChildRegistered(
            aggregate_id=child_id,
            child_id=child_id,
            name="Child 1",
            age=5,
            preferences={},
        )

        time.sleep(0.001)  # Small delay

        event2 = ChildRegistered(
            aggregate_id=child_id,
            child_id=child_id,
            name="Child 2",
            age=6,
            preferences={},
        )

        assert event1.occurred_at != event2.occurred_at
        assert event1.occurred_at < event2.occurred_at

    def test_event_timestamp_precision(self):
        """Test event timestamp precision."""
        child_id = uuid4()
        before = datetime.utcnow()

        event = ChildRegistered(
            aggregate_id=child_id,
            child_id=child_id,
            name="Test",
            age=5,
            preferences={},
        )

        after = datetime.utcnow()

        assert before <= event.occurred_at <= after


class TestEventVersioning:
    """Test event versioning functionality."""

    def test_default_version(self):
        """Test that events have default version 1."""
        child_id = uuid4()
        event = ChildRegistered(
            aggregate_id=child_id,
            child_id=child_id,
            name="Test",
            age=5,
            preferences={},
        )

        assert event.version == 1

    def test_custom_version(self):
        """Test events with custom versions."""
        child_id = uuid4()

        event_v1 = ChildRegistered(
            aggregate_id=child_id,
            child_id=child_id,
            name="Test",
            age=5,
            preferences={},
            version=1,
        )

        event_v2 = ChildProfileUpdated(
            aggregate_id=child_id,
            child_id=child_id,
            name="Updated Test",
            age=6,
            preferences={},
            version=2,
        )

        assert event_v1.version == 1
        assert event_v2.version == 2

    def test_version_ordering(self):
        """Test that versions can be used for ordering."""
        child_id = uuid4()

        events = [
            ChildRegistered(
                aggregate_id=child_id,
                child_id=child_id,
                name="Test",
                age=5,
                preferences={},
                version=3,
            ),
            ChildProfileUpdated(
                aggregate_id=child_id,
                child_id=child_id,
                name="Test",
                age=5,
                preferences={},
                version=1,
            ),
            ConversationStarted(
                aggregate_id=uuid4(),
                conversation_id=uuid4(),
                child_id=child_id,
                initial_message="Hi",
                version=2,
            ),
        ]

        sorted_events = sorted(events, key=lambda e: e.version)

        assert sorted_events[0].version == 1
        assert sorted_events[1].version == 2
        assert sorted_events[2].version == 3
