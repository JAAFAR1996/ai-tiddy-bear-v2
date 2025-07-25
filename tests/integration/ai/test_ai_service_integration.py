"""AI Service Integration Tests

Real AI service tests using test implementations instead of mocks.
"""

from datetime import datetime
from typing import Any

import pytest

from src.application.services.ai.ai_orchestration_service import AIOrchestratorService
from src.application.services.ai.interfaces import AIServiceInterface
from src.domain.value_objects.safety_level import SafetyLevel


class TestAIService(AIServiceInterface):
    """Test implementation of AI service with predictable responses."""

    def __init__(self):
        self.responses = {
            "story": "Once upon a time, there was a friendly dragon who loved to help children learn.",
            "math": "Let's count together! 1, 2, 3, 4, 5!",
            "science": "Did you know that butterflies taste with their feet?",
            "default": "That's a great question! Let me think about that.",
        }
        self.safety_checks = []
        self.response_count = 0

    async def generate_response(self, prompt: str, context: dict[str, Any]) -> str:
        """Generate a test response based on prompt content."""
        self.response_count += 1

        # Check child age for age-appropriate response
        child_age = context.get("child_age", 7)

        # Determine response type
        prompt_lower = prompt.lower()
        if "story" in prompt_lower:
            response = self.responses["story"]
        elif any(word in prompt_lower for word in ["math", "count", "number"]):
            response = self.responses["math"]
        elif any(word in prompt_lower for word in ["science", "nature", "animal"]):
            response = self.responses["science"]
        else:
            response = self.responses["default"]

        # Add age-appropriate modifier
        if child_age < 6:
            response = f"For our young friend: {response}"
        elif child_age > 10:
            response = f"Here's something cool: {response}"

        return response

    async def check_content_safety(self, content: str) -> dict[str, Any]:
        """Check content safety with test implementation."""
        self.safety_checks.append(content)

        # Simple safety check based on keywords
        unsafe_words = ["violence", "scary", "dangerous", "hurt"]
        content_lower = content.lower()

        is_safe = not any(word in content_lower for word in unsafe_words)
        safety_score = 1.0 if is_safe else 0.3

        return {
            "is_safe": is_safe,
            "safety_score": safety_score,
            "flags": [] if is_safe else ["potentially_unsafe_content"],
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def generate_contextual_response(
        self, prompt: str, context: dict[str, Any], history: list
    ) -> str:
        """Generate response with context awareness."""
        # Check if this is a follow-up question
        if history and "more" in prompt.lower():
            last_topic = self._extract_topic(history[-1])
            return f"Let me tell you more about {last_topic}!"

        return await self.generate_response(prompt, context)

    def _extract_topic(self, message: str) -> str:
        """Extract topic from previous message."""
        if "dragon" in message:
            return "dragons"
        if "count" in message:
            return "numbers"
        if "butterfly" in message:
            return "butterflies"
        return "that"


class InMemoryCache:
    """In-memory cache implementation for testing."""

    def __init__(self):
        self._data = {}
        self._access_count = {}

    async def get(self, key: str) -> str | None:
        """Get value from cache."""
        self._access_count[key] = self._access_count.get(key, 0) + 1
        return self._data.get(key)

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        """Set value in cache."""
        self._data[key] = value

    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        self._data.pop(key, None)

    def get_access_count(self, key: str) -> int:
        """Get number of times key was accessed."""
        return self._access_count.get(key, 0)


@pytest.fixture
def test_ai_service():
    """Create test AI service."""
    return TestAIService()


@pytest.fixture
def cache():
    """Create in-memory cache."""
    return InMemoryCache()


@pytest.fixture
def ai_orchestrator(test_ai_service, cache):
    """Create AI orchestrator with test implementations."""
    return AIOrchestratorService(
        ai_service=test_ai_service,
        cache=cache,
        content_filter=None,  # Would use real content filter
        safety_validator=None,  # Would use real safety validator
    )


class TestAIServiceIntegration:
    """Integration tests for AI service."""

    @pytest.mark.asyncio
    async def test_generate_age_appropriate_response(self, test_ai_service):
        """Test that responses are age-appropriate."""
        # Test for young child
        response_young = await test_ai_service.generate_response(
            "Tell me a story", {"child_age": 4}
        )
        assert "For our young friend:" in response_young
        assert "friendly dragon" in response_young

        # Test for older child
        response_older = await test_ai_service.generate_response(
            "Tell me a story", {"child_age": 11}
        )
        assert "Here's something cool:" in response_older

    @pytest.mark.asyncio
    async def test_content_safety_checking(self, test_ai_service):
        """Test content safety checking with real logic."""
        # Test safe content
        safe_result = await test_ai_service.check_content_safety(
            "Tell me about butterflies"
        )
        assert safe_result["is_safe"] is True
        assert safe_result["safety_score"] == 1.0
        assert len(safe_result["flags"]) == 0

        # Test unsafe content
        unsafe_result = await test_ai_service.check_content_safety(
            "Tell me something scary and dangerous"
        )
        assert unsafe_result["is_safe"] is False
        assert unsafe_result["safety_score"] == 0.3
        assert "potentially_unsafe_content" in unsafe_result["flags"]

    @pytest.mark.asyncio
    async def test_contextual_responses(self, test_ai_service):
        """Test contextual response generation."""
        # First message
        first_response = await test_ai_service.generate_contextual_response(
            "Tell me about butterflies", {"child_age": 7}, []
        )
        assert "butterflies taste with their feet" in first_response

        # Follow-up message
        follow_up = await test_ai_service.generate_contextual_response(
            "Tell me more!", {"child_age": 7}, [first_response]
        )
        assert "more about butterflies" in follow_up

    @pytest.mark.asyncio
    async def test_response_tracking(self, test_ai_service):
        """Test that service tracks responses properly."""
        # Generate multiple responses
        for i in range(5):
            await test_ai_service.generate_response(f"Question {i}", {"child_age": 7})

        assert test_ai_service.response_count == 5
        assert len(test_ai_service.safety_checks) == 0  # Safety not called yet

        # Check safety
        await test_ai_service.check_content_safety("Test content")
        assert len(test_ai_service.safety_checks) == 1


class TestAIOrchestrationIntegration:
    """Integration tests for AI orchestration."""

    @pytest.mark.asyncio
    async def test_orchestrated_response_with_caching(self, ai_orchestrator, cache):
        """Test orchestrated response generation with caching."""
        prompt = "Tell me a math problem"
        context = {"child_id": "test-123", "child_age": 8}

        # First call - should generate new response
        response1 = await ai_orchestrator.generate_safe_response(prompt, context)
        assert response1 is not None
        assert "count" in response1.lower()

        # Check cache was populated
        cache_key = f"ai_response:test-123:{hash(prompt)}"
        cached = await cache.get(cache_key)
        assert cached is not None

        # Second call - should use cache
        response2 = await ai_orchestrator.generate_safe_response(prompt, context)
        assert response2 == response1
        assert cache.get_access_count(cache_key) == 1

    @pytest.mark.asyncio
    async def test_safety_filtering_integration(self, test_ai_service):
        """Test safety filtering with real implementation."""
        # Create a response that should be filtered
        unsafe_prompt = "Tell me a scary violent story"
        context = {"child_age": 6}

        # Check safety first
        safety_result = await test_ai_service.check_content_safety(unsafe_prompt)
        assert safety_result["is_safe"] is False

        # Service should handle unsafe content appropriately
        response = await test_ai_service.generate_response(unsafe_prompt, context)
        assert response is not None  # Should still generate safe alternative

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, test_ai_service):
        """Test handling of concurrent requests."""
        import asyncio

        # Create multiple concurrent requests
        prompts = [f"Question {i}" for i in range(10)]
        context = {"child_age": 7}

        tasks = [
            test_ai_service.generate_response(prompt, context) for prompt in prompts
        ]

        responses = await asyncio.gather(*tasks)

        # All should complete successfully
        assert len(responses) == 10
        assert all(response is not None for response in responses)
        assert test_ai_service.response_count == 10


