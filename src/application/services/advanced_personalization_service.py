"""
Manages advanced personalization features for a tailored user experience.

This service analyzes child interactions to create detailed personality profiles.
These profiles are then used to generate personalized content, such as stories
and activities, that match the child's interests, learning style, and
interaction preferences.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List
from uuid import UUID
from datetime import datetime

from src.domain.value_objects.personality import ChildPersonality, PersonalityType
from src.domain.interfaces.personality_profile_repository import (
    IPersonalityProfileRepository,
)
from src.infrastructure.logging_config import get_logger
from src.application.interfaces.ai_provider import AIProvider

logger = get_logger(__name__, component="advanced_personalization_service")


class AdvancedPersonalizationService:
    """Service for advanced personalization and content recommendation."""

    def __init__(
        self,
        repository: IPersonalityProfileRepository,
        ai_provider: AIProvider,
        logger: logging.Logger = logger,
    ) -> None:
        """
        Initializes the advanced personalization service with a repository for persistence and an AI provider.

        Args:
            repository: The repository for storing and retrieving personality profiles.
            ai_provider: The AI provider for personality analysis.
            logger: Logger instance for logging service operations.
        """
        self.repository = repository
        self.ai_provider = ai_provider
        self.logger = logger
        # self.personality_profiles: Dict[str, ChildPersonality] = {}

    async def create_personality_profile(
        self, child_id: UUID, interactions: List[Dict[str, Any]]
    ) -> ChildPersonality:
        """
        Analyzes child interactions to create a personality profile and persists it.

        Args:
            child_id: The ID of the child.
            interactions: A list of interactions to analyze.

        Returns:
            The created child personality profile.
        """
        self.logger.info(f"Creating personality profile for child: {child_id}")
        personality = await self._analyze_interactions(child_id, interactions)
        await self.repository.save_profile(personality)
        self.logger.info(
            f"Personality profile created and saved for child: {child_id}")
        return personality

    async def get_personality_profile(
            self, child_id: UUID) -> ChildPersonality | None:
        """
        Retrieves the personality profile for a child from the repository.

        Args:
            child_id: The ID of the child.

        Returns:
            The child's personality profile, or None if not found.
        """
        self.logger.debug(
            f"Attempting to retrieve personality profile for child: {child_id}"
        )
        profile = await self.repository.get_profile_by_child_id(child_id)
        if profile:
            self.logger.info(
                f"Personality profile found for child: {child_id}")
        else:
            self.logger.info(
                f"Personality profile not found for child: {child_id}")
        return profile

    async def get_personalized_content(
            self, child_id: UUID) -> Dict[str, Any] | None:
        """
        Gets personalized content recommendations for a child from their profile.

        Args:
            child_id: The ID of the child.

        Returns:
            A dictionary of personalized content, or None if no profile exists.
        """
        profile = await self.get_personality_profile(child_id)
        if not profile:
            self.logger.info(
                f"No personality profile found for child {child_id}. Cannot provide personalized content."
            )
            return None

        self.logger.debug(
            f"Generating personalized content for child {child_id} (Personality: {profile.personality_type.value})."
        )
        try:
            # Convert profile to a dictionary for the AI provider
            profile_dict = profile.__dict__
            # Assuming AIProvider's method can take child_id, personality
            # profile, and additional context
            personalized_content = await self.ai_provider.generate_personalized_content(
                child_id,
                profile_dict,
                {"current_time": str(datetime.now())},  # Example context
            )
            self.logger.info(
                f"AI generated personalized content for child {child_id}.")
            return personalized_content
        except Exception as e:
            self.logger.error(
                f"Error generating personalized content with AI service for child {child_id}: {e}",
                exc_info=True,
            )
            # Fallback to a generic content recommendation if AI service fails
            self.logger.warning(
                "Falling back to generic content recommendations.")
            return {
                "stories": ["A generic story for everyone"],
                "activities": ["A generic fun activity"],
                "difficulty_level": "easy",
            }

    async def _analyze_interactions(
        self, child_id: UUID, interactions: List[Dict[str, Any]]
    ) -> ChildPersonality:
        """
        Analyzes interactions to determine personality traits using the AI provider.

        Args:
            interactions: A list of interactions (e.g., {"text": "...", "sentiment": "..."}).

        Returns:
            A child personality profile based on AI analysis.
        """
        self.logger.info(
            "Analyzing child interactions for personality traits using AI provider."
        )
        try:
            # Assuming AIProvider.analyze_personality returns a dictionary
            # suitable for ChildPersonality
            personality_data = await self.ai_provider.analyze_personality(interactions)

            # Map the AI response to ChildPersonality.
            # This mapping logic might need to be more sophisticated in a real
            # system.
            personality_type_str = personality_data.get(
                "personality_type", "OTHER"
            ).upper()
            personality_type = (
                PersonalityType[personality_type_str]
                if personality_type_str in PersonalityType.__members__
                else PersonalityType.OTHER
            )

            return ChildPersonality(
                child_id=child_id,
                personality_type=personality_type,
                traits=personality_data.get("traits", {}),
                learning_style=personality_data.get("learning_style", []),
                last_updated=datetime.now(),
                metadata=personality_data.get("metadata", {}),
            )
        except Exception as e:
            self.logger.error(
                f"Error during personality analysis: {e}",
                exc_info=True)
            # Fallback to a default or generic personality if AI analysis fails
            return ChildPersonality(
                child_id=child_id,
                personality_type=PersonalityType.OTHER,
                interests=["general"],
                learning_style="mixed",
                interaction_preferences={},
                last_updated=datetime.now(),
                metadata={
                    "error": str(e),
                    "fallback_reason": "AI personality analysis failed",
                },
            )
