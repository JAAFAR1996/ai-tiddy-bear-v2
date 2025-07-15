"""
Generates contextual responses and determines appropriate activity types.

This service is responsible for analyzing input text, emotion, and session
context to produce relevant AI responses and suggest suitable activities.
It aims to make interactions more dynamic and engaging by adapting to the
current conversational flow and emotional state.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional
from src.application.interfaces.ai_provider import AIProvider
from src.application.services.session_manager import SessionData
from src.infrastructure.logging_config import get_logger
from src.application.interfaces.safety_monitor import SafetyMonitor
from src.domain.safety.models import SafetyLevel

logger = get_logger(__name__, component="response_generator")


class ActivityType(Enum):
    """Enumeration for different types of activities or response contexts."""

    STORY = "story"
    GAME = "game"
    LEARNING = "learning"
    SLEEP_ROUTINE = "sleep_routine"
    CONVERSATION = "conversation"
    COMFORT = "comfort"


@dataclass(slots=True)
class ResponseContext:
    """Represents the context of a generated AI response."""

    text: str
    activity_type: ActivityType
    emotion: str


class ResponseGenerator:
    """Service for generating contextual responses and determining activity types."""

    def __init__(self, ai_service: AIProvider | None = None, safety_monitor: SafetyMonitor = None) -> None:
        """
        Initializes the response generator.

        Args:
            ai_service: An optional AI service dependency.
            safety_monitor: Optional SafetyMonitor for content validation.
        """
        self.ai_service = ai_service
        self.logger = logger
        self.safety_monitor = safety_monitor

    async def determine_activity_type(
        self, text: str, emotion: dict[str, Any], session: SessionData
    ) -> ActivityType:
        """
        Determines the appropriate activity type based on input text, emotion, and session
        using the AI service, with fallback.

        Args:
            text: The input text.
            emotion: The detected emotion (e.g., {'sentiment': 'joy', 'score': 0.8}).
            session: The current session context.

        Returns:
            The determined ActivityType.
        """
        if self.ai_service:
            try:
                session_context_dict = session.__dict__ # Convert dataclass to dict for generic AI API
                predicted_activity_str = await self.ai_service.determine_activity_type(
                    text, emotion, session_context_dict
                )
                return ActivityType[predicted_activity_str.upper()]
            except Exception as e:
                # Log the error and fall back
                self.logger.error(f"Error determining activity type with AI service: {e}", exc_info=True)
        # Fallback logic if AI service is not available or fails
        return ActivityType.CONVERSATION

    async def generate_contextual_response(
        self, text: str, emotion: dict[str, Any], session: SessionData
    ) -> ResponseContext:
        """
        Generates a contextual response based on input text, emotion, and session
        using the AI service, with fallback.

        Args:
            text: The input text.
            emotion: The detected emotion (e.g., {'sentiment': 'joy', 'score': 0.8}).
            session: The current session context.

        Returns:
            A ResponseContext object containing the generated response.
        """
        if self.ai_service:
            try:
                # Assuming conversation_history is extracted or managed by a higher-level service
                # For this specific method, we might just pass the current input and relevant context
                conversation_history_dummy = [] # Replace with actual conversation history if available from session
                child_preferences_dummy = session.data.get("child_preferences", None) # Assuming preferences are stored in session data

                ai_response_text = await self.ai_service.generate_response(
                    child_id=session.child_id,
                    conversation_history=conversation_history_dummy,
                    current_input=text,
                    child_preferences=child_preferences_dummy
                )
                self.logger.info(f"AI generated contextual response: {ai_response_text[:50]}...")
                
                # Validate AI-generated response for safety
                if self.safety_monitor:
                    child_age_for_safety = session.data.get("child_age", 0)
                    safety_result = await self.safety_monitor.check_content_safety(ai_response_text, child_age=child_age_for_safety)
                    if safety_result.risk_level in [SafetyLevel.UNSAFE, SafetyLevel.POTENTIALLY_UNSAFE]:
                        self.logger.warning(f"AI response blocked: Unsafe content detected for child {session.child_id}. Response: '{ai_response_text[:50]}...' Reason: {safety_result.analysis_details}")
                        return ResponseContext(
                            "I'm sorry, that's not something I can talk about. Can we find another topic?",
                            ActivityType.CONVERSATION,
                            "neutral",
                        )
                # The activity_type and emotion from AIProvider.generate_response might need parsing
                # For now, assume a simple mapping or default from context/emotion input
                activity_type = await self.determine_activity_type(text, emotion, session)
                response_emotion = emotion.get("sentiment", "neutral") # Assuming sentiment key exists

                return ResponseContext(ai_response_text, activity_type, response_emotion)
            except Exception as e:
                self.logger.error(f"Error generating contextual response with AI service: {e}", exc_info=True)
        # Fallback logic if AI service is not available or fails
        self.logger.warning("Falling back to generic response due to AI service failure or unavailability.")
        return ResponseContext("I'm sorry, I couldn't generate a personalized response right now. Can we talk about something else?", ActivityType.CONVERSATION, "neutral")
