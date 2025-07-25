import logging
from datetime import datetime
from typing import Any

from src.application.dto.ai_response import AIResponse

from .utils import AIServiceUtils

try:
    from openai import AsyncOpenAI
except ImportError as e:
    # F821: يجب تعريف get_logger بشكل صحيح
    # الحل: استخدم logging مباشرة أو import من logging_config لو متوفر
    logger = logging.getLogger(__name__)
    logger.error(f"CRITICAL ERROR: Required dependencies missing: {e}")
    logger.error("Install required dependencies: pip install openai pydantic")
    raise ImportError(f"Missing AI service dependencies: {e}") from e

"""AI Teddy Bear Main Service - Production Implementation
Enterprise-grade AI service for child-safe interactions following hexagonal architecture."""

logger = logging.getLogger(__name__)


class AITeddyBearService:
    """Production-grade AI service for child-safe interactions.
    Features:
    - Real OpenAI GPT-4 integration
    - Multi-layer content filtering
    - Age-appropriate response generation
    - COPPA compliance
    - Performance monitoring
    - Comprehensive error handling.
    """

    def __init__(self, openai_api_key: str, redis_cache=None, settings=None) -> None:
        if not openai_api_key:
            raise ValueError("OpenAI API key is required for production use")
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.redis_cache = redis_cache
        self.settings = settings
        # AI model configuration
        self.model = "gpt-4-turbo-preview"
        self.max_tokens = 200
        self.temperature = 0.7
        # Safety configuration
        self.safety_threshold = 0.9
        self.banned_topics = [
            "violence",
            "adult content",
            "drugs",
            "alcohol",
            "weapons",
            "inappropriate language",
            "scary content",
            "personal information",
        ]
        logger.info("AI Teddy Bear Service initialized with production configuration")

    async def generate_response(
        self,
        message: str,
        child_age: int,
        child_name: str,
        context: list[dict[str, str]] | None = None,
        parent_guidelines: str | None = None,
    ) -> AIResponse:
        """Generate safe, age-appropriate AI response."""
        start_time = datetime.utcnow()
        # Input validation
        if child_age > 13:
            raise ValueError(
                "Service only available for children 13 and under (COPPA compliance)",
            )
        if not message or not message.strip():
            raise ValueError("Message cannot be empty")
        # Check cache first
        cache_key = self._generate_cache_key(message, child_age, child_name)
        if self.redis_cache:
            cached_response = await self._get_cached_response(cache_key)
            if cached_response:
                cached_response.cached = True
                return cached_response

        try:
            # Content moderation check
            moderation_result = await self._moderate_content(message)
            if not moderation_result["safe"]:
                raise ValueError(
                    f"Content flagged by moderation: "
                    f"{moderation_result['categories']}",
                )
            # Generate age-appropriate system prompt
            system_prompt = self._create_system_prompt(
                child_age,
                child_name,
                parent_guidelines,
            )
            # Prepare conversation messages
            messages = [{"role": "system", "content": system_prompt}]
            # Add context if provided
            if context:
                for ctx in context[-5:]:  # Last 5 messages for context
                    messages.append(ctx)
            messages.append({"role": "user", "content": message})
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                presence_penalty=0.6,
                frequency_penalty=0.5,
            )
            ai_content = response.choices[0].message.content
            # Post-process and validate response
            processed_response = await self._post_process_response(
                ai_content,
                child_age,
                moderation_result,
            )
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            processed_response.processing_time = processing_time
            # Cache the response
            if self.redis_cache:
                await self._cache_response(cache_key, processed_response)
            logger.info(
                "AI response generated for child age %s, processing time: %.3fs",
                child_age,
                processing_time,
            )
            return processed_response
        except Exception as e:
            logger.error(f"AI service error: {e}")
            # Return safe fallback response
            return await self._get_fallback_response(child_name, child_age)

    async def _moderate_content(self, content: str) -> dict[str, Any]:
        """Use OpenAI moderation API to check content safety."""
        try:
            moderation = await self.client.moderations.create(input=content)
            result = moderation.results[0]
            return {
                "safe": not result.flagged,
                "categories": [
                    cat
                    for cat, flagged in result.categories.model_dump().items()
                    if flagged
                ],
                "scores": result.category_scores.model_dump(),
            }
        except Exception as e:
            logger.error(f"Moderation API error: {e}")
            # Fail safe - assume content is unsafe if moderation fails
            return {
                "safe": False,
                "categories": ["moderation_error"],
                "scores": {},
            }

    def _create_system_prompt(
        self,
        child_age: int,
        child_name: str,
        parent_guidelines: str | None = None,
    ) -> str:
        """Create age-appropriate system prompt."""
        age_group = self._get_age_group(child_age)
        base_prompt = (
            f"You are a friendly, caring AI teddy bear speaking to {child_name}, who is {child_age} years old.\n"
            "CRITICAL SAFETY RULES:\n"
            f"- Use age-appropriate language for {age_group} children\n"
            "- Keep responses positive, educational, and fun\n"
            "- Never discuss inappropriate topics (violence, adult content, personal information)\n"
            "- Encourage creativity, learning, and positive values\n"
            "- Keep responses under 150 words\n"
            "- Use simple, clear language\n"
            "- Be encouraging and supportive\n"
            "CONVERSATION STYLE:\n"
            "- Warm and caring like a favorite teddy bear\n"
            "- Curious about the child's interests\n"
            "- Educational but fun\n"
            "- Encouraging and confidence-building"
        )
        if parent_guidelines:
            base_prompt += f"\n\nPARENT GUIDELINES:\n{parent_guidelines}"
        return base_prompt

    async def _post_process_response(
        self,
        content: str,
        child_age: int,
        moderation_result: dict,
    ) -> AIResponse:
        """Process and validate AI response."""
        # Content safety analysis
        safety_score = self._calculate_safety_score(content, moderation_result)
        age_appropriate = self._check_age_appropriateness(content, child_age)
        sentiment = self._analyze_sentiment(content)
        topics = self._extract_topics(content)
        # Additional safety checks
        moderation_flags = []
        if safety_score < self.safety_threshold:
            moderation_flags.append("low_safety_score")
        if not age_appropriate:
            moderation_flags.append("age_inappropriate")
        # Clean content
        cleaned_content = self._clean_content(content)
        return AIResponse(
            content=cleaned_content,
            safety_score=safety_score,
            age_appropriate=age_appropriate,
            sentiment=sentiment,
            topics=topics,
            processing_time=0.0,  # Will be set by caller
            moderation_flags=moderation_flags,
        )

    def _calculate_safety_score(self, content: str, moderation_result: dict) -> float:
        """Calculate content safety score."""
        return AIServiceUtils.calculate_safety_score(
            content,
            moderation_result,
            self.banned_topics,
        )

    def _check_age_appropriateness(self, content: str, age: int) -> bool:
        """Check if content is appropriate for child's age."""
        return AIServiceUtils.check_age_appropriateness(content, age)

    def _analyze_sentiment(self, content: str) -> str:
        """Simple sentiment analysis."""
        return AIServiceUtils.analyze_sentiment(content)

    def _extract_topics(self, content: str) -> list[str]:
        """Extract main topics from content."""
        return AIServiceUtils.extract_topics(content)

    def _clean_content(self, content: str) -> str:
        """Clean and sanitize content."""
        return AIServiceUtils.clean_content(content)

    def _get_age_group(self, age: int) -> str:
        """Get age group classification."""
        return AIServiceUtils.get_age_group(age)

    def _generate_cache_key(self, message: str, age: int, name: str) -> str:
        """Generate cache key for response."""
        return AIServiceUtils.generate_cache_key(message, age, name)

    async def _get_cached_response(self, cache_key: str) -> AIResponse | None:
        """Get cached response if available."""
        try:
            if self.redis_cache:
                cached_data = await self.redis_cache.get(cache_key)
                if cached_data:
                    return AIResponse.model_validate_json(cached_data)
        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")
        return None

    async def _cache_response(self, cache_key: str, response: AIResponse) -> None:
        """Cache the response for future use."""
        try:
            if self.redis_cache:
                # Cache for 1 hour
                await self.redis_cache.setex(
                    cache_key,
                    3600,
                    response.model_dump_json(),
                )
        except Exception as e:
            logger.warning(f"Cache storage error: {e}")

    async def _get_fallback_response(
        self,
        child_name: str,
        child_age: int,
    ) -> AIResponse:
        """Get safe fallback response when AI service fails."""
        return AIServiceUtils.get_fallback_response(child_name, child_age)
