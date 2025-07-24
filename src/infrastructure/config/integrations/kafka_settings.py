from pydantic import Field

from src.infrastructure.config.core.base_settings import BaseApplicationSettings


class KafkaSettings(BaseApplicationSettings):
    """Configuration settings for Kafka."""

    KAFKA_BOOTSTRAP_SERVERS: str = Field("kafka:9092", env="KAFKA_BOOTSTRAP_SERVERS")
    SCHEMA_REGISTRY_URL: str = Field(
        "http://schema-registry:8081", env="SCHEMA_REGISTRY_URL"
    )
    KAFKA_ENABLED: bool = Field(False, env="KAFKA_ENABLED")
