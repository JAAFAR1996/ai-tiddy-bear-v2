"""
Provides services for generating dynamic and personalized content.

This service leverages external AI capabilities to create tailored stories,
educational content, and interactive experiences for children based on their
profiles and preferences. It aims to make interactions more engaging and
relevant to each child's unique needs.
"""

from typing import Any, Dict, List

from src.application.interfaces.read_model_interfaces import (
    IExternalAPIClient,
    get_external_api_client,
)
from src.domain.entities.child_profile import ChildProfile


class DynamicContentService:
    """Service for generating dynamic personalized content for children."""

    def __init__(self, api_client: IExternalAPIClient = None) -> None:
        """
        Initializes the dynamic content service.

        Args:
            api_client: An optional external API client for content generation.
                        Defaults to an OpenAI client if not provided.
        """
        self.api_client = api_client or get_external_api_client("openai")

    async def generate_personalized_story(
        self, child_profile: ChildProfile, theme: str, length: str = "short"
    ) -> str:
        """
        Generates a personalized story for a child.

        Args:
            child_profile: The profile of the child.
            theme: The theme of the story.
            length: The desired length of the story (e.g., "short", "medium", "long").

        Returns:
            The generated personalized story.
        """
        prompt = (
            f"Generate a {length} story for a child named {child_profile.name} "
            f"who is {child_profile.age} years old. "
            f"The story should be about {theme}. "
            f"Incorporate the child's preferences: {child_profile.preferences}. "
            "Ensure the language is age-appropriate and positive."
        )
        # Assuming a dummy conversation history for story generation
        conversation_history = []
        current_input = prompt
        response_data = await self.api_client.make_request(
            "chat/completions",
            {"messages": [{"role": "user", "content": current_input}]},
        )
        story = response_data.get("response", current_input)
        return story

    async def generate_educational_content(
        self, child_profile: ChildProfile, topic: str
    ) -> str:
        """
        Generates educational content for a child.

        Args:
            child_profile: The profile of the child.
            topic: The topic for the educational content.

        Returns:
            The generated educational text.
        """
        prompt = (
            f"Create a short educational explanation about {topic} for a "
            f"{child_profile.age}-year-old child named {child_profile.name}. "
            "Keep it simple, engaging, and easy to understand."
        )
        conversation_history = []
        current_input = prompt
        educational_text = await self.api_client.generate_response(
            child_profile.id, conversation_history, current_input
        )
        return educational_text

    async def get_interactive_activity(
        self, child_profile: ChildProfile, activity_type: str
    ) -> Dict[str, Any]:
        """
        Generates an interactive activity for a child.

        Args:
            child_profile: The profile of the child.
            activity_type: The type of activity to generate (e.g., "quiz", "puzzle").

        Returns:
            A dictionary representing the interactive activity.
        """
        prompt = (
            f"Create a {activity_type} for a child named {child_profile.name} "
            f"who is {child_profile.age} years old. "
            f"The activity should be engaging and appropriate for their age."
        )
        conversation_history = []
        current_input = prompt
        activity_data = await self.api_client.make_request(
            "interactive_activities",
            {"messages": [{"role": "user", "content": current_input}]},
        )
        return activity_data.get("response", {})
