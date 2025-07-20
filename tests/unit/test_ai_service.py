"""Comprehensive Unit Tests for Production AI Service"""

import json
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.domain.value_objects import ChildAge
from src.infrastructure.ai.real_ai_service import (
    AIResponse,
    ProductionAIService,
    StoryRequest,
)


@pytest.fixture
def ai_service():
    """Create AI service instance for testing."""
    service = ProductionAIService()
    service.openai_api_key = "test-api-key"
    return service


@pytest.fixture
def mock_openai_client():
    """Create mock OpenAI client."""
    client = AsyncMock()
    client.chat.completions.create = AsyncMock()
    client.moderations.create = AsyncMock()
    return client


@pytest.fixture
def mock_redis():
    """Create mock Redis cache."""
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.setex = AsyncMock(return_value=True)
    return redis


@pytest.fixture
def child_context():
    """Create sample child context."""
    return {
        "child_id": str(uuid4()),
        "name": "Alice",
        "age": 7,
        "interests": ["dinosaurs", "space", "animals"],
        "personality": "curious and friendly",
    }


class TestContentGeneration:
    """Test AI content generation functionality."""

    @pytest.mark.asyncio
    async def test_generate_response_success(
        self, ai_service, mock_openai_client, child_context
    ):
        """Test successful AI response generation."""
        ai_service.client = mock_openai_client

        # Mock OpenAI response
        mock_openai_client.chat.completions.create.return_value = AsyncMock(
            choices=[
                AsyncMock(
                    message=AsyncMock(
                        content="Once upon a time, there was a friendly dinosaur named Rex!"
                    )
                )
            ]
        )

        # Mock moderation as safe
        mock_openai_client.moderations.create.return_value = AsyncMock(
            results=[
                AsyncMock(
                    categories=AsyncMock(
                        violence=False,
                        violence_graphic=False,
                        sexual=False,
                        sexual_minors=False,
                        hate=False,
                        hate_threatening=False,
                        self_harm=False,
                        self_harm_intent=False,
                        self_harm_instructions=False,
                        harassment=False,
                        harassment_threatening=False,
                    )
                )
            ]
        )

        response = await ai_service.generate_response(
            message="Tell me a story about dinosaurs",
            child_age=ChildAge.SCHOOL_AGE,
            child_context=child_context,
        )

        assert isinstance(response, AIResponse)
        assert response.content is not None
        assert response.safety_score >= 0.9
        assert response.age_appropriate is True
        assert "dinosaur" in response.content.lower()
        assert len(response.topics) > 0

    @pytest.mark.asyncio
    async def test_generate_response_with_context(
        self, ai_service, mock_openai_client, child_context
    ):
        """Test response generation with conversation context."""
        ai_service.client = mock_openai_client

        conversation_context = [
            {"role": "user", "content": "What's your favorite color?"},
            {
                "role": "assistant",
                "content": "I love all colors, but blue is special!",
            },
        ]

        mock_openai_client.chat.completions.create.return_value = AsyncMock(
            choices=[
                AsyncMock(
                    message=AsyncMock(
                        content="Blue is like the sky and ocean! What's your favorite color?"
                    )
                )
            ]
        )

        response = await ai_service.generate_response(
            message="Why do you like blue?",
            child_age=ChildAge.PRESCHOOL,
            child_context=child_context,
            conversation_context=conversation_context,
        )

        assert response.content is not None
        assert "blue" in response.content.lower()

    @pytest.mark.asyncio
    async def test_generate_response_unsafe_content(
        self, ai_service, mock_openai_client, child_context
    ):
        """Test handling of unsafe content detection."""
        ai_service.client = mock_openai_client

        # Mock unsafe moderation result
        mock_openai_client.moderations.create.return_value = AsyncMock(
            results=[
                AsyncMock(
                    categories=AsyncMock(
                        violence=True,
                        violence_graphic=False,
                        sexual=False,
                        sexual_minors=False,
                        hate=False,
                        hate_threatening=False,
                        self_harm=False,
                        self_harm_intent=False,
                        self_harm_instructions=False,
                        harassment=False,
                        harassment_threatening=False,
                    )
                )
            ]
        )

        response = await ai_service.generate_response(
            message="Tell me about fighting",
            child_age=ChildAge.PRESCHOOL,
            child_context=child_context,
        )

        assert response.safety_score < 0.5
        assert response.age_appropriate is False
        assert "I'd prefer to talk about" in response.content

    @pytest.mark.asyncio
    async def test_generate_response_with_caching(
        self, ai_service, mock_openai_client, mock_redis, child_context
    ):
        """Test response caching functionality."""
        ai_service.client = mock_openai_client
        ai_service.redis_cache = mock_redis

        # First call - cache miss
        mock_redis.get.return_value = None

        mock_openai_client.chat.completions.create.return_value = AsyncMock(
            choices=[AsyncMock(message=AsyncMock(content="Cached response"))]
        )

        response1 = await ai_service.generate_response(
            message="What is 2+2?",
            child_age=ChildAge.SCHOOL_AGE,
            child_context=child_context,
        )

        assert response1.cached is False
        mock_redis.setex.assert_called_once()

        # Second call - cache hit
        cached_data = {
            "content": "Cached response",
            "safety_score": 1.0,
            "age_appropriate": True,
            "sentiment": "neutral",
            "topics": ["math"],
            "processing_time": 0.1,
        }
        mock_redis.get.return_value = json.dumps(cached_data)

        response2 = await ai_service.generate_response(
            message="What is 2+2?",
            child_age=ChildAge.SCHOOL_AGE,
            child_context=child_context,
        )

        assert response2.cached is True
        assert response2.content == "Cached response"


