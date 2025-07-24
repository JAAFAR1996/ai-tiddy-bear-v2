"""Provides services for processing child interactions with the AI system.

This service handles incoming messages from children, performs comprehensive
safety checks, sanitizes content, and logs interactions for COPPA compliance.
It ensures that all interactions are safe, appropriate, and within defined
parameters for message length and child age.
"""

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from src.application.interfaces.safety_monitor import (
    SafetyAnalysisResult,
    SafetyMonitor,
)
from src.common.exceptions import InvalidInputError, ResourceNotFoundError
from src.domain.interfaces.child_profile_repository import IChildProfileRepository
from src.domain.interfaces.sanitization_service import ISanitizationService
from src.infrastructure.config.services.interaction_config import InteractionConfig
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="interaction_service")


class InteractionService:
    """Service for handling child interactions."""

    def __init__(
        self,
        config: InteractionConfig,
        child_profile_repository: IChildProfileRepository,
        sanitization_service: ISanitizationService,
        safety_monitor: SafetyMonitor,
        logger: logging.Logger = logger,
    ) -> None:
        """Initializes the interaction service with configuration and dependencies.

        Args:
            config: Configuration for interaction service settings.
            child_profile_repository: Repository for child profile data.
            sanitization_service: Service for sanitizing text and detecting PII.
            safety_monitor: Service for comprehensive content safety analysis.
            logger: Logger instance for logging service operations.

        """
        self.config = config
        self.child_profile_repository = child_profile_repository
        self.sanitization_service = sanitization_service
        self.safety_monitor = safety_monitor
        self.logger = logger

    async def process(self, child_id: str, message: str) -> dict[str, Any]:
        """Processes a child's interaction with comprehensive safety checks.

        Args:
            child_id: Unique identifier for the child.
            message: Message from the child.

        Returns:
            A dictionary containing processed interaction data.

        Raises:
            ValueError: If input validation fails.

        """
        # Input validation
        if not child_id or not isinstance(child_id, str):
            self.logger.warning("Invalid child_id provided in process method.")
            raise InvalidInputError("Valid child_id is required")
        if not message or not isinstance(message, str):
            self.logger.warning(f"Invalid message provided for child {child_id}.")
            raise InvalidInputError("Valid message is required")
        if len(message) > self.config.max_message_length:
            self.logger.warning(
                f"Message from child {child_id} too long (length: {len(message)}).",
            )
            raise InvalidInputError(
                f"Message too long. Maximum {self.config.max_message_length} characters",
            )

        # Age verification before any processing
        try:
            if not await self._check_child_age(UUID(child_id)):
                self.logger.warning(
                    f"Interaction blocked for child {child_id} due to age restriction.",
                )
                return {
                    "success": False,
                    "error": "Interaction not allowed due to age restrictions.",
                    "safe": False,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
        except (ResourceNotFoundError, InvalidInputError) as e:
            self.logger.error(f"Age verification failed for child {child_id}: {e}")
            return {
                "success": False,
                "error": f"Age verification failed: {e!s}",
                "safe": False,
                "timestamp": datetime.now(UTC).isoformat(),
            }

        # Clean and sanitize message
        cleaned_message = await self._sanitize_message(message)

        # Check for PII before further processing
        if await self.sanitization_service.detect_pii(cleaned_message):
            self.logger.warning(
                f"PII detected in message for child {child_id}. "
                "Blocking interaction.",
            )
            return {
                "success": False,
                "error": "Message contains personal information",
                "safe": False,
                "timestamp": datetime.now(UTC).isoformat(),
            }

        # Safety content filtering
        safety_result = await self._check_content_safety(cleaned_message)
        if not safety_result.is_safe:
            self.logger.warning(
                f"Unsafe content detected for child {child_id}: "
                f"{safety_result.overall_risk_level.value}",
            )
            return {
                "success": False,
                "error": (
                    "Message contains inappropriate content: "
                    f"{safety_result.overall_risk_level.value}"
                ),
                "safe": False,
                "timestamp": datetime.now(UTC).isoformat(),
            }

        # Log successful interaction for COPPA compliance
        self.logger.info(
            f"Safe interaction processed for child {child_id}. "
            f"Message: {cleaned_message}",
        )

        return {
            "success": True,
            "child_id": child_id,
            "processed_message": cleaned_message,
            "safe": True,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def _sanitize_message(self, message: str) -> str:
        """Sanitizes the message by removing potentially harmful characters or patterns
        using the injected sanitization service.

        Args:
            message: The original message.

        Returns:
            The sanitized message.

        """
        self.logger.debug(f"Sanitizing message: {message[:50]}...")
        sanitized_message = await self.sanitization_service.sanitize_text(message)
        self.logger.info("Message sanitization complete.")
        return sanitized_message

    async def _check_content_safety(self, message: str) -> SafetyAnalysisResult:
        """Checks the content of the message for safety and appropriateness using the injected safety monitor.

        Args:
            message: The message to check.

        Returns:
            A SafetyAnalysisResult object.

        """
        self.logger.debug(f"Checking content safety for message: {message[:50]}...")
        safety_result = await self.safety_monitor.analyze_content(message)
        self.logger.info(
            "Content safety check complete. Is safe: "
            f"{safety_result.is_safe}, Risk level: "
            f"{safety_result.overall_risk_level.value}",
        )
        return safety_result

    async def _check_child_age(self, child_id: UUID) -> bool:
        """Asynchronously checks if the child's age is within the allowed range.

        Args:
            child_id: The ID of the child.

        Returns:
            True if the age is valid, False otherwise.

        Raises:
            ResourceNotFoundError: If the child profile is not found.
            InvalidInputError: If child age is missing or invalid.

        """
        self.logger.debug(f"Checking age for child: {child_id}")
        child_age = await self.child_profile_repository.get_child_age(child_id)

        if child_age is None:
            self.logger.warning(
                f"Child age not found for child {child_id}. "
                "Cannot perform age check.",
            )
            raise ResourceNotFoundError(
                f"Child profile or age not found for child_id: {child_id}",
            )

        if not isinstance(child_age, int) or child_age < 0:
            self.logger.error(
                f"Invalid child age retrieved for child {child_id}: {child_age}",
            )
            raise InvalidInputError(f"Invalid age format for child {child_id}")

        is_age_valid = (
            self.config.min_child_age <= child_age <= self.config.max_child_age
        )
        if not is_age_valid:
            self.logger.warning(
                f"Child {child_id} (age {child_age}) is outside allowed age "
                f"range ({self.config.min_child_age}-{self.config.max_child_age}).",
            )
        else:
            self.logger.info(
                f"Child {child_id} (age {child_age}) is within allowed age range.",
            )
        return is_age_valid
