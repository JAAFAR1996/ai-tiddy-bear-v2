"""
Production ChatGPT API Client with Child Safety Filtering

Enterprise-grade OpenAI integration for AI Teddy Bear
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
import asyncio
import json
import logging
import os
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="infrastructure")

# Production-only imports - no fallbacks allowed
try:
    from openai import AsyncOpenAI
    import openai
except ImportError as e:
    logger.critical(f"CRITICAL ERROR: OpenAI library is required for production use: {e}")
    logger.critical("Install required dependencies: pip install openai")
    raise ImportError(f"Missing required dependency: openai") from e

from src.infrastructure.config.settings import get_settings

class ProductionChatGPTClient:
    """Production ChatGPT client with comprehensive child safety filtering."""

    def __init__(self, api_key: str = None) -> None:
        self.settings = get_settings()
        self.api_key = api_key or self.settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required for production use")
        self.client = AsyncOpenAI(api_key=self.api_key)

        # Child safety configuration
        self.child_safety_rules = [
            "Always use child-friendly language",
            "Avoid scary or violent content",
            "Keep responses age-appropriate",
            "Encourage learning and creativity",
            "Be supportive and positive",
            "Don't discuss adult topics",
            "Redirect inappropriate questions to safe topics"
        ]

        # Forbidden content for children
        self.forbidden_words = [
            "violence", "weapon", "kill", "death", "blood", "scary",
            "nightmare", "monster", "ghost", "demon", "hell", "damn",
            "adult", "sex", "drug", "alcohol", "cigarette", "smoke"
        ]

        # Safe topics for children
        self.safe_topics = [
            "animals", "nature", "friendship", "family", "school", "hobbies",
            "science", "space", "art", "music", "stories", "adventures"
        ]

    async def get_chat_completion(
        self,
        messages: List[Dict[str, str]],
        child_id: str,
        temperature: float = 0.7,
        max_tokens: int = 150
    ) -> str:
        """
        Get a chat completion from OpenAI with child safety filters.

        Args:
            messages: A list of messages in the conversation.
            child_id: The ID of the child for logging and context.
            temperature: The sampling temperature for the model.
            max_tokens: The maximum number of tokens to generate.

        Returns:
            The content of the chat completion.
        """
        # 1. Pre-filter user input for immediate safety concerns
        last_user_message = messages[-1]["content"]
        if self._is_content_forbidden(last_user_message):
            logger.warning(
                f"Forbidden content detected in input for child {child_id}",
                extra={"child_id": child_id, "message": last_user_message}
            )
            return self._get_safe_redirect_response()

        # 2. Add system prompt with child safety rules
        system_prompt = (
            "You are a friendly, safe, and supportive AI Teddy Bear for a young child. "
            "Your primary goal is to provide a positive and educational experience. "
            "Follow these rules strictly:\n" +
            "\n".join(f"- {rule}" for rule in self.child_safety_rules)
        )
        
        # Add a specific instruction to guide the model's tone and persona
        system_prompt += "\n\nRemember to be gentle, patient, and encouraging in all your responses."

        # Construct the full list of messages for the API call
        api_messages = [{"role": "system", "content": system_prompt}] + messages

        try:
            response = await self.client.chat.completions.create(
                model=self.settings.OPENAI_MODEL,
                messages=api_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                # Add safety settings if the API supports it (this is a conceptual example)
                # safety_settings={"harm_category": "HARASSMENT", "threshold": "BLOCK_NONE"}
            )
            
            generated_text = response.choices[0].message.content.strip()

            # 3. Post-filter the generated response for safety
            if self._is_content_forbidden(generated_text):
                logger.error(
                    f"OpenAI response contained forbidden content for child {child_id}",
                    extra={"child_id": child_id, "generated_text": generated_text}
                )
                return self._get_safe_redirect_response()

            return generated_text

        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}", extra={"child_id": child_id})
            raise ConnectionError(f"Failed to connect to OpenAI: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error in get_chat_completion: {e}", extra={"child_id": child_id})
            raise

    def _is_content_forbidden(self, text: str) -> bool:
        """Check if text contains forbidden words."""
        lower_text = text.lower()
        return any(word in lower_text for word in self.forbidden_words)

    def _get_safe_redirect_response(self) -> str:
        """Provide a safe, generic response that redirects the conversation."""
        # Choose a random safe topic to redirect to
        safe_topic = asyncio.run(self._get_random_safe_topic())
        return f"That's a grown-up question! Let's talk about something fun, like {safe_topic}. What do you like about {safe_topic}?"

    async def _get_random_safe_topic(self) -> str:
        """Asynchronously get a random safe topic."""
        # In a real application, this could involve more complex logic
        # or even another model call to get a contextually relevant topic.
        import random
        return random.choice(self.safe_topics)

# Example usage (for testing or demonstration)
async def main():
    # This requires OPENAI_API_KEY to be set in the environment or a .env file
    try:
        client = ProductionChatGPTClient()
        messages = [
            {"role": "user", "content": "Tell me a story about a friendly dragon."}
        ]
        response = await client.get_chat_completion(messages, child_id="test_child_123")
        print(f"AI Teddy Bear says: {response}")

        # Example of a potentially unsafe question
        messages_unsafe = [
            {"role": "user", "content": "What happens when people get into a fight?"}
        ]
        response_unsafe = await client.get_chat_completion(messages_unsafe, child_id="test_child_456")
        print(f"AI Teddy Bear (safe redirect): {response_unsafe}")

    except (ValueError, ImportError) as e:
        logger.error(f"Failed to run example: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during the example run: {e}")

if __name__ == "__main__":
    # To run this, you need to have your environment configured.
    # For example, create a .env file with:
    # OPENAI_API_KEY="your_key_here"
    # OPENAI_MODEL="gpt-3.5-turbo"
    
    # Note: Running this directly might require additional setup for the settings loader.
    # Consider running this as part of a larger application context.
    pass