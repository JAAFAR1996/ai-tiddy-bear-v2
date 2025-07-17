"""
Tests for Interaction Service
Testing child interaction processing with safety filters.
"""

import pytest
from datetime import datetime
from unittest.mock import patch

from src.application.services.interaction_service import InteractionService


class TestInteractionService:
    """Test the Interaction Service."""

    @pytest.fixture
    def service(self):
        """Create an interaction service instance."""
        return InteractionService()

    def test_initialization(self, service):
        """Test service initialization."""
        assert isinstance(service, InteractionService)
        assert service.max_message_length == 500
        assert service.min_child_age == 3
        assert service.max_child_age == 13

    @pytest.mark.asyncio
    async def test_process_valid_interaction(self, service):
        """Test processing a valid child interaction."""
        child_id = "child_123"
        message = "Hello, can you tell me a story?"

        with patch.object(service, "_check_content_safety") as mock_safety:
            mock_safety.return_value = {"safe": True, "reason": ""}

            with patch(
                "src.application.services.interaction_service.datetime"
            ) as mock_datetime:
                mock_datetime.utcnow.return_value = datetime(
                    2024, 1, 15, 10, 30, 0
                )

                result = await service.process(child_id, message)

        assert result["success"] is True
        assert result["child_id"] == child_id
        assert result["processed_message"] == message.strip()
        assert result["safe"] is True
        assert result["timestamp"] == "2024-01-15T10:30:00"

        # Verify safety check was called
        mock_safety.assert_called_once_with(message.strip())

    @pytest.mark.asyncio
    async def test_process_invalid_child_id(self, service):
        """Test processing with invalid child ID."""
        invalid_child_ids = [None, "", 123, [], {}]

        for invalid_id in invalid_child_ids:
            with pytest.raises(ValueError, match="Valid child_id is required"):
                await service.process(invalid_id, "test message")

    @pytest.mark.asyncio
    async def test_process_invalid_message(self, service):
        """Test processing with invalid message."""
        child_id = "child_123"
        invalid_messages = [None, "", 123, [], {}]

        for invalid_message in invalid_messages:
            with pytest.raises(ValueError, match="Valid message is required"):
                await service.process(child_id, invalid_message)

    @pytest.mark.asyncio
    async def test_process_message_too_long(self, service):
        """Test processing with message exceeding maximum length."""
        child_id = "child_123"
        long_message = "x" * (service.max_message_length + 1)

        with pytest.raises(ValueError, match="Message too long"):
            await service.process(child_id, long_message)

    @pytest.mark.asyncio
    async def test_process_message_at_length_limit(self, service):
        """Test processing with message at exactly the length limit."""
        child_id = "child_123"
        max_length_message = "x" * service.max_message_length

        with patch.object(service, "_check_content_safety") as mock_safety:
            mock_safety.return_value = {"safe": True, "reason": ""}

            result = await service.process(child_id, max_length_message)

        assert result["success"] is True
        assert len(result["processed_message"]) == service.max_message_length

    @pytest.mark.asyncio
    async def test_process_unsafe_content(self, service):
        """Test processing message with unsafe content."""
        child_id = "child_123"
        message = "This contains bad word content"

        with patch.object(service, "_check_content_safety") as mock_safety:
            mock_safety.return_value = {
                "safe": False,
                "reason": "Contains inappropriate language",
            }

            with patch(
                "src.application.services.interaction_service.logger"
            ) as mock_logger:
                with patch(
                    "src.application.services.interaction_service.datetime"
                ) as mock_datetime:
                    mock_datetime.utcnow.return_value = datetime(
                        2024, 1, 15, 10, 30, 0
                    )

                    result = await service.process(child_id, message)

        assert result["success"] is False
        assert result["error"] == "Message contains inappropriate content"
        assert result["safe"] is False
        assert result["timestamp"] == "2024-01-15T10:30:00"

        # Should log warning
        mock_logger.warning.assert_called_once()
        warning_msg = mock_logger.warning.call_args[0][0]
        assert "Unsafe content detected" in warning_msg
        assert child_id in warning_msg

    @pytest.mark.asyncio
    async def test_process_successful_logging(self, service):
        """Test that successful interactions are properly logged."""
        child_id = "child_456"
        message = "What is your favorite color?"

        with patch.object(service, "_check_content_safety") as mock_safety:
            mock_safety.return_value = {"safe": True, "reason": ""}

            with patch(
                "src.application.services.interaction_service.logger"
            ) as mock_logger:
                result = await service.process(child_id, message)

        assert result["success"] is True

        # Should log successful interaction
        mock_logger.info.assert_called_once()
        log_msg = mock_logger.info.call_args[0][0]
        assert "Safe interaction processed" in log_msg
        assert child_id in log_msg
        assert message.strip() in log_msg

    def test_sanitize_message_basic(self, service):
        """Test basic message sanitization."""
        test_cases = [
            ("  hello world  ", "hello world"),
            ("\n\ntest message\n\n", "test message"),
            ("\t\tspaces and tabs\t\t", "spaces and tabs"),
            ("already clean", "already clean"),
            ("", ""),
            ("   ", ""),
        ]

        for input_msg, expected in test_cases:
            result = service._sanitize_message(input_msg)
            assert result == expected

    def test_sanitize_message_special_characters(self, service):
        """Test message sanitization with special characters."""
        # Current implementation only strips whitespace
        test_cases = [
            ("  Hello! How are you? 😊  ", "Hello! How are you? 😊"),
            ("  Test with émojis 🚨  ", "Test with émojis 🚨"),
            ("  Mixed chars: !@#$%^&*()  ", "Mixed chars: !@#$%^&*()"),
        ]

        for input_msg, expected in test_cases:
            result = service._sanitize_message(input_msg)
            assert result == expected

    @pytest.mark.asyncio
    async def test_check_content_safety_safe_content(self, service):
        """Test content safety check with safe content."""
        safe_messages = [
            "Hello, how are you?",
            "Can you tell me a story about animals?",
            "What is 2 + 2?",
            "I like playing with toys",
            "Tell me about dinosaurs",
        ]

        for message in safe_messages:
            result = await service._check_content_safety(message)
            assert result["safe"] is True
            assert result["reason"] == ""

    @pytest.mark.asyncio
    async def test_check_content_safety_unsafe_content(self, service):
        """Test content safety check with unsafe content."""
        unsafe_messages = [
            "This has a bad word in it",
            "BAD WORD here",
            "Contains bad word somewhere",
        ]

        for message in unsafe_messages:
            result = await service._check_content_safety(message)
            assert result["safe"] is False
            assert result["reason"] == "Contains inappropriate language"

    @pytest.mark.asyncio
    async def test_check_content_safety_case_insensitive(self, service):
        """Test that content safety check is case insensitive."""
        variations = [
            "bad word",
            "Bad Word",
            "BAD WORD",
            "bAd WoRd",
        ]

        for message in variations:
            result = await service._check_content_safety(message)
            assert result["safe"] is False
            assert result["reason"] == "Contains inappropriate language"

    def test_check_child_age_valid_ages(self, service):
        """Test child age validation with valid ages."""
        valid_ages = [3, 5, 8, 10, 13]

        for age in valid_ages:
            result = service._check_child_age(age)
            assert result is True

    def test_check_child_age_invalid_ages(self, service):
        """Test child age validation with invalid ages."""
        invalid_ages = [2, 14, 15, 0, -1, 100]

        for age in invalid_ages:
            result = service._check_child_age(age)
            assert result is False

    def test_check_child_age_boundary_conditions(self, service):
        """Test child age validation at boundaries."""
        # Test exact boundaries
        assert service._check_child_age(service.min_child_age) is True  # 3
        assert service._check_child_age(service.max_child_age) is True  # 13
        assert (
            service._check_child_age(service.min_child_age - 1) is False
        )  # 2
        assert (
            service._check_child_age(service.max_child_age + 1) is False
        )  # 14

    @pytest.mark.asyncio
    async def test_process_whitespace_only_message(self, service):
        """Test processing message with only whitespace."""
        child_id = "child_123"
        whitespace_messages = ["   ", "\n\n\n", "\t\t\t", "  \n\t  "]

        for message in whitespace_messages:
            with pytest.raises(ValueError, match="Valid message is required"):
                await service.process(child_id, message)

    @pytest.mark.asyncio
    async def test_concurrent_interaction_processing(self, service):
        """Test concurrent processing of multiple interactions."""
        import asyncio

        interactions = [
            ("child_1", "Hello, how are you?"),
            ("child_2", "Can you tell me a story?"),
            ("child_3", "What is your favorite color?"),
            ("child_4", "I like playing games"),
            ("child_5", "Tell me about space"),
        ]

        with patch.object(service, "_check_content_safety") as mock_safety:
            mock_safety.return_value = {"safe": True, "reason": ""}

            # Process all interactions concurrently
            tasks = [
                service.process(child_id, message)
                for child_id, message in interactions
            ]
            results = await asyncio.gather(*tasks)

        # All should succeed
        assert len(results) == 5
        assert all(r["success"] for r in results)

        # Each should have correct child_id
        for i, (child_id, _) in enumerate(interactions):
            assert results[i]["child_id"] == child_id

    @pytest.mark.asyncio
    async def test_message_processing_preserves_content(self, service):
        """Test that message processing preserves important content."""
        test_cases = [
            "Hello! How are you today? 😊",
            "Can you help me with math: 2 + 2 = ?",
            "I love animals like cats, dogs, and birds!",
            "Tell me about planets: Earth, Mars, Jupiter",
            "My favorite colors are red, blue, and green.",
        ]

        for message in test_cases:
            with patch.object(service, "_check_content_safety") as mock_safety:
                mock_safety.return_value = {"safe": True, "reason": ""}

                result = await service.process("child_123", message)

            assert result["success"] is True
            # Content should be preserved (only stripped)
            assert result["processed_message"] == message.strip()

    @pytest.mark.asyncio
    async def test_error_handling_in_safety_check(self, service):
        """Test error handling when safety check fails."""
        child_id = "child_123"
        message = "test message"

        with patch.object(service, "_check_content_safety") as mock_safety:
            mock_safety.side_effect = Exception("Safety check failed")

            # Should propagate the exception
            with pytest.raises(Exception, match="Safety check failed"):
                await service.process(child_id, message)

    @pytest.mark.asyncio
    async def test_timestamp_consistency(self, service):
        """Test that timestamps are consistent and properly formatted."""
        child_id = "child_123"
        message = "test message"

        with patch.object(service, "_check_content_safety") as mock_safety:
            mock_safety.return_value = {"safe": True, "reason": ""}

            with patch(
                "src.application.services.interaction_service.datetime"
            ) as mock_datetime:
                mock_datetime.utcnow.return_value = datetime(
                    2024, 3, 15, 14, 30, 45, 123456
                )

                result = await service.process(child_id, message)

        assert result["timestamp"] == "2024-03-15T14:30:45.123456"

        # Should be valid ISO format
        parsed_time = datetime.fromisoformat(result["timestamp"])
        assert parsed_time.year == 2024
        assert parsed_time.month == 3
        assert parsed_time.day == 15
        assert parsed_time.hour == 14
        assert parsed_time.minute == 30
        assert parsed_time.second == 45

    @pytest.mark.asyncio
    async def test_different_child_ids_isolation(self, service):
        """Test that interactions from different children are properly isolated."""
        child_interactions = [
            ("child_alice", "Hello from Alice"),
            ("child_bob", "Hello from Bob"),
            ("child_charlie", "Hello from Charlie"),
        ]

        results = []
        for child_id, message in child_interactions:
            with patch.object(service, "_check_content_safety") as mock_safety:
                mock_safety.return_value = {"safe": True, "reason": ""}

                result = await service.process(child_id, message)
                results.append(result)

        # Each result should have correct child_id and message
        for i, (expected_child_id, expected_message) in enumerate(
            child_interactions
        ):
            assert results[i]["child_id"] == expected_child_id
            assert results[i]["processed_message"] == expected_message

    @pytest.mark.parametrize("message_length", [1, 50, 100, 250, 499, 500])
    @pytest.mark.asyncio
    async def test_various_message_lengths(self, service, message_length):
        """Test processing messages of various lengths."""
        child_id = "child_123"
        message = "x" * message_length

        with patch.object(service, "_check_content_safety") as mock_safety:
            mock_safety.return_value = {"safe": True, "reason": ""}

            result = await service.process(child_id, message)

        assert result["success"] is True
        assert len(result["processed_message"]) == message_length

    @pytest.mark.asyncio
    async def test_unicode_and_emoji_handling(self, service):
        """Test handling of Unicode characters and emojis."""
        unicode_messages = [
            "Hello 👋 from Alice!",
            "I love animals 🐱🐶🐰",
            "¿Cómo estás? 😊",
            "Testing 中文字符",
            "Math: 2 + 2 = 4 ✓",
            "Hearts: ❤️💙💚💛💜",
        ]

        for message in unicode_messages:
            with patch.object(service, "_check_content_safety") as mock_safety:
                mock_safety.return_value = {"safe": True, "reason": ""}

                result = await service.process("child_123", message)

            assert result["success"] is True
            assert result["processed_message"] == message.strip()

    @pytest.mark.asyncio
    async def test_service_limits_constants(self, service):
        """Test that service limits are properly configured."""
        # These limits are important for child safety
        assert service.max_message_length == 500  # Reasonable limit
        assert service.min_child_age == 3  # COPPA consideration
        assert service.max_child_age == 13  # COPPA boundary

        # Verify these are used in validation
        assert service._check_child_age(2) is False  # Below min
        assert service._check_child_age(3) is True  # At min
        assert service._check_child_age(13) is True  # At max
        assert service._check_child_age(14) is False  # Above max
