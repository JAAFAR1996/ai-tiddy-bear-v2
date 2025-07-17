"""
Tests for Response Generator
Testing contextual response generation and activity type determination.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from dataclasses import dataclass

from src.application.services.response_generator import (
    ResponseGenerator,
    ActivityType,
    ResponseContext,
)
from src.application.services.session_manager import SessionData


class TestResponseGenerator:
    """Test the Response Generator."""

    @pytest.fixture
    def mock_ai_service(self):
        """Create a mock AI service."""
        ai_service = Mock()
        ai_service.determine_activity_type = AsyncMock()
        ai_service.generate_response = AsyncMock()
        return ai_service

    @pytest.fixture
    def mock_session(self):
        """Create a mock session data."""
        return SessionData(
            child_id="child_123",
            session_id="session_456",
            data={
                "child_preferences": {
                    "favorite_color": "blue",
                    "interests": ["animals", "space"],
                }
            },
        )

    @pytest.fixture
    def generator_with_ai(self, mock_ai_service):
        """Create a response generator with AI service."""
        return ResponseGenerator(ai_service=mock_ai_service)

    @pytest.fixture
    def generator_without_ai(self):
        """Create a response generator without AI service."""
        return ResponseGenerator()

    def test_initialization_with_ai_service(self, mock_ai_service):
        """Test initialization with AI service."""
        generator = ResponseGenerator(ai_service=mock_ai_service)

        assert generator.ai_service == mock_ai_service
        assert generator.logger is not None

    def test_initialization_without_ai_service(self):
        """Test initialization without AI service."""
        generator = ResponseGenerator()

        assert generator.ai_service is None
        assert generator.logger is not None

    def test_activity_type_enum(self):
        """Test ActivityType enum values."""
        assert ActivityType.STORY == "story"
        assert ActivityType.GAME == "game"
        assert ActivityType.LEARNING == "learning"
        assert ActivityType.SLEEP_ROUTINE == "sleep_routine"
        assert ActivityType.CONVERSATION == "conversation"
        assert ActivityType.COMFORT == "comfort"

    def test_response_context_dataclass(self):
        """Test ResponseContext dataclass."""
        context = ResponseContext(
            text="Test response", activity_type=ActivityType.STORY, emotion="happy"
        )

        assert context.text == "Test response"
        assert context.activity_type == ActivityType.STORY
        assert context.emotion == "happy"

    @pytest.mark.asyncio
    async def test_determine_activity_type_with_ai_success(
        self, generator_with_ai, mock_ai_service, mock_session
    ):
        """Test activity type determination with AI service success."""
        # Arrange
        text = "Tell me a story about dragons"
        emotion = {"sentiment": "joy", "score": 0.8}
        mock_ai_service.determine_activity_type.return_value = "STORY"

        # Act
        result = await generator_with_ai.determine_activity_type(
            text, emotion, mock_session
        )

        # Assert
        assert result == ActivityType.STORY
        mock_ai_service.determine_activity_type.assert_called_once_with(
            text, emotion, mock_session.__dict__
        )

    @pytest.mark.asyncio
    async def test_determine_activity_type_with_ai_error(
        self, generator_with_ai, mock_ai_service, mock_session
    ):
        """Test activity type determination with AI service error."""
        # Arrange
        text = "Let's play a game"
        emotion = {"sentiment": "excited", "score": 0.9}
        mock_ai_service.determine_activity_type.side_effect = Exception(
            "AI service error"
        )

        with patch.object(generator_with_ai, "logger") as mock_logger:
            # Act
            result = await generator_with_ai.determine_activity_type(
                text, emotion, mock_session
            )

            # Assert
            assert result == ActivityType.CONVERSATION  # Fallback
            mock_logger.error.assert_called_once()
            error_msg = mock_logger.error.call_args[0][0]
            assert "Error determining activity type" in error_msg

    @pytest.mark.asyncio
    async def test_determine_activity_type_without_ai(
        self, generator_without_ai, mock_session
    ):
        """Test activity type determination without AI service."""
        # Arrange
        text = "What's 2 + 2?"
        emotion = {"sentiment": "curious", "score": 0.7}

        # Act
        result = await generator_without_ai.determine_activity_type(
            text, emotion, mock_session
        )

        # Assert
        assert result == ActivityType.CONVERSATION  # Default fallback

    @pytest.mark.asyncio
    async def test_generate_contextual_response_with_ai_success(
        self, generator_with_ai, mock_ai_service, mock_session
    ):
        """Test contextual response generation with AI service success."""
        # Arrange
        text = "I'm feeling sad"
        emotion = {"sentiment": "sadness", "score": 0.6}
        mock_ai_service.generate_response.return_value = (
            "I'm here to help you feel better. Would you like to talk about it?"
        )
        mock_ai_service.determine_activity_type.return_value = "COMFORT"

        # Act
        result = await generator_with_ai.generate_contextual_response(
            text, emotion, mock_session
        )

        # Assert
        assert isinstance(result, ResponseContext)
        assert "I'm here to help you feel better" in result.text
        assert result.activity_type == ActivityType.COMFORT
        assert result.emotion == "sadness"

        # Verify AI service calls
        mock_ai_service.generate_response.assert_called_once_with(
            child_id=mock_session.child_id,
            conversation_history=[],
            current_input=text,
            child_preferences=mock_session.data.get("child_preferences", None),
        )

    @pytest.mark.asyncio
    async def test_generate_contextual_response_with_ai_error(
        self, generator_with_ai, mock_ai_service, mock_session
    ):
        """Test contextual response generation with AI service error."""
        # Arrange
        text = "How are you?"
        emotion = {"sentiment": "neutral", "score": 0.5}
        mock_ai_service.generate_response.side_effect = Exception(
            "AI generation error")

        with patch.object(generator_with_ai, "logger") as mock_logger:
            # Act
            result = await generator_with_ai.generate_contextual_response(
                text, emotion, mock_session
            )

            # Assert
            assert isinstance(result, ResponseContext)
            assert (
                "I'm sorry, I couldn't generate a personalized response" in result.text
            )
            assert result.activity_type == ActivityType.CONVERSATION
            assert result.emotion == "neutral"

            # Verify logging
            mock_logger.error.assert_called()
            mock_logger.warning.assert_called()
            warning_msg = mock_logger.warning.call_args[0][0]
            assert "Falling back to generic response" in warning_msg

    @pytest.mark.asyncio
    async def test_generate_contextual_response_without_ai(
        self, generator_without_ai, mock_session
    ):
        """Test contextual response generation without AI service."""
        # Arrange
        text = "Hello there!"
        emotion = {"sentiment": "joy", "score": 0.8}

        with patch.object(generator_without_ai, "logger") as mock_logger:
            # Act
            result = await generator_without_ai.generate_contextual_response(
                text, emotion, mock_session
            )

            # Assert
            assert isinstance(result, ResponseContext)
            assert (
                "I'm sorry, I couldn't generate a personalized response" in result.text
            )
            assert result.activity_type == ActivityType.CONVERSATION
            assert result.emotion == "neutral"

            # Verify warning logged
            mock_logger.warning.assert_called_once()
            warning_msg = mock_logger.warning.call_args[0][0]
            assert "Falling back to generic response" in warning_msg

    @pytest.mark.asyncio
    async def test_activity_type_all_values(
        self, generator_with_ai, mock_ai_service, mock_session
    ):
        """Test that all ActivityType values can be determined."""
        text = "test input"
        emotion = {"sentiment": "neutral", "score": 0.5}

        activity_types = [
            "STORY",
            "GAME",
            "LEARNING",
            "SLEEP_ROUTINE",
            "CONVERSATION",
            "COMFORT",
        ]

        for activity_str in activity_types:
            mock_ai_service.determine_activity_type.return_value = activity_str

            result = await generator_with_ai.determine_activity_type(
                text, emotion, mock_session
            )

            expected_activity = ActivityType[activity_str]
            assert result == expected_activity

    @pytest.mark.asyncio
    async def test_emotion_extraction_from_context(
        self, generator_with_ai, mock_ai_service, mock_session
    ):
        """Test emotion extraction from different emotion formats."""
        text = "test"
        mock_ai_service.generate_response.return_value = "Generated response"
        mock_ai_service.determine_activity_type.return_value = "CONVERSATION"

        emotion_formats = [
            {"sentiment": "joy", "score": 0.8},
            {"sentiment": "fear", "confidence": 0.7},
            {"emotion": "anger", "intensity": 0.6},
            {},  # Empty emotion
            {"unknown_key": "unknown_value"},
        ]

        for emotion in emotion_formats:
            result = await generator_with_ai.generate_contextual_response(
                text, emotion, mock_session
            )

            expected_emotion = emotion.get("sentiment", "neutral")
            assert result.emotion == expected_emotion

    @pytest.mark.asyncio
    async def test_session_data_handling(
            self, generator_with_ai, mock_ai_service):
        """Test proper handling of session data."""
        text = "test input"
        emotion = {"sentiment": "happy", "score": 0.9}

        # Test with different session data formats
        session_variations = [
            SessionData(child_id="child_1", session_id="session_1", data={}),
            SessionData(
                child_id="child_2",
                session_id="session_2",
                data={"child_preferences": {"theme": "animals"}},
            ),
            SessionData(
                child_id="child_3",
                session_id="session_3",
                data={"custom_field": "value"},
            ),
        ]

        mock_ai_service.generate_response.return_value = "Response"
        mock_ai_service.determine_activity_type.return_value = "CONVERSATION"

        for session in session_variations:
            result = await generator_with_ai.generate_contextual_response(
                text, emotion, session
            )

            assert isinstance(result, ResponseContext)
            assert result.text == "Response"

            # Verify session data was passed correctly
            call_args = mock_ai_service.generate_response.call_args
            assert call_args[1]["child_id"] == session.child_id
            assert call_args[1]["child_preferences"] == session.data.get(
                "child_preferences", None
            )

    @pytest.mark.asyncio
    async def test_concurrent_response_generation(
        self, generator_with_ai, mock_ai_service, mock_session
    ):
        """Test concurrent response generation."""
        import asyncio

        inputs = [
            ("Tell me a story", {"sentiment": "excited", "score": 0.9}),
            ("Let's play a game", {"sentiment": "happy", "score": 0.8}),
            ("What is math?", {"sentiment": "curious", "score": 0.7}),
        ]

        # Mock responses
        mock_ai_service.generate_response.side_effect = [
            "Here's a wonderful story...",
            "Let's play together!",
            "Math is about numbers...",
        ]
        mock_ai_service.determine_activity_type.side_effect = [
            "STORY",
            "GAME",
            "LEARNING",
        ]

        # Generate responses concurrently
        tasks = [
            generator_with_ai.generate_contextual_response(
                text, emotion, mock_session)
            for text, emotion in inputs
        ]

        results = await asyncio.gather(*tasks)

        # Verify all responses
        assert len(results) == 3
        assert all(isinstance(r, ResponseContext) for r in results)

        expected_activities = [
            ActivityType.STORY,
            ActivityType.GAME,
            ActivityType.LEARNING,
        ]
        for i, result in enumerate(results):
            assert result.activity_type == expected_activities[i]

    @pytest.mark.asyncio
    async def test_logging_behavior(
        self, generator_with_ai, mock_ai_service, mock_session
    ):
        """Test logging behavior in different scenarios."""
        text = "test message"
        emotion = {"sentiment": "neutral", "score": 0.5}
        mock_ai_service.generate_response.return_value = (
            "AI generated response text here"
        )
        mock_ai_service.determine_activity_type.return_value = "CONVERSATION"

        with patch.object(generator_with_ai, "logger") as mock_logger:
            await generator_with_ai.generate_contextual_response(
                text, emotion, mock_session
            )

            # Should log successful AI response generation
            mock_logger.info.assert_called_once()
            info_msg = mock_logger.info.call_args[0][0]
            assert "AI generated contextual response" in info_msg
            assert "AI generated response text here"[:50] in info_msg

    @pytest.mark.asyncio
    async def test_edge_cases_invalid_ai_responses(
        self, generator_with_ai, mock_ai_service, mock_session
    ):
        """Test edge cases with invalid AI responses."""
        text = "test"
        emotion = {"sentiment": "neutral", "score": 0.5}

        # Test invalid activity type
        mock_ai_service.determine_activity_type.return_value = "INVALID_ACTIVITY"
        mock_ai_service.generate_response.return_value = "Some response"

        with pytest.raises(KeyError):
            await generator_with_ai.determine_activity_type(text, emotion, mock_session)

        # Test None response
        mock_ai_service.generate_response.return_value = None
        mock_ai_service.determine_activity_type.return_value = "CONVERSATION"

        # Should handle gracefully and not crash
        result = await generator_with_ai.generate_contextual_response(
            text, emotion, mock_session
        )
        assert isinstance(result, ResponseContext)

    @pytest.mark.asyncio
    async def test_different_emotion_sentiments(
        self, generator_with_ai, mock_ai_service, mock_session
    ):
        """Test handling of different emotion sentiments."""
        text = "test input"
        mock_ai_service.generate_response.return_value = "Response"
        mock_ai_service.determine_activity_type.return_value = "CONVERSATION"

        sentiments = [
            "joy",
            "sadness",
            "anger",
            "fear",
            "surprise",
            "disgust",
            "neutral",
        ]

        for sentiment in sentiments:
            emotion = {"sentiment": sentiment, "score": 0.7}

            result = await generator_with_ai.generate_contextual_response(
                text, emotion, mock_session
            )

            assert result.emotion == sentiment
            assert isinstance(result, ResponseContext)

    @pytest.mark.asyncio
    async def test_conversation_history_handling(
        self, generator_with_ai, mock_ai_service, mock_session
    ):
        """Test conversation history handling in AI calls."""
        text = "Continue our conversation"
        emotion = {"sentiment": "engaged", "score": 0.8}
        mock_ai_service.generate_response.return_value = "Continuing conversation..."
        mock_ai_service.determine_activity_type.return_value = "CONVERSATION"

        await generator_with_ai.generate_contextual_response(
            text, emotion, mock_session
        )

        # Verify that conversation_history is passed (currently empty dummy)
        call_args = mock_ai_service.generate_response.call_args
        assert call_args[1]["conversation_history"] == []
        assert call_args[1]["current_input"] == text

    def test_response_context_immutability(self):
        """Test that ResponseContext behaves as expected with slots."""
        context = ResponseContext(
            text="Test", activity_type=ActivityType.STORY, emotion="happy"
        )

        # Should be able to access attributes
        assert context.text == "Test"
        assert context.activity_type == ActivityType.STORY
        assert context.emotion == "happy"

        # Should be able to modify attributes (dataclass behavior)
        context.text = "Modified"
        assert context.text == "Modified"

    @pytest.mark.asyncio
    async def test_error_recovery_sequences(
        self, generator_with_ai, mock_ai_service, mock_session
    ):
        """Test error recovery in sequences of operations."""
        text = "test input"
        emotion = {"sentiment": "neutral", "score": 0.5}

        # First call fails, second succeeds
        mock_ai_service.generate_response.side_effect = [
            Exception("First failure"),
            "Success response",
        ]
        mock_ai_service.determine_activity_type.side_effect = [
            Exception("Activity failure"),
            "CONVERSATION",
        ]

        with patch.object(generator_with_ai, "logger"):
            # First call should fallback
            result1 = await generator_with_ai.generate_contextual_response(
                text, emotion, mock_session
            )
            assert "I'm sorry, I couldn't generate" in result1.text

            # Reset side effects for success
            mock_ai_service.generate_response.side_effect = None
            mock_ai_service.generate_response.return_value = "Success response"
            mock_ai_service.determine_activity_type.side_effect = None
            mock_ai_service.determine_activity_type.return_value = "CONVERSATION"

            # Second call should succeed
            result2 = await generator_with_ai.generate_contextual_response(
                text, emotion, mock_session
            )
            assert result2.text == "Success response"
