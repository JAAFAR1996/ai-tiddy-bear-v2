"""
Provides services for generating dynamic and personalized stories.

This service leverages an AI provider to create unique stories tailored to
a child's name, age, preferences, and chosen theme. It aims to enhance
the interactive experience by offering engaging and relevant narrative content.
"""

from typing import Any, Dict, List

from src.application.interfaces.ai_provider import AIProvider
from src.domain.value_objects.child_preferences import ChildPreferences


class DynamicStoryService:
    """Service for generating dynamic personalized stories."""

    def __init__(self, ai_provider: AIProvider) -> None:
        """Initializes the dynamic story service.

        Args:
            ai_provider: The AI provider to use for story generation.
        """
        self.ai_provider = ai_provider

    async def generate_story(
        self,
        child_name: str,
        child_age: int,
        child_preferences: ChildPreferences,
        theme: str = "adventure",
        length: str = "short",  # short, medium, long
    ) -> str:
        """
        Generates a personalized story for a child.

        Args:
            child_name: The name of the child.
            child_age: The age of the child.
            child_preferences: The child's preferences.
            theme: The theme of the story (e.g., "adventure", "fantasy").
            length: The desired length of the story ("short", "medium", "long").

        Returns:
            The generated story content.
        """
        prompt = (
            f"Generate a {length} story for a {child_age}-year-old named {child_name}. "
            f"The story should be about {theme}. "
            f"Incorporate the child's favorite topics: {', '.join(child_preferences.favorite_topics)}. "
            f"The story should be in {child_preferences.language} and suitable for their learning level {child_preferences.learning_level}."
        )
        # Use a dummy child_id and conversation_history for story generation, as it's not a direct conversation
        # The AIProvider interface expects these, but they might not be strictly relevant for story generation.
        # A more refined AIProvider might have a separate method for creative
        # content generation.
        story_content = await self.ai_provider.generate_response(
            child_id=None,  # Dummy ID
            conversation_history=[],  # No conversation history for story generation
            current_input=prompt,
            child_preferences=child_preferences,
        )
        return story_content
