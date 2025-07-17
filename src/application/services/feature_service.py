"""
Manages feature availability and parental controls for the AI Teddy Bear.

This service allows for the dynamic enabling and disabling of features based
on child age, parental consent, and safety considerations. It ensures that
features are only accessible when appropriate, adhering to COPPA compliance
and providing a customizable experience for each child.
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="feature_service")


class FeatureType(str, Enum):
    """Available feature types."""

    VOICE_GAMES = "voice_games"
    STORY_TELLING = "story_telling"
    EDUCATIONAL_CONTENT = "educational_content"
    AUDIO_RECORDING = "audio_recording"
    PERSONALIZATION = "personalization"
    AR_VR_FEATURES = "ar_vr_features"


class FeatureService:
    """Service for managing child-specific features with safety controls."""

    def __init__(self, logger: logging.Logger = logger) -> None:
        """Initializes the feature service with default features and age restrictions."""
        self.logger = logger
        # Default safe features for all children
        self.default_features = {
            FeatureType.STORY_TELLING: True,
            FeatureType.EDUCATIONAL_CONTENT: True,
            FeatureType.VOICE_GAMES: False,  # Requires parental approval
            FeatureType.AUDIO_RECORDING: False,  # COPPA sensitive
            FeatureType.PERSONALIZATION: False,  # Data collection
            FeatureType.AR_VR_FEATURES: False,  # Age restricted
        }
        # Age-appropriate feature matrix
        self.age_restrictions = {
            FeatureType.VOICE_GAMES: 5,  # Minimum age 5
            FeatureType.AUDIO_RECORDING: 8,  # Minimum age 8
            FeatureType.AR_VR_FEATURES: 10,  # Minimum age 10
        }

    async def enable_feature(
        self,
        feature_name: str,
        child_id: str,
        child_age: int = None,
        parent_consent: bool = False,
    ) -> Dict[str, Any]:
        """
        Enables a feature for a specific child with safety checks.

        Args:
            feature_name: Name of the feature to enable.
            child_id: Unique identifier for the child.
            child_age: Age of the child for restrictions.
            parent_consent: Whether parent has given explicit consent.

        Returns:
            A dictionary indicating the success status and any messages.
        """
        try:
            feature_type = FeatureType(feature_name)
        except ValueError:
            self.logger.warning(
                f"Invalid feature type provided for enable_feature: {feature_name}"
            )
            return {"success": False, "message": "Invalid feature type."}

        if feature_type not in self.default_features:
            return {"success": False,
                    "message": f"Unknown feature: {feature_name}"}

        # If feature is off by default
        if not self.default_features[feature_type]:
            if child_age is None:
                return {
                    "success": False,
                    "message": "Child age is required for this feature.",
                }

            if feature_type in self.age_restrictions:
                min_age = self.age_restrictions[feature_type]
                if child_age < min_age:
                    return {
                        "success": False,
                        "message": f"Child is too young for {feature_name}. Minimum age: {min_age}",
                    }

            if not parent_consent:
                return {
                    "success": False,
                    "message": f"Parental consent required for {feature_name}.",
                }

        # Feature can be enabled
        # In a real system, this would update a child's profile in a database
        self.logger.info(
            f"Feature '{feature_type.value}' enabled for child {child_id}")
        return {"success": True,
                "message": f"Feature '{feature_type.value}' enabled."}

    async def disable_feature(self, feature_name: str,
                              child_id: str) -> Dict[str, Any]:
        """
        Disables a feature for a specific child.

        Args:
            feature_name: Name of the feature to disable.
            child_id: Unique identifier for the child.

        Returns:
            A dictionary indicating the success status and any messages.
        """
        try:
            feature_type = FeatureType(feature_name)
        except ValueError:
            self.logger.warning(
                f"Invalid feature type provided for disable_feature: {feature_name}"
            )
            return {"success": False, "message": "Invalid feature type."}

        if not self.default_features.get(feature_type):
            return {
                "success": False,
                "message": f"Feature {feature_type.value} is already disabled or unknown.",
            }

        self.logger.info(
            f"Feature '{feature_type.value}' disabled for child {child_id}"
        )
        return {"success": True,
                "message": f"Feature '{feature_type.value}' disabled."}

    def get_feature_status(self, feature_name: str,
                           child_id: str) -> Dict[str, Any]:
        """
        Gets the current status of a feature for a specific child.

        Args:
            feature_name: Name of the feature.
            child_id: Unique identifier for the child.

        Returns:
            A dictionary indicating the feature's status.
        """
        try:
            feature_type = FeatureType(feature_name)
        except ValueError:
            self.logger.warning(
                f"Invalid feature type provided for get_feature_status: {feature_name}"
            )
            return {"success": False, "message": "Invalid feature type."}

        is_enabled = self.default_features.get(feature_type, False)
        self.logger.info(
            f"Feature '{feature_type.value}' status for child {child_id}: {is_enabled}"
        )
        return {"feature_name": feature_type.value, "is_enabled": is_enabled}
