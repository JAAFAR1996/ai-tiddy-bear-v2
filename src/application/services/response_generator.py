"""Provides response generation services for child interactions.

This service handles AI-driven response generation, context management, safety
filtering, and ensures that all AI-generated content adheres to COPPA and child
safety requirements.
"""

import logging
from typing import Any

from src.application.interfaces.safety_monitor import SafetyMonitor, SafetyLevel
from src.domain.entities.session import Session, ActivityType
from src.domain.exceptions import ServiceUnavailableError
from src.infrastructure.logging_config import get_logger
from src.presentation.api.models import ResponseContext

logger = get_logger(__name__, component="response_generator")


class ResponseGenerator:
    """Service for generating AI responses in child interactions."""

    def __init__(
        self,
        ai_client: Any,
        safety_monitor: SafetyMonitor,
        logger: logging.Logger = logger,
    ) -> None:
        """Initializes the response generator with AI client and safety monitor.

        Args:
            ai_client: The AI client used for response generation.
            safety_monitor: Service for comprehensive content safety analysis.
            logger: Logger instance for logging service operations.

        """
        self.ai_client = ai_client
        self.safety_monitor = safety_monitor
        self.logger = logger

    async def generate_response(
        self, session: Session, user_input: str
    ) -> ResponseContext:
        """Generates a response to the user's input, ensuring safety and compliance.

        Args:
            session: The active Session object.
            user_input: The user's message or input.

        Returns:
            A ResponseContext object containing the AI's reply and context.

        Raises:
            ServiceUnavailableError: If the AI client or safety monitor fails.

        """
        # Basic input validation
        if not user_input or not isinstance(user_input, str):
            self.logger.warning(
                f"Invalid user input received for session {session.session_id}"
            )
            return ResponseContext(
                "I'm sorry, I didn't understand that. Can you try asking another way?",
                ActivityType.CONVERSATION,
                "neutral",
            )

        # Generate AI response
        try:
            ai_response_text = await self.ai_client.generate(
                session, user_input
            )
        except Exception as e:
            self.logger.error(
                f"AI client failed to generate response for session {session.session_id}: {e}",
                exc_info=True,
            )
            raise ServiceUnavailableError(
                "AI service temporarily unavailable."
            )

        # Safety check on generated response
        try:
            safety_result = await self.safety_monitor.check_content_safety(
                ai_response_text, child_age=session.child_age
            )
        except Exception as e:
            self.logger.error(
                f"Safety monitor failed for session {session.session_id}: {e}",
                exc_info=True,
            )
            raise ServiceUnavailableError(
                "Content safety service temporarily unavailable."
            )

        if safety_result.risk_level in [
            SafetyLevel.UNSAFE,
            SafetyLevel.POTENTIALLY_UNSAFE,
        ]:
            self.logger.warning(
                "AI response blocked: Unsafe content detected for child %s. "
                "Response: '%s...' Reason: %s",
                session.child_id,
                ai_response_text[:50],
                safety_result.analysis_details,
            )
            return ResponseContext(
                "I'm sorry, that's not something I can talk about. Can we find another topic?",
                ActivityType.CONVERSATION,
                "neutral",
            )

        # Log safe AI response for audit
        self.logger.info(
            f"Safe AI response generated for session {session.session_id}: "
            f"{ai_response_text[:100]}"
        )

        return ResponseContext(
            ai_response_text,
            ActivityType.CONVERSATION,
            safety_result.inferred_emotion or "neutral",
        )