class TestStoryGeneration:
    """Test story generation functionality."""

    @pytest.mark.asyncio
    async def test_generate_story_success(self, ai_service, mock_openai_client):
        """Test successful story generation."""
        ai_service.client = mock_openai_client

        story_request = StoryRequest(
            theme="space adventure",
            characters=["Luna the astronaut", "Cosmo the robot"],
            child_age=7,
            child_name="Alice",
            duration_minutes=5,
        )

        mock_openai_client.chat.completions.create.return_value = AsyncMock(
            choices=[
                AsyncMock(
                    message=AsyncMock(
                        content="Luna and Cosmo zoomed through space in their shiny rocket ship..."
                    )
                )
            ]
        )

        story = await ai_service.generate_story(story_request)

        assert "story" in story
        assert "title" in story
        assert "Luna" in story["story"]
        assert "Cosmo" in story["story"]
        assert story["age_appropriate"] is True

    @pytest.mark.asyncio
    async def test_generate_story_with_moral(self, ai_service, mock_openai_client):
        """Test story generation with educational moral."""
        ai_service.client = mock_openai_client

        story_request = StoryRequest(
            theme="friendship",
            moral_lesson="sharing is caring",
            child_age=5,
            child_name="Bob",
        )

        mock_openai_client.chat.completions.create.return_value = AsyncMock(
            choices=[
                AsyncMock(
                    message=AsyncMock(
                        content="Two friends learned that sharing toys made playing even more fun!"
                    )
                )
            ]
        )

        story = await ai_service.generate_story(story_request)

        assert "sharing" in story["story"].lower()
        assert story["educational_value"] is not None


class TestSafetyAnalysis:
    """Test content safety analysis."""

    @pytest.mark.asyncio
    async def test_analyze_content_safety_safe(self, ai_service, mock_openai_client):
        """Test safety analysis for safe content."""
        ai_service.client = mock_openai_client

        mock_openai_client.moderations.create.return_value = AsyncMock(
            results=[
                AsyncMock(
                    categories=AsyncMock(
                        violence=False,
                        sexual=False,
                        hate=False,
                        self_harm=False,
                        harassment=False,
                    ),
                    category_scores=AsyncMock(
                        violence=0.001,
                        sexual=0.0001,
                        hate=0.0001,
                        self_harm=0.0001,
                        harassment=0.001,
                    ),
                )
            ]
        )

        result = await ai_service.analyze_content_safety("Let's play a fun game!")

        assert result["safe"] is True
        assert result["safety_score"] > 0.95
        assert len(result["flags"]) == 0
        assert result["severity"] == "none"

    @pytest.mark.asyncio
    async def test_analyze_content_safety_unsafe(self, ai_service, mock_openai_client):
        """Test safety analysis for unsafe content."""
        ai_service.client = mock_openai_client

        mock_openai_client.moderations.create.return_value = AsyncMock(
            results=[
                AsyncMock(
                    categories=AsyncMock(
                        violence=True,
                        sexual=False,
                        hate=False,
                        self_harm=False,
                        harassment=True,
                    ),
                    category_scores=AsyncMock(
                        violence=0.8,
                        sexual=0.001,
                        hate=0.001,
                        self_harm=0.001,
                        harassment=0.7,
                    ),
                )
            ]
        )

        result = await ai_service.analyze_content_safety("Inappropriate content here")

        assert result["safe"] is False
        assert result["safety_score"] < 0.5
        assert "violence" in result["flags"]
        assert "harassment" in result["flags"]
        assert result["severity"] == "high"

    @pytest.mark.asyncio
    async def test_custom_safety_filters(self, ai_service):
        """Test custom safety filters for child content."""
        unsafe_phrases = [
            "give me your address",
            "don't tell your parents",
            "keep this secret",
            "send me a photo",
            "what's your phone number",
        ]

        for phrase in unsafe_phrases:
            result = await ai_service._apply_custom_safety_filters(phrase, 7)
            assert result["safe"] is False
            assert "custom_filter" in result["reason"]


