"""Orchestrates AI-related services to generate safe and personalized responses.

This service acts as a central hub for coordinating various AI components,
including the AI provider, safety monitor, conversation service, and text-to-speech
service. It ensures that all AI interactions are child-safe, context-aware,
and tailored to the child's preferences.
"""

from uuid import UUID

from src.application.dto.ai_response import AIResponse
from src.common.exceptions import ()
from src.application.interfaces.ai_provider import AIProvider
from src.application.interfaces.safety_monitor import (
    SafetyLevel,
    SafetyMonitor,
)
from src.application.interfaces.text_to_speech_service import TextToSpeechService
from src.application.services.core.conversation_service import ConversationService
from src.domain.value_objects.child_preferences import ChildPreferences
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="ai_orchestration")


class AIOrchestrationService:
    """Orchestrates AI services for child-safe AI interactions."""

    def __init__(
        self,
        ai_provider: AIProvider,
        safety_monitor: SafetyMonitor,
        conversation_service: ConversationService,
        tts_service: TextToSpeechService | None = None,
    ):
        """Initializes the AI Orchestration Service.

        Args:
            ai_provider: Service for generating AI responses.
            safety_monitor: Child safety monitoring and content filtering.
            conversation_service: Service for managing conversation history.
            tts_service: Optional text-to-speech conversion service.

        """
        self.ai_provider = ai_provider
        self.safety_monitor = safety_monitor
        self.conversation_service = conversation_service
        self.tts_service = tts_service

    async def get_ai_response(
        self,
        child_id: UUID,
        conversation_history: list[str],
        current_input: str,
        voice_id: str,
        child_preferences: ChildPreferences,
    ) -> AIResponse:
        """Generates a child-safe AI response with comprehensive safety monitoring.

        Args:
            child_id: Unique identifier for the child.
            conversation_history: Previous conversation context.
            current_input: Child's current input/question.
            voice_id: Voice preference for TTS response.
            child_preferences: Child's personalization settings.

        Returns:
            An AIResponse object containing the safe response and audio.

        """
        # 1. Input safety check
        input_safety = self.safety_monitor.check_text_safety(current_input)
        if input_safety != SafetyLevel.SAFE:
            return AIResponse.safe_fallback("I can't talk about that.")

        # 2. Generate AI response
        try:
            raw_response = await self.ai_provider.generate_response(
                conversation_history,
                current_input,
                child_preferences,
            )
        except (
            ServiceUnavailableError,
            TimeoutError,
            ApplicationException,
        ) as e:  # Assuming these specific exceptions from external_apis or a custom exception module
            logger.error(f"AI provider error: {e}", exc_info=True)
            return AIResponse.safe_fallback(
                "I'm sorry, I'm having trouble understanding right now. Can we talk about something else?",
            )
        except Exception as e:
            logger.critical(
                f"Unexpected error during AI response generation: {e}",
                exc_info=True,
            )
            return AIResponse.safe_fallback(
                "An unexpected error occurred. Please try again later.",
            )

        # 3. Output safety check
        output_safety = self.safety_monitor.check_text_safety(raw_response)
        if output_safety != SafetyLevel.SAFE:
            return AIResponse.safe_fallback("I have a better idea!")

        # 4. Generate audio if TTS service is available
        audio_content = None
        if self.tts_service:
            try:
                audio_content = await self.tts_service.generate_speech(
                    raw_response,
                    voice_id,
                )
            except (ServiceUnavailableError, InvalidInputError, ApplicationException) as e:
                logger.warning(f"TTS service error: {e}", exc_info=True)
                # Continue without audio if TTS fails, as it's not critical
            except Exception as e:
                logger.error(
                    f"Unexpected error during TTS generation: {e}",
                    exc_info=True,
                )
                # Continue without audio if TTS fails, as it's not critical

        # 5. Update conversation history
        self.conversation_service.add_interaction(child_id, current_input, raw_response)

        return AIResponse(
            text=raw_response,
            audio=audio_content,
            safety_level=output_safety,
        )
