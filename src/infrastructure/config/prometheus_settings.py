from pydantic import Field
from src.infrastructure.config.base_settings import BaseApplicationSettings

class PrometheusSettings(BaseApplicationSettings):
    """Configuration settings for Prometheus monitoring."""

    PROMETHEUS_ENABLED: bool = Field(True, env="PROMETHEUS_ENABLED")
    PROMETHEUS_PORT: int = Field(9090, env="PROMETHEUS_PORT")