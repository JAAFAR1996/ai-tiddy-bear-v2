"""Provides content filtering services to ensure child-safe interactions.

This service filters inappropriate words and content based on predefined lists
and age-group specific rules. It is crucial for maintaining COPPA compliance
and providing a safe environment for children using the AI Teddy Bear.
"""

import logging

from src.application.interfaces.safety_monitor import SafetyMonitor
from src.domain.value_objects.safety_level import SafetyLevel
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="content_filter_service")


class ContentFilterService:
    """Service for filtering inappropriate content."""

    def __init__(
        self,
        safety_monitor: SafetyMonitor,
        logger: logging.Logger = logger,
    ) -> None:
        """Initializes the content filter service.

        Args:
            safety_monitor: The SafetyMonitor implementation for comprehensive
                content safety checks.
            logger: Logger instance for logging service operations.

        """
        self.safety_monitor = safety_monitor
        self.logger = logger

    async def filter_content(self, text: str, age: int = 0) -> str:
        """Filters inappropriate content from the given text using a comprehensive
        safety monitor.

        Args:
            text: The input text to filter.
            age: The age of the user for age-specific filtering (default to 0 if
                not provided).

        Returns:
            The filtered text, or "[CONTENT BLOCKED]" if deemed unsafe.

        """
        self.logger.info("Filtering content for age-appropriate content")
        safety_result = await self.safety_monitor.check_content_safety(
            text,
            child_age=age,
        )

        if safety_result.risk_level == SafetyLevel.UNSAFE:
            self.logger.warning(
                f"Content deemed UNSAFE for age {age}. Original: "
                f"'{text[:50]}...' Reason: {safety_result.analysis_details}",
            )
            return "[CONTENT BLOCKED]"
        if safety_result.risk_level == SafetyLevel.POTENTIALLY_UNSAFE:
            self.logger.warning(
                f"Content deemed POTENTIALLY UNSAFE for age {age}. Original: "
                f"'{text[:50]}...' Reason: {safety_result.analysis_details}",
            )
            return "[CONTENT FLAGGED FOR REVIEW]"

        self.logger.info("Content deemed SAFE for user's age group")
        return text
