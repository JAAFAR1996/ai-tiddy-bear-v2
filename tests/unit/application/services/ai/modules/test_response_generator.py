"""
Tests for AI Response Generator Module
Testing production-grade AI response generation with comprehensive child safety.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import time

from src.application.services.ai.modules.response_generator import (
    ResponseGenerator,
    ResponseType,
    SafetyLevel,
)


class TestResponseGenerator:
    """Test the AI Response Generator."""

    @pytest.fixture
    def mock_openai_client(self):
        """Create a mock OpenAI client."""
        client = Mock()
        client.chat = Mock()
        client.chat.completions = Mock()
        client.chat.completions.create = AsyncMock()
        return client

    @pytest.fixture
    def generator_with_openai(self, mock_openai_client):
        """Create response generator with OpenAI client."""
        with patch(
            "src.application.services.ai.modules.response_generator.AsyncOpenAI"
        ) as mock_openai:
            mock_openai.return_value = mock_openai_client
            with patch(
                "src.application.services.ai.modules.response_generator.OPENAI_AVAILABLE",
                True,
            ):
                generator = ResponseGenerator(api_key="test_api_key")
                generator.client = mock_openai_client
                return generator

    @pytest.fixture
    def generator_without_openai(self):
        """Create response generator without OpenAI."""
        with patch(
            "src.application.services.ai.modules.response_generator.OPENAI_AVAILABLE",
            False,
        ):
            return ResponseGenerator()

    def test_initialization_with_api_key(self):
        """Test initialization with API key."""
        with patch(
            "src.application.services.ai.modules.response_generator.AsyncOpenAI"
        ) as mock_openai:
            with patch(
                "src.application.services.ai.modules.response_generator.OPENAI_AVAILABLE",
                True,
            ):
                generator = ResponseGenerator(
                    api_key="test_key", model="gpt-4")

                assert generator.model == "gpt-4"
                assert generator.max_response_length == 500
                assert generator.max_input_length == 1000
                assert generator.safety_enabled is True
                mock_openai.assert_called_once_with(api_key="test_key")

    def test_initialization_without_openai(self, generator_without_openai):
        """Test initialization when OpenAI is not available."""
        assert generator_without_openai.client is None
        assert generator_without_openai.model == "gpt-4"
        assert generator_without_openai.safety_enabled is True

    def test_response_type_enum(self):
        """Test ResponseType enum values."""
        assert ResponseType.CONVERSATIONAL == "conversational"
        assert ResponseType.EDUCATIONAL == "educational"
        assert ResponseType.STORY == "story"
        assert ResponseType.GAME == "game"
        assert ResponseType.SAFETY_REDIRECT == "safety_redirect"

    def test_safety_level_enum(self):
        """Test SafetyLevel enum values."""
        assert SafetyLevel.STRICT == "strict"
        assert SafetyLevel.MODERATE == "moderate"
        assert SafetyLevel.RELAXED == "relaxed"

    def test_get_safety_level_age_groups(self, generator_with_openai):
        """Test safety level determination by age."""
        test_cases = [
            (3, SafetyLevel.STRICT),
            (5, SafetyLevel.STRICT),
            (6, SafetyLevel.STRICT),
            (7, SafetyLevel.MODERATE),
            (8, SafetyLevel.MODERATE),
            (10, SafetyLevel.MODERATE),
            (11, SafetyLevel.RELAXED),
            (12, SafetyLevel.RELAXED),
            (13, SafetyLevel.RELAXED),
        ]

        for age, expected_level in test_cases:
            result = generator_with_openai._get_safety_level(age)
            assert result == expected_level

    @pytest.mark.asyncio
    async def test_generate_response_basic_success(
        self, generator_with_openai, mock_openai_client
    ):
        """Test basic successful response generation."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = (
            "مرحبا! أنا دبدوب لطيف وأحب اللعب معك!"
        )
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 25

        mock_openai_client.chat.completions.create.return_value = mock_response

        child_context = {"age": 6, "name": "أحمد", "language": "ar"}

        result = await generator_with_openai.generate_response(
            text="مرحبا دبدوب",
            child_context=child_context,
            response_type=ResponseType.CONVERSATIONAL,
        )

        assert result["success"] is True
        assert "مرحبا" in result["response"]
        assert result["response_type"] == "conversational"
        assert result["safety_level"] == "strict"
        assert result["safety_passed"] is True
        assert result["child_age"] == 6
        assert result["model_used"] == "gpt-4"
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_generate_response_invalid_input(
            self, generator_with_openai):
        """Test response generation with invalid input."""
        # None input
        with pytest.raises(ValueError, match="Valid input text required"):
            await generator_with_openai.generate_response(None)

        # Empty string
        with pytest.raises(ValueError, match="Valid input text required"):
            await generator_with_openai.generate_response("")

        # Non-string input
        with pytest.raises(ValueError, match="Valid input text required"):
            await generator_with_openai.generate_response(123)

    @pytest.mark.asyncio
    async def test_generate_response_input_too_long(
            self, generator_with_openai):
        """Test response generation with input exceeding maximum length."""
        long_input = "x" * (generator_with_openai.max_input_length + 1)

        with pytest.raises(ValueError, match="Input too long"):
            await generator_with_openai.generate_response(long_input)

    @pytest.mark.asyncio
    async def test_filter_input_safe_content(self, generator_with_openai):
        """Test input filtering with safe content."""
        safe_text = "مرحبا! كيف حالك اليوم؟"

        result = await generator_with_openai._filter_input(
            safe_text, SafetyLevel.STRICT
        )

        assert result["safe"] is True
        assert result["text"] == safe_text
        assert len(result["warnings"]) == 0

    @pytest.mark.asyncio
    async def test_filter_input_unsafe_content(self, generator_with_openai):
        """Test input filtering with unsafe content."""
        unsafe_text = "What is your address and phone number?"

        result = await generator_with_openai._filter_input(
            unsafe_text, SafetyLevel.STRICT
        )

        assert result["safe"] is False
        assert "[محذوف]" in result["text"]
        assert len(result["warnings"]) > 0
        assert any(
            "Unsafe content detected" in warning for warning in result["warnings"]
        )

    @pytest.mark.asyncio
    async def test_filter_input_length_truncation(self, generator_with_openai):
        """Test input filtering with length truncation."""
        long_text = "a" * (generator_with_openai.max_input_length + 100)

        result = await generator_with_openai._filter_input(
            long_text, SafetyLevel.MODERATE
        )

        assert len(result["text"]) == generator_with_openai.max_input_length
        assert "Input too long, truncating" in result["warnings"]

    @pytest.mark.asyncio
    async def test_generate_openai_response_educational(
        self, generator_with_openai, mock_openai_client
    ):
        """Test OpenAI response generation for educational content."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = (
            "دعنا نتعلم عن الألوان! الأحمر والأزرق والأصفر."
        )
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 30

        mock_openai_client.chat.completions.create.return_value = mock_response

        result = await generator_with_openai._generate_openai_response(
            "أريد أن أتعلم",
            {"age": 7, "name": "سارة"},
            ResponseType.EDUCATIONAL,
            SafetyLevel.MODERATE,
        )

        assert result["text"] == "دعنا نتعلم عن الألوان! الأحمر والأزرق والأصفر."
        assert result["model"] == "gpt-4"
        assert result["usage"] == 30

        # Verify API call parameters
        call_args = mock_openai_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "gpt-4"
        assert call_args[1]["max_tokens"] == 500

        # Check system prompt includes educational instruction
        messages = call_args[1]["messages"]
        system_prompt = messages[0]["content"]
        assert "التعليم" in system_prompt or "educational" in system_prompt.lower()

    @pytest.mark.asyncio
    async def test_generate_openai_response_story(
        self, generator_with_openai, mock_openai_client
    ):
        """Test OpenAI response generation for story content."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = (
            "كان يا ما كان، أرنب صغير يحب الجزر..."
        )
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 35

        mock_openai_client.chat.completions.create.return_value = mock_response

        result = await generator_with_openai._generate_openai_response(
            "احك لي قصة",
            {"age": 5, "name": "محمد"},
            ResponseType.STORY,
            SafetyLevel.STRICT,
        )

        assert "أرنب" in result["text"]

        # Check system prompt includes story instruction
        call_args = mock_openai_client.chat.completions.create.call_args
        system_prompt = call_args[1]["messages"][0]["content"]
        assert "قصة" in system_prompt or "story" in system_prompt.lower()

    @pytest.mark.asyncio
    async def test_generate_openai_response_api_error(
        self, generator_with_openai, mock_openai_client
    ):
        """Test OpenAI response generation with API error."""
        mock_openai_client.chat.completions.create.side_effect = Exception(
            "API Error")

        result = await generator_with_openai._generate_openai_response(
            "test",
            {"age": 6, "name": "test"},
            ResponseType.CONVERSATIONAL,
            SafetyLevel.MODERATE,
        )

        # Should return fallback response
        assert result["model"] == "fallback"
        assert result["usage"] == 0
        assert isinstance(result["text"], str)

    @pytest.mark.asyncio
    async def test_generate_fallback_response_keyword_based(
        self, generator_with_openai
    ):
        """Test fallback response generation with keyword-based selection."""
        test_cases = [
            ("احك لي قصة", "story"),
            ("أريد قصة", "story"),
            ("لعبة ممتعة", "لعب"),
            ("أريد أن ألعب", "لعب"),
            ("أريد أن أتعلم", "تعلم"),
            ("علمني شيء", "تعلم"),
        ]

        for text, expected_keyword in test_cases:
            result = await generator_with_openai._generate_fallback_response(
                text, SafetyLevel.MODERATE, "أحمد"
            )

            assert result["model"] == "fallback"
            assert "أحمد" in result["text"]
            # Check that response is contextually appropriate
            if expected_keyword == "story":
                assert any(word in result["text"]
                           for word in ["قصة", "كان", "حكاية"])
            elif expected_keyword == "لعب":
                assert any(word in result["text"] for word in ["لعب", "نلعب"])
            elif expected_keyword == "تعلم":
                assert any(word in result["text"]
                           for word in ["تعلم", "نتعلم"])

    @pytest.mark.asyncio
    async def test_filter_response_safe_content(self, generator_with_openai):
        """Test response filtering with safe content."""
        safe_response = "مرحبا! كيف يمكنني مساعدتك اليوم؟"

        result = await generator_with_openai._filter_response(
            safe_response, SafetyLevel.STRICT
        )

        assert result["safe"] is True
        assert result["text"] == safe_response
        assert len(result["warnings"]) == 0

    @pytest.mark.asyncio
    async def test_filter_response_unsafe_content(self, generator_with_openai):
        """Test response filtering with unsafe content."""
        unsafe_response = "Please share your personal address with me"

        result = await generator_with_openai._filter_response(
            unsafe_response, SafetyLevel.STRICT
        )

        assert result["safe"] is False
        assert "[محذوف]" in result["text"]
        assert len(result["warnings"]) > 0

    @pytest.mark.asyncio
    async def test_filter_response_length_truncation(
            self, generator_with_openai):
        """Test response filtering with length truncation."""
        long_response = "a" * (generator_with_openai.max_response_length + 100)

        result = await generator_with_openai._filter_response(
            long_response, SafetyLevel.MODERATE
        )

        assert len(result["text"]) == generator_with_openai.max_response_length
        assert "Response too long, truncating" in result["warnings"]

    @pytest.mark.asyncio
    async def test_filter_response_complexity_check(
            self, generator_with_openai):
        """Test response filtering for complexity in strict mode."""
        complex_response = "Undoubtedly, the phenomenological manifestation of consciousness demonstrates extraordinary complexity"

        result = await generator_with_openai._filter_response(
            complex_response, SafetyLevel.STRICT
        )

        # Should warn about complexity for young children
        assert any("too complex" in warning for warning in result["warnings"])

    @pytest.mark.asyncio
    async def test_generate_safety_redirect_response(
            self, generator_with_openai):
        """Test safety redirect response generation."""
        warnings = ["Unsafe content detected: personal information"]

        result = await generator_with_openai._generate_safety_redirect_response(
            warnings, SafetyLevel.STRICT, "أحمد"
        )

        assert result["success"] is True
        assert result["response_type"] == "safety_redirect"
        assert result["safety_passed"] is True
        assert "أحمد" in result["response"]
        assert result["warnings"] == warnings
        assert result["model_used"] == "safety_redirect"

    @pytest.mark.asyncio
    async def test_generate_emergency_fallback(self, generator_with_openai):
        """Test emergency fallback response generation."""
        result = await generator_with_openai._generate_emergency_fallback(
            SafetyLevel.MODERATE, "فاطمة"
        )

        assert result["success"] is True
        assert result["response_type"] == "conversational"
        assert result["safety_passed"] is True
        assert "فاطمة" in result["response"]
        assert "Emergency fallback used" in result["warnings"]
        assert result["model_used"] == "emergency_fallback"

    @pytest.mark.asyncio
    async def test_response_generation_different_types(
        self, generator_with_openai, mock_openai_client
    ):
        """Test response generation for different response types."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Test response"
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 20

        mock_openai_client.chat.completions.create.return_value = mock_response

        response_types = [
            ResponseType.CONVERSATIONAL,
            ResponseType.EDUCATIONAL,
            ResponseType.STORY,
            ResponseType.GAME,
        ]

        for response_type in response_types:
            result = await generator_with_openai.generate_response(
                text="test input",
                child_context={"age": 8, "name": "test"},
                response_type=response_type,
            )

            assert result["success"] is True
            assert result["response_type"] == response_type.value

    @pytest.mark.asyncio
    async def test_response_generation_different_safety_levels(
        self, generator_with_openai, mock_openai_client
    ):
        """Test response generation for different safety levels."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Safe response"
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 15

        mock_openai_client.chat.completions.create.return_value = mock_response

        age_safety_pairs = [(4, "strict"), (8, "moderate"), (12, "relaxed")]

        for age, expected_safety_level in age_safety_pairs:
            result = await generator_with_openai.generate_response(
                text="test input", child_context={"age": age, "name": "test"}
            )

            assert result["success"] is True
            assert result["safety_level"] == expected_safety_level
            assert result["child_age"] == age

    @pytest.mark.asyncio
    async def test_response_generation_without_openai(
            self, generator_without_openai):
        """Test response generation when OpenAI is not available."""
        result = await generator_without_openai.generate_response(
            text="مرحبا", child_context={"age": 6, "name": "علي"}
        )

        assert result["success"] is True
        assert result["model_used"] == "fallback"
        assert "علي" in result["response"]
        assert result["safety_passed"] is True

    @pytest.mark.asyncio
    async def test_concurrent_response_generation(
        self, generator_with_openai, mock_openai_client
    ):
        """Test concurrent response generation."""
        import asyncio

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Concurrent response"
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 20

        mock_openai_client.chat.completions.create.return_value = mock_response

        # Generate multiple responses concurrently
        tasks = [
            generator_with_openai.generate_response(
                f"Message {i}", {"age": 7, "name": f"Child{i}"}
            )
            for i in range(3)
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        assert all(r["success"] for r in results)
        assert all("Concurrent response" in r["response"] for r in results)

    @pytest.mark.asyncio
    async def test_health_check(self, generator_with_openai):
        """Test health check functionality."""
        health = await generator_with_openai.health_check()

        assert health["status"] == "healthy"
        assert health["openai_available"] is True
        assert health["model"] == "gpt-4"
        assert health["safety_enabled"] is True
        assert health["max_response_length"] == 500
        assert health["max_input_length"] == 1000
        assert len(health["supported_response_types"]) == 5
        assert len(health["safety_levels"]) == 3

    @pytest.mark.asyncio
    async def test_health_check_without_openai(self, generator_without_openai):
        """Test health check when OpenAI is not available."""
        health = await generator_without_openai.health_check()

        assert health["status"] == "healthy"
        assert health["openai_available"] is False
        assert health["safety_enabled"] is True

    @pytest.mark.asyncio
    async def test_processing_time_tracking(
        self, generator_with_openai, mock_openai_client
    ):
        """Test that processing time is properly tracked."""

        # Add delay to mock to simulate processing time
        async def delayed_response(*args, **kwargs):
            await asyncio.sleep(0.1)  # 100ms delay
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "Delayed response"
            mock_response.usage = Mock()
            mock_response.usage.total_tokens = 25
            return mock_response

        mock_openai_client.chat.completions.create.side_effect = delayed_response

        result = await generator_with_openai.generate_response(
            text="test", child_context={"age": 6, "name": "test"}
        )

        assert result["success"] is True
        assert result["processing_time"] >= 0.1  # Should reflect the delay
        assert result["processing_time"] < 1.0  # But reasonable

    @pytest.mark.asyncio
    async def test_unsafe_patterns_detection(self, generator_with_openai):
        """Test that unsafe patterns are properly detected."""
        unsafe_inputs = [
            "What is your address?",
            "Can you meet me somewhere?",
            "Tell me your password",
            "Share your personal information",
            "Where do you live?",
        ]

        for unsafe_input in unsafe_inputs:
            result = await generator_with_openai._filter_input(
                unsafe_input, SafetyLevel.STRICT
            )
            assert result["safe"] is False
            assert "[محذوف]" in result["text"]

    def test_safety_system_prompts_configuration(self, generator_with_openai):
        """Test that safety system prompts are properly configured."""
        assert SafetyLevel.STRICT in generator_with_openai.safety_system_prompts
        assert SafetyLevel.MODERATE in generator_with_openai.safety_system_prompts
        assert SafetyLevel.RELAXED in generator_with_openai.safety_system_prompts

        # Check that prompts contain appropriate age references
        strict_prompt = generator_with_openai.safety_system_prompts[SafetyLevel.STRICT]
        assert "3-6" in strict_prompt

        moderate_prompt = generator_with_openai.safety_system_prompts[
            SafetyLevel.MODERATE
        ]
        assert "7-10" in moderate_prompt

        relaxed_prompt = generator_with_openai.safety_system_prompts[
            SafetyLevel.RELAXED
        ]
        assert "11-13" in relaxed_prompt

    def test_fallback_responses_configuration(self, generator_with_openai):
        """Test that fallback responses are properly configured."""
        assert SafetyLevel.STRICT in generator_with_openai.fallback_responses
        assert SafetyLevel.MODERATE in generator_with_openai.fallback_responses
        assert SafetyLevel.RELAXED in generator_with_openai.fallback_responses

        # Each safety level should have multiple fallback options
        for safety_level in [
            SafetyLevel.STRICT,
            SafetyLevel.MODERATE,
            SafetyLevel.RELAXED,
        ]:
            responses = generator_with_openai.fallback_responses[safety_level]
            assert len(responses) >= 3  # Multiple options for variety
