"""
Provides centralized configuration management for COPPA compliance features.

This module defines the `COPPAConfig` class, which acts as a single source
of truth for determining whether COPPA compliance is enabled. It allows
conditional execution of COPPA-specific logic throughout the application,
loading its state from application settings or environment variables.
"""

import logging
import os
from functools import lru_cache
from typing import Optional

from fastapi import Depends

from src.infrastructure.config.settings import Settings, get_settings


class COPPAConfig:
    """Centralized COPPA configuration manager."""

    def __init__(self, settings: Settings = Depends(get_settings)) -> None:
        """Initializes the COPPA configuration.

        Args:
            settings: The application settings instance.
        """
        self._enabled: Optional[bool] = None
        self._initialized = False
        self.settings = settings

    @property
    def enabled(self) -> bool:
        """
        Checks if COPPA compliance is enabled.

        Returns:
            True if COPPA compliance workflows should be executed, False otherwise.
        """
        if not self._initialized:
            self._initialize()
        return self._enabled

    @lru_cache(maxsize=1)  # Cache the initialization result
    def _initialize(self) -> None:
        """
        Initializes COPPA configuration from environment and settings.
        """
        try:
            self._enabled = self.settings.privacy.COPPA_ENABLED
            logging.info(
                f"COPPA compliance initialized from settings: {self._enabled}")
        except AttributeError:
            # Fallback to environment variable if settings not properly loaded
            env_value = os.getenv("COPPA_ENABLED", "").lower()
            if env_value in ("true", "1", "yes", "on"):
                self._enabled = True
            elif env_value in ("false", "0", "no", "off"):
                self._enabled = False
            else:
                # Default based on environment
                environment = os.getenv("ENVIRONMENT", "development").lower()
                self._enabled = environment == "production"
            logging.info(
                f"COPPA compliance initialized from environment: {self._enabled}"
            )
        self._initialized = True


def get_coppa_config() -> COPPAConfig:
    """
    Dependency injection function to get the COPPAConfig instance.

    Returns:
        The COPPAConfig instance.
    """
    return COPPAConfig()
