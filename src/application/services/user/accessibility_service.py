"""Manages accessibility features for children with special needs.

This service handles the creation and management of accessibility profiles,
ensuring that the AI Teddy Bear adapts its interaction to the specific needs
of each child. It supports various special needs, including visual and
hearing impairments, motor difficulties, and learning disabilities.
"""

import logging
from typing import Any
from uuid import UUID

from src.domain.interfaces.accessibility_profile_repository import (
    IAccessibilityProfileRepository,
)
from src.domain.value_objects.accessibility import (
    AccessibilityProfile,
    SpecialNeedType,
)
from src.infrastructure.config.services.accessibility_config import AccessibilityConfig
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="accessibility_service")


class AccessibilityService:
    """Service for handling special accessibility needs."""

    def __init__(
        self,
        repository: IAccessibilityProfileRepository,
        accessibility_config: AccessibilityConfig,
        logger: logging.Logger = logger,
    ) -> None:
        """Initializes the accessibility service with a repository for persistence and configuration.

        Args:
            repository: The repository for storing and retrieving accessibility profiles.
            accessibility_config: Configuration for accessibility rules and settings.
            logger: Logger instance for logging service operations.

        """
        self.repository = repository
        self.config = accessibility_config
        self.logger = logger

    async def create_accessibility_profile(
        self,
        child_id: UUID,
        needs: list[SpecialNeedType],
    ) -> AccessibilityProfile:
        """Creates an accessibility profile for a child and persists it.

        Args:
            child_id: The ID of the child.
            needs: A list of special needs for the child.

        Returns:
            The created AccessibilityProfile.

        """
        self.logger.info(f"Creating accessibility profile for child: {child_id}")
        profile = AccessibilityProfile(
            child_id=child_id,
            special_needs=needs,
            preferred_interaction_mode="voice",  # Default, can be refined later
            voice_speed_adjustment=1.0,
            volume_level=0.8,
            subtitles_enabled=False,
            additional_settings={},
        )
        await self.repository.save_profile(profile)
        self.logger.info(
            f"Accessibility profile created and saved for child: {child_id}",
        )
        return profile

    async def get_accessibility_profile(
        self,
        child_id: UUID,
    ) -> AccessibilityProfile | None:
        """Retrieves the accessibility profile for a child from the repository.

        Args:
            child_id: The ID of the child.

        Returns:
            The accessibility profile, or None if not found.

        """
        self.logger.debug(
            f"Attempting to retrieve accessibility profile for child: {child_id}",
        )
        profile = await self.repository.get_profile_by_child_id(child_id)
        if profile:
            self.logger.info(f"Accessibility profile found for child: {child_id}")
        else:
            self.logger.info(f"Accessibility profile not found for child: {child_id}")
        return profile

    def _get_adaptations(self, needs: list[SpecialNeedType]) -> list[str]:
        """Gets recommended adaptations based on special needs from the configuration.

        Args:
            needs: A list of special needs.

        Returns:
            A list of recommended adaptations.

        """
        if not needs:
            return []

        adaptations = []
        for need in needs:
            adaptations.extend(self.config.adaptation_rules.get(need.value, []))
        return list(set(adaptations))  # Remove duplicates

    def _get_accessibility_settings(
        self,
        needs: list[SpecialNeedType],
    ) -> dict[str, Any]:
        """Gets accessibility settings based on special needs from the configuration.

        Args:
            needs: A list of special needs.

        Returns:
            A dictionary of accessibility settings.

        """
        settings = {
            "audio_enabled": True,
            "visual_enabled": True,
            "simplified_ui": False,
            # Default settings
        }
        for need in needs:
            # Apply overrides from configuration
            overrides = self.config.accessibility_settings_rules.get(need.value, {})
            settings.update(overrides)

        # Ensure core settings are dynamically calculated if not overridden
        if SpecialNeedType.HEARING_IMPAIRMENT in needs:
            settings["audio_enabled"] = False
        if SpecialNeedType.VISUAL_IMPAIRMENT in needs:
            settings["visual_enabled"] = False
        if any(
            need
            in [
                SpecialNeedType.MOTOR_IMPAIRMENT,
                SpecialNeedType.COGNITIVE_DELAY,
            ]
            for need in needs
        ):
            settings["simplified_ui"] = True

        return settings
