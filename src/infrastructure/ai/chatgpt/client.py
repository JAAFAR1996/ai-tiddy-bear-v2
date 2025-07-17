"""
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import logging
import os
"""

ChatGPT Client for AI Teddy Bear - Main Client Class
"""

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError as e:
    # Production environment MUST have OpenAI dependency
    raise ImportError(
        "CRITICAL: OpenAI package is required for production deployment. "
        "Install with: pip install openai"
    ) from e

# Constants for ChatGPT configuration
DEFAULT_MAX_TOKENS = 200
DEFAULT_TEMPERATURE = 0.7
DEFAULT_PRESENCE_PENALTY = 0.1
DEFAULT_FREQUENCY_PENALTY = 0.1
MAX_RESPONSE_WORDS = 150

from src.infrastructure.logging_config import get_logger
logger = get_logger(__name__, component="infrastructure")

from .safety_filter import SafetyFilter
from .response_enhancer import ResponseEnhancer
from .fallback_responses import FallbackResponseGenerator

class ChatGPTClient:
    """ChatGPT client with child safety filtering and content moderation."""
    def __init__(self, api_key: str = None) -> None:
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "CRITICAL: OpenAI API key is required for production deployment. "
                "Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )
        # Initialize OpenAI client - no fallback in production
        self.client = OpenAI(api_key=self.api_key)
        # Initialize safety components
        self.safety_filter = SafetyFilter()
        self.response_enhancer = ResponseEnhancer()
        self.fallback_generator = FallbackResponseGenerator()

    async def generate_child_safe_response(
                                         self,
                                         message: str,
                                         child_age: int,
                                         child_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate child - safe response from ChatGPT with content filtering."""
        try:
            # Create child-safe system prompt
            system_prompt = self._create_child_safe_system_prompt(child_age, child_preferences)
            # Check message safety
            safety_check = self.safety_filter.analyze_message_safety(message)
            if not safety_check["safe"]:
                return await self.fallback_generator.generate_safety_redirect_response(message, child_age)
            # Create safe message
            safe_message = self.safety_filter.sanitize_message(message)
            # Call ChatGPT
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": safe_message}
                ],
                max_tokens=DEFAULT_MAX_TOKENS,
                temperature=DEFAULT_TEMPERATURE,
                presence_penalty=DEFAULT_PRESENCE_PENALTY,
                frequency_penalty=DEFAULT_FREQUENCY_PENALTY
            )
            raw_response = response.choices[0].message.content
            # Check response safety
            response_safety = self.safety_filter.analyze_response_safety(raw_response)
            if not response_safety["safe"]:
                return await self.fallback_generator.generate_fallback_response(message, child_age, child_preferences)
            # Enhance response for children
            enhanced_response = self.response_enhancer.enhance_response_for_children(raw_response, child_age, child_preferences)
            return {
                "response": enhanced_response,
                "emotion": self.response_enhancer.detect_emotion(enhanced_response),
                "safety_analysis": response_safety,
                "age_appropriate": True,
                "source": "chatgpt",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"ChatGPT API error: {e}")
            return await self.fallback_generator.generate_fallback_response(message, child_age, child_preferences)

    def _create_child_safe_system_prompt(self, child_age: int, preferences: Dict[str, Any] = None) -> str:
        """Create child - safe system prompt with age - appropriate guidelines."""
        preferences = preferences or {}
        interests = preferences.get("interests", ["animals", "stories"])
        favorite_character = preferences.get("favorite_character", "friendly teddy bear")
        age_guidance = {
            3: "Use very simple words and short sentences. Focus on basic concepts.",
            4: "Use simple words and short sentences. Include fun sounds and repetition.",
            5: "Use simple vocabulary. Include basic learning concepts like colors and numbers.",
            6: "Use age-appropriate vocabulary. Include educational content about nature and friendship.",
            7: "Use clear, friendly language. Include more detailed explanations about the world.",
            8: "Use engaging language. Include problem-solving and creativity encouragement.",
            9: "Use varied vocabulary. Include more complex concepts explained simply.",
            10: "Use rich vocabulary. Include critical thinking and exploration topics."
        }
        age_specific = age_guidance.get(child_age, age_guidance[6])
        return f'''You are a friendly, caring AI assistant designed specifically for children aged {child_age}.

SAFETY RULES (NEVER BREAK THESE):
- Always use child-friendly, positive language
- Never discuss violence, scary content, or adult topics
- Keep all responses age-appropriate for a {child_age}-year-old
- If asked about inappropriate topics, redirect to safe subjects
- Be encouraging, supportive, and educational
- Focus on learning, creativity, and fun

CHILD PROFILE:
- Age: {child_age} years old
- Interests: {', '.join(interests)}
- Favorite character: {favorite_character}

RESPONSE GUIDELINES:
- {age_specific}
- Include the child's interests when possible
- Use the favorite character in examples if appropriate
- Keep responses under {MAX_RESPONSE_WORDS} words
- End with a friendly question or encouragement
- Be warm, caring, and patient

FORBIDDEN TOPICS:
- Violence, weapons, fighting, death
- Scary content, monsters, nightmares
- Adult topics, relationships, mature content
- Negative emotions without positive resolution
- Dangerous activities or risky behavior

SAFE TOPICS TO FOCUS ON:
- Animals, nature, friendship, family
- Learning, school, books, art, music
- Games, sports, healthy activities
- Colors, shapes, numbers, letters
- Stories, imagination, creativity

Remember: You are talking to a {child_age}-year-old child. Be their friendly, safe, and educational companion.'''