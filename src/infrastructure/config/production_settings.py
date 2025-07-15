"""
Defines comprehensive production configuration settings for the AI Teddy Bear application.

This module extends various base settings classes to provide a complete set
of configurations for a production environment, including AI, security,
infrastructure, and application-specific settings. It incorporates Pydantic
for robust validation and ensures that all necessary parameters for a secure
and performant deployment are properly defined.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import Field, root_validator, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.infrastructure.logging_config import get_logger

from .ai_settings import AISettings
from .base_settings import BaseApplicationSettings
from .infrastructure_settings import InfrastructureSettings
from .security_settings import SecuritySettings

logger = get_logger(__name__, component="config")


class ProductionSettings(
    BaseApplicationSettings,
    SecuritySettings,
    InfrastructureSettings,
    AISettings,
    BaseSettings,
):
    """Advanced production settings for AI Teddy Bear application."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ================================
    # Feature Flags
    # ================================
    enable_voice_transcription: bool = True
    enable_emotion_detection: bool = True
    enable_multi_language: bool = False
    enable_ar_features: bool = False
    enable_federated_learning: bool = False

    # ================================
    # Performance Configuration
    # ================================
    enable_response_caching: bool = True
    cache_response_ttl: int = Field(300, ge=60, le=3600)
    enable_query_optimization: bool = True
    connection_pool_timeout: int = Field(30, ge=5, le=120)

    # ================================
    # CORS Configuration
    # ================================
    cors_origins: List[str] = Field(
        default_factory=lambda: ["https://app.aiteddybear.com"]
    )
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = Field(
        default_factory=lambda: ["*"]
    )
    cors_allow_headers: List[str] = Field(
        default_factory=lambda: ["*"]
    )

    # ================================
    # Security Configuration (Overrides from SecuritySettings if needed)
    # ================================
    # Example: Force a stronger algorithm in production
    jwt_algorithm: str = Field("HS512", env="JWT_ALGORITHM")

    # ================================
    # Logging Configuration (Overrides from BaseApplicationSettings if needed)
    # ================================
    log_level: str = Field("INFO", env="LOG_LEVEL")

    # ================================
    # Paths
    # ================================
    data_dir: Path = Field(Path("data"), env="DATA_DIR")
    log_dir: Path = Field(Path("logs"), env="LOG_DIR")

    @validator("data_dir", "log_dir", pre=True)
    def create_dirs_if_not_exists(cls, v: str) -> Path:
        """
        Ensures that the specified directory exists, creating it if necessary.

        Args:
            v: The path string for the directory.

        Returns:
            A Path object representing the directory.
        """
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @root_validator(pre=True)
    def check_production_env_vars(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs a root validation to ensure critical environment variables
        are set for production.

        Args:
            values: The dictionary of settings values.

        Returns:
            The validated dictionary of settings values.

        Raises:
            ValueError: If critical production environment variables are missing.
        """
        if values.get("environment") == "production":
            required_prod_vars = [
                "DATABASE_URL",
                "JWT_SECRET_KEY",
                "OPENAI_API_KEY",
            ]
            missing_vars = [
                var for var in required_prod_vars if not os.getenv(var)
            ]
            if missing_vars:
                raise ValueError(
                    f"Missing critical production environment variables: {missing_vars}"
                )
        return values