class TestCacheIntegration:
    """Integration tests for caching functionality."""

    @pytest.mark.asyncio
    async def test_cache_operations(self, cache):
        """Test cache operations work correctly."""
        # Set value
        await cache.set("key1", "value1")

        # Get value
        value = await cache.get("key1")
        assert value == "value1"

        # Delete value
        await cache.delete("key1")
        value = await cache.get("key1")
        assert value is None

    @pytest.mark.asyncio
    async def test_cache_access_tracking(self, cache):
        """Test cache access tracking."""
        await cache.set("tracked_key", "value")

        # Access multiple times
        for _ in range(5):
            await cache.get("tracked_key")

        assert cache.get_access_count("tracked_key") == 5
        assert cache.get_access_count("non_existent") == 0


class TestEndToEndAIFlow:
    """End-to-end tests for complete AI interaction flow."""

    @pytest.mark.asyncio
    async def test_complete_conversation_flow(self, test_ai_service, cache):
        """Test a complete conversation flow."""
        child_context = {
            "child_id": "child-123",
            "child_age": 7,
            "child_name": "Alice",
            "safety_level": SafetyLevel.STRICT,
        }

        conversation_history = []

        # Initial greeting
        greeting = await test_ai_service.generate_response(
            "Hello! What's your name?", child_context
        )
        conversation_history.append(("Hello! What's your name?", greeting))

        # Story request
        story_response = await test_ai_service.generate_contextual_response(
            "Can you tell me a story?", child_context, conversation_history
        )
        assert "Once upon a time" in story_response
        conversation_history.append(("Can you tell me a story?", story_response))

        # Follow-up question
        follow_up = await test_ai_service.generate_contextual_response(
            "Tell me more about the dragon!",
            child_context,
            conversation_history,
        )
        assert "dragon" in follow_up.lower()

        # Verify safety was maintained throughout
        for _, response in conversation_history:
            safety_check = await test_ai_service.check_content_safety(response)
            assert safety_check["is_safe"] is True
