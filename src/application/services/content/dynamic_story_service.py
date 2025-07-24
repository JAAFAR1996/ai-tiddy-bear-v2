"""Provides services for generating dynamic and personalized stories.

This service leverages an AI provider to create unique stories tailored to
a child's name, age, preferences, and chosen theme. It aims to enhance
the interactive experience by offering engaging and relevant narrative content.
"""

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
        child_id: str | None = None,
        conversation_history: list | None = None,
    ) -> str:
        """Generates a personalized story for a child (production implementation).

        Args:
            child_name: The name of the child.
            child_age: The age of the child.
            child_preferences: The child's preferences.
            theme: The theme of the story (e.g., "adventure", "fantasy").
            length: The desired length of the story ("short", "medium", "long").
            child_id: (اختياري) معرف الطفل الحقيقي إذا توفر.
            conversation_history: (اختياري) سجل المحادثة الفعلي إذا توفر.

        Returns:
            The generated story content.
        """
        if not hasattr(self.ai_provider, "generate_response") or not callable(
            self.ai_provider.generate_response
        ):
            raise NotImplementedError(
                "AIProvider must implement a real generate_response method for story generation."
            )
        prompt = (
            f"Generate a {length} story for a {child_age}-year-old named {child_name}. "
            f"The story should be about {theme}. "
            f"Incorporate the child's favorite topics: "
            f"{', '.join(child_preferences.favorite_topics)}. "
            f"The story should be in {child_preferences.language} and "
            f"suitable for their learning level "
            f"{child_preferences.learning_level}."
        )
        story_content = await self.ai_provider.generate_response(
            child_id=child_id,
            conversation_history=(
                conversation_history if conversation_history is not None else []
            ),
            current_input=prompt,
            child_preferences=child_preferences,
        )
        return story_content