class TestEmotionAnalysis:
    """Test emotion analysis functionality."""

    @pytest.mark.asyncio
    async def test_analyze_emotion_happy(self, ai_service):
        """Test emotion analysis for happy content."""
        text = "I'm so excited! Today was the best day ever!"

        emotion = await ai_service.analyze_emotion(text)

        assert emotion["primary_emotion"] == "joy"
        assert emotion["confidence"] > 0.7
        assert emotion["valence"] == "positive"

    @pytest.mark.asyncio
    async def test_analyze_emotion_sad(self, ai_service):
        """Test emotion analysis for sad content."""
        text = "I'm feeling really sad and lonely today."

        emotion = await ai_service.analyze_emotion(text)

        assert emotion["primary_emotion"] == "sadness"
        assert emotion["valence"] == "negative"
        assert "suggested_response_tone" in emotion

    @pytest.mark.asyncio
    async def test_analyze_emotion_mixed(self, ai_service):
        """Test emotion analysis for mixed emotions."""
        text = "I'm happy about my new toy but sad my friend moved away."

        emotion = await ai_service.analyze_emotion(text)

        assert "emotions" in emotion
        assert len(emotion["emotions"]) > 1
        assert emotion["valence"] == "mixed"


class TestPromptEngineering:
    """Test prompt engineering for different age groups."""

    def test_create_system_prompt_preschool(self, ai_service):
        """Test system prompt for preschool age."""
        prompt = ai_service._create_system_prompt(
            ChildAge.PRESCHOOL, "Timmy", {"interests": ["trucks", "colors"]}
        )

        assert "simple words" in prompt.lower()
        assert "3-5 year old" in prompt
        assert "Timmy" in prompt
        assert "trucks" in prompt

    def test_create_system_prompt_school_age(self, ai_service):
        """Test system prompt for school age."""
        prompt = ai_service._create_system_prompt(
            ChildAge.SCHOOL_AGE, "Sarah", {"interests": ["science", "reading"]}
        )

        assert "6-12 year old" in prompt
        assert "educational" in prompt.lower()
        assert "Sarah" in prompt
        assert "science" in prompt

    def test_create_system_prompt_with_personality(self, ai_service):
        """Test system prompt with personality traits."""
        prompt = ai_service._create_system_prompt(
            ChildAge.SCHOOL_AGE,
            "Alex",
            {
                "interests": ["art"],
                "personality": "shy and creative",
                "learning_style": "visual",
            },
        )

        assert "shy" in prompt
        assert "creative" in prompt
        assert "visual" in prompt.lower()


class TestErrorHandling:
    """Test error handling in AI service."""

    @pytest.mark.asyncio
    async def test_openai_api_error(
        self, ai_service, mock_openai_client, child_context
    ):
        """Test handling of OpenAI API errors."""
        ai_service.client = mock_openai_client

        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")

        response = await ai_service.generate_response(
            message="Hello",
            child_age=ChildAge.PRESCHOOL,
            child_context=child_context,
        )

        assert response.content is not None
        assert "I'm having trouble" in response.content
        assert response.safety_score == 1.0  # Fallback response is safe

    @pytest.mark.asyncio
    async def test_rate_limit_error(
        self, ai_service, mock_openai_client, child_context
    ):
        """Test handling of rate limit errors."""
        ai_service.client = mock_openai_client

        # Simulate rate limit error
        mock_openai_client.chat.completions.create.side_effect = Exception(
            "Rate limit exceeded"
        )

        response = await ai_service.generate_response(
            message="Hello",
            child_age=ChildAge.PRESCHOOL,
            child_context=child_context,
        )

        assert response.content is not None
        assert "try again" in response.content.lower()

    @pytest.mark.asyncio
    async def test_invalid_cache_data(self, ai_service, mock_redis):
        """Test handling of corrupted cache data."""
        ai_service.redis_cache = mock_redis

        # Return invalid JSON from cache
        mock_redis.get.return_value = "invalid json data"

        # Should handle gracefully and continue
        cache_result = await ai_service._get_from_cache("test_key")
        assert cache_result is None


class TestTokenManagement:
    """Test token counting and management."""

    def test_estimate_tokens(self, ai_service):
        """Test token estimation."""
        text = "This is a sample text for counting tokens."

        token_count = ai_service._estimate_tokens(text)

        assert isinstance(token_count, int)
        assert token_count > 0
        assert token_count < 50  # Reasonable for short text

    def test_truncate_context(self, ai_service):
        """Test context truncation for token limits."""
        # Create large context
        large_context = [
            {"role": "user", "content": "Long message " * 100},
            {"role": "assistant", "content": "Long response " * 100},
        ] * 10

        truncated = ai_service._truncate_context(large_context, max_tokens=1000)

        assert len(truncated) < len(large_context)
        assert ai_service._estimate_tokens(str(truncated)) <= 1000
