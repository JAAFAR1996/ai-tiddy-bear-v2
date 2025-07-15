import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from src.domain.entities.conversation import (
    ContentType,
    Conversation,
    EmotionalState,
    InteractionType,
    Message,
    MessageRole,
)
from src.infrastructure.persistence.conversation_sqlite_repository import (
    ConversationSQLiteRepository,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture
def mock_session_factory():
    """Mock session factory for testing"""
    return Mock()


@pytest.fixture
def conversation_repository(temp_db, mock_session_factory):
    """Create a Conversation repository instance for testing"""
    repo = ConversationSQLiteRepository(mock_session_factory, temp_db)
    return repo


@pytest.fixture
def sample_conversation_data():
    """Sample conversation data for testing"""
    return {
        "id": "test-conv-001",
        "session_id": "session-123",
        "child_id": "child-456",
        "parent_id": "parent-789",
        "start_time": datetime.now() - timedelta(minutes=30),
        "end_time": datetime.now() - timedelta(minutes=15),
        "duration_seconds": 900,  # 15 minutes
        "interaction_type": InteractionType.LEARNING,
        "topics": ["math", "science", "problem_solving"],
        "primary_language": "en",
        "quality_score": 0.85,
        "safety_score": 1.0,
        "educational_score": 0.9,
        "engagement_score": 0.8,
        "llm_provider": "openai",
        "model_version": "gpt-4",
        "context_summary": "Educational conversation about basic math and science concepts",
        "metadata": {"user_agent": "TeddyBear/1.0", "ip_address": "192.168.1.1"},
        "total_messages": 12,
        "child_messages": 6,
        "assistant_messages": 6,
        "questions_asked": 3,
        "moderation_flags": 0,
        "parent_visible": True,
        "archived": False,
    }


@pytest.fixture
def sample_messages():
    """Sample messages for testing"""
    return [
        Message(
            id="msg-001",
            role=MessageRole.USER,
            content="Hi, can you help me with math?",
            content_type=ContentType.TEXT,
            sequence_number=0,
            timestamp=datetime.now() - timedelta(minutes=29),
            metadata={"input_method": "voice"},
        ),
        Message(
            id="msg-002",
            role=MessageRole.ASSISTANT,
            content="Of course! I'd love to help you with math. What would you like to learn about?",
            content_type=ContentType.TEXT,
            sequence_number=1,
            timestamp=datetime.now() - timedelta(minutes=28),
            sentiment_score=0.8,
            confidence_score=0.95,
        ),
        Message(
            id="msg-003",
            role=MessageRole.USER,
            content="I want to learn about addition",
            content_type=ContentType.TEXT,
            sequence_number=2,
            timestamp=datetime.now() - timedelta(minutes=27),
            metadata={"topic_detected": "addition"},
        ),
    ]


@pytest.fixture
def sample_emotional_states():
    """Sample emotional states for testing"""
    return [
        EmotionalState(
            id="emotion-001",
            primary_emotion="curious",
            confidence=0.85,
            secondary_emotions=[{"emotion": "excited", "confidence": 0.6}],
            arousal_level=0.6,
            valence_level=0.8,
            emotional_context="Child showing interest in learning",
            analysis_method="hume",
        ),
        EmotionalState(
            id="emotion-002",
            primary_emotion="happy",
            confidence=0.9,
            secondary_emotions=[{"emotion": "confident", "confidence": 0.7}],
            arousal_level=0.7,
            valence_level=0.9,
            emotional_context="Child excited about solving problems",
            analysis_method="hume",
        ),
    ]


@pytest.fixture
def sample_conversation(
    sample_conversation_data, sample_messages, sample_emotional_states
):
    """Create a sample Conversation entity"""
    conversation = Conversation(**sample_conversation_data)
    conversation.messages = sample_messages
    conversation.emotional_states = sample_emotional_states

    # Link messages and emotional states to conversation
    for msg in conversation.messages:
        msg.conversation_id = conversation.id
    for state in conversation.emotional_states:
        state.conversation_id = conversation.id

    return conversation
