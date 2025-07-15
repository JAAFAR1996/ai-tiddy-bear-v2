"""
Defines infrastructure-related configuration settings for the application.

This module provides structured access to various infrastructure components
and their configurations, including database, cache (Redis), message queues
(RabbitMQ, Kafka), storage (S3, Azure, GCS), and monitoring tools (Prometheus,
Grafana, Sentry, New Relic, Datadog). It ensures consistent and validated
settings for deploying and operating the application.
"""

from typing import Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class InfrastructureSettings(BaseSettings):
    """Infrastructure configuration settings."""

    # ================================
    # Database Configuration (PostgreSQL Only)
    # ================================
    database_url: str = Field(..., regex="^postgresql")
    db_pool_size: int = Field(20, ge=5, le=100)
    db_max_overflow: int = Field(0, ge=0, le=50)
    db_pool_recycle: int = Field(300, ge=60, le=3600)
    db_echo: bool = False
    db_ssl_mode: str = "require"

    # ================================
    # Cache Configuration (Redis)
    # ================================
    redis_url: str = Field(..., regex="^redis://")
    redis_password: Optional[str] = None
    redis_max_connections: int = Field(50, ge=10, le=200)
    cache_ttl: int = Field(3600, ge=60, le=86400)  # 1 hour to 1 day

    # ================================
    # Message Queue Configuration
    # ================================
    rabbitmq_url: Optional[str] = None
    kafka_bootstrap_servers: Optional[str] = None
    message_queue_type: str = Field("redis", regex="^(redis|rabbitmq|kafka)$")

    # ================================
    # Storage Configuration
    # ================================
    storage_type: str = Field("s3", regex="^(local|s3|azure|gcs)$")
    storage_bucket: Optional[str] = None
    storage_region: Optional[str] = None
    max_upload_size_mb: int = Field(10, ge=1, le=100)

    # ================================
    # Monitoring Configuration
    # ================================
    prometheus_enabled: bool = True
    grafana_enabled: bool = True
    sentry_dsn: Optional[str] = None
    newrelic_license_key: Optional[str] = None
    datadog_api_key: Optional[str] = None

    # Logging
    log_to_file: bool = True
    log_file_path: str = "/var/log/ai-teddy/app.log"
    log_rotation: str = "daily"
    log_retention_days: int = 7

    # ================================
    # Security Configuration
    # ================================
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_minutes: int = 10080  # 7 days

    # ================================
    # Feature Flags
    # ================================
    feature_x_enabled: bool = False
    feature_y_enabled: bool = True

    # ================================
    # External Services
    # ================================
    external_api_timeout_seconds: int = 10

    @validator("database_url", pre=True, always=True)
    def validate_database_url(cls, v: str) -> str:
        """
        Validates that the database URL starts with 'postgresql'.

        Args:
            v: The database URL.

        Returns:
            The validated database URL.

        Raises:
            ValueError: If the URL does not start with 'postgresql'.
        """
        if not v.startswith("postgresql"):
            raise ValueError("Database URL must start with 'postgresql'")
        return v
