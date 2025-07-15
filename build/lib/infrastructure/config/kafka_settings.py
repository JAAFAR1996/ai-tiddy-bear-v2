"""
Defines Kafka-related configuration settings for the application.

This module uses Pydantic to manage environment variables and provide
structured access to Kafka connection details, such as bootstrap servers
and schema registry URL. It ensures that Kafka settings are loaded
securely and consistently across the application.
"""

from pydantic import Field

from src.infrastructure.config.base_settings import BaseApplicationSettings


class KafkaSettings(BaseApplicationSettings):
    """Configuration settings for Kafka integration."""

    KAFKA_BOOTSTRAP_SERVERS: str = Field(..., env="KAFKA_BOOTSTRAP_SERVERS")
    SCHEMA_REGISTRY_URL: str = Field(..., env="SCHEMA_REGISTRY_URL")
