"""Production Real AI Service for AI Teddy Bear
Enterprise-grade AI service with OpenAI GPT-4 integration and comprehensive safety filtering.
Refactored to be under 300 lines by extracting components.
"""

from fastapi import Depends

# Production-only imports - no fallbacks allowed
try:
    import redis.asyncio as redis
    from openai import AsyncOpenAI
except ImportError as e:
    logger.critical(f"CRITICAL ERROR: Required dependencies missing: {e}")
    logger.critical("Install required dependencies: pip install openai pydantic redis")
    raise ImportError("Missing required AI dependencies") from e

from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="ai")


class ProductionAIService:
    """Production-grade AI service with real OpenAI GPT-4 integration.
    Features:
    - Real OpenAI GPT-4 API integration
    - Multi-layer content safety filtering
    - Age-appropriate response generation
    - COPPA compliance (children 13 and under)
    - Redis caching for performance
    - Comprehensive error handling
    - Performance monitoring.
    """

    def __init__(self, settings: Settings = Depends(get_settings)) -> None:
        self.settings = settings
        openai_api_key = self.settings.ai.OPENAI_API_KEY
        if not openai_api_key:
            raise ValueError("OpenAI API key is required for production use")
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.redis_cache = redis.from_url(
            self.settings.redis.REDIS_URL,
            decode_responses=True,
        )
        # Initialize components
        self.safety_analyzer = SafetyAnalyzer(self.client)
        self.prompt_builder = PromptBuilder()
        # AI model configuration
        self.model = "gpt-4-turbo-preview"
        self.max_tokens = 200
        self.temperature = 0.7
        logger.info("Production AI Service initialized")
