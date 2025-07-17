"""Provides services for generating dynamic and personalized content.

This service leverages external AI capabilities to create tailored stories,
educational content, and interactive experiences for children based on their
profiles and preferences. It aims to make interactions more engaging and
relevant to each child's unique needs.
"""

from typing import Any

from src.application.interfaces.read_model_interfaces import (
    IExternalAPIClient,
    get_external_api_client,
)
from src.application.interfaces.safety_monitor import SafetyMonitor
from src.domain.entities.child_profile import ChildProfile
from src.domain.safety.models import SafetyLevel
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="dynamic_content_service")


class DynamicContentService:
    """Service for generating dynamic personalized content for children."""

    def __init__(
        self,
        api_client: IExternalAPIClient = None,
        safety_monitor: SafetyMonitor = None,
    ) -> None:
        """Initializes the dynamic content service.

        Args:
            api_client: An optional external API client for content generation.
                        Defaults to an OpenAI client if not provided.
            safety_monitor: The SafetyMonitor instance for content validation.

        """
        self.api_client = api_client or get_external_api_client("openai")
        self.safety_monitor = safety_monitor
        self.logger = logger

    async def generate_personalized_story(
        self,
        child_profile: ChildProfile,
        theme: str,
        length: str = "short",
    ) -> str:
        """Generates a personalized story for a child.

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
        current_input = prompt
        response_data = await self.api_client.make_request(
            "chat/completions",
            {"messages": [{"role": "user", "content": current_input}]},
        )
        story = response_data.get("response", current_input)

        # Validate generated content
        if self.safety_monitor:
            safety_result = await self.safety_monitor.check_content_safety(
                story,
                child_age=child_profile.age,
            )
            if safety_result.risk_level in [
                SafetyLevel.UNSAFE,
                SafetyLevel.POTENTIALLY_UNSAFE,
            ]:
                self.logger.warning(
                    f"Unsafe story generated for child {child_profile.id}: {story[:100]}... Returning fallback.",
                )
                return "I'm sorry, I can't tell that story right now. How about a different one?"
        return story

    async def generate_educational_content(
        self,
        child_profile: ChildProfile,
        topic: str,
    ) -> str:
        """Generates educational content for a child.

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
            child_profile.id,
            conversation_history,
            current_input,
        )
        # Validate generated content
        if self.safety_monitor:
            safety_result = await self.safety_monitor.check_content_safety(
                educational_text,
                child_age=child_profile.age,
            )
            if safety_result.risk_level in [
                SafetyLevel.UNSAFE,
                SafetyLevel.POTENTIALLY_UNSAFE,
            ]:
                self.logger.warning(
                    f"Unsafe educational content generated for child {child_profile.id}: {educational_text[:100]}... Returning fallback.",
                )
                return "I'm sorry, I can't provide information on that topic right now. Is there something else you'd like to learn?"
        return educational_text

    async def get_interactive_activity(
        self,
        child_profile: ChildProfile,
        activity_type: str,
    ) -> dict[str, Any]:
        """Generates an interactive activity for a child.

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
        current_input = prompt
        activity_data = await self.api_client.make_request(
            "interactive_activities",
            {"messages": [{"role": "user", "content": current_input}]},
        )
        activity_response = activity_data.get("response", {})
        # Validate generated content
        if self.safety_monitor and isinstance(activity_response, str):
            safety_result = await self.safety_monitor.check_content_safety(
                activity_response,
                child_age=child_profile.age,
            )
            if safety_result.risk_level in [
                SafetyLevel.UNSAFE,
                SafetyLevel.POTENTIALLY_UNSAFE,
            ]:
                self.logger.warning(
                    f"Unsafe activity generated for child {child_profile.id}: {activity_response[:100]}... Returning empty activity.",
                )
                return {"error": "Content blocked due to safety concerns."}
        return activity_response
