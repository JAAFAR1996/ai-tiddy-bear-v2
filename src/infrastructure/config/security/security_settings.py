"""
src/infrastructure/config/security_settings.py
Secure SecuritySettings with comprehensive JWT cryptographic validation
"""

from pydantic import Field, SecretStr, field_validator, model_validator

from src.infrastructure.config.core.base_settings import BaseApplicationSettings


class SecuritySettings(BaseApplicationSettings):
    """Configuration settings for application security."""

    # Constants for key lengths - CRITICAL CHILD SAFETY REQUIREMENTS
    MIN_SECRET_KEY_LENGTH: int = 64  # Increased from 32 for enhanced security
    MIN_JWT_SECRET_KEY_LENGTH: int = (
        64  # CRITICAL: 64 chars minimum for child data protection
    )
    COPPA_ENCRYPTION_KEY_LENGTH: int = 44

    # Security keys - MUST be provided via environment variables
    SECRET_KEY: str = Field(
        env="SECRET_KEY",
        description="Main application secret key for security operations",
    )
    JWT_SECRET_KEY: str = Field(
        env="JWT_SECRET_KEY",
        description="Secret key for JWT token signing and verification",
    )
    COPPA_ENCRYPTION_KEY: str = Field(
        env="COPPA_ENCRYPTION_KEY",
        description="Encryption key for COPPA-compliant data protection",
    )

    # المتغيرات الإضافية مع قيم افتراضية
    JWT_SECRET: str | None = Field(default=None, env="JWT_SECRET")
    JWT_REFRESH_SECRET: str | None = Field(default=None, env="JWT_REFRESH_SECRET")
    SESSION_SECRET: str | None = Field(default=None, env="SESSION_SECRET")
    ENCRYPTION_KEY: str | None = Field(default=None, env="ENCRYPTION_KEY")
    DATA_ENCRYPTION_KEY: str | None = Field(default=None, env="DATA_ENCRYPTION_KEY")
    FIELD_ENCRYPTION_KEY: str | None = Field(default=None, env="FIELD_ENCRYPTION_KEY")

    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(
        60, env="RATE_LIMIT_REQUESTS_PER_MINUTE"
    )
    RATE_LIMIT_BURST: int = Field(10, env="RATE_LIMIT_BURST")
    RATE_LIMIT_REQUESTS_PER_HOUR: int = Field(3600, env="RATE_LIMIT_REQUESTS_PER_HOUR")

    MAX_LOGIN_ATTEMPTS: int = Field(5, env="MAX_LOGIN_ATTEMPTS")
    LOCKOUT_DURATION_SECONDS: int = Field(300, env="LOCKOUT_DURATION_SECONDS")

    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    JWT_EXPIRE_MINUTES: int = Field(30, env="JWT_EXPIRE_MINUTES")
    JWT_REFRESH_EXPIRE_DAYS: int = Field(30, env="JWT_REFRESH_EXPIRE_DAYS")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    SESSION_EXPIRE_HOURS: int = Field(24, env="SESSION_EXPIRE_HOURS")
    SESSION_SECURE: bool = Field(True, env="SESSION_SECURE")
    SESSION_HTTPONLY: bool = Field(True, env="SESSION_HTTPONLY")
    SESSION_SAMESITE: str = Field("strict", env="SESSION_SAMESITE")

    CONTENT_FILTER_STRICT_MODE: bool = Field(True, env="CONTENT_FILTER_STRICT_MODE")
    SAFETY_THRESHOLD: float = Field(0.8, env="SAFETY_THRESHOLD")

    # HashiCorp Vault Configuration (PRODUCTION REQUIRED)
    VAULT_URL: str | None = Field(
        None, env="VAULT_URL", description="HashiCorp Vault server URL"
    )
    VAULT_TOKEN: SecretStr | None = Field(
        None, env="VAULT_TOKEN", description="Vault authentication token"
    )
    VAULT_NAMESPACE: str | None = Field(
        None, env="VAULT_NAMESPACE", description="Vault Enterprise namespace"
    )
    VAULT_MOUNT_POINT: str = Field(
        "secret", env="VAULT_MOUNT_POINT", description="Vault secrets mount point"
    )
    VAULT_ENABLED: bool = Field(
        False, env="VAULT_ENABLED", description="Enable Vault integration"
    )

    # Production mode requires Vault
    @field_validator("VAULT_URL", mode="after")
    @classmethod
    def validate_vault_url_production(cls, v: str | None, info) -> str | None:
        """Validate Vault URL in production."""
        environment = info.data.get("ENVIRONMENT", "development")
        if environment == "production" and not v:
            raise ValueError("VAULT_URL is required in production environment")
        return v

    @field_validator("VAULT_TOKEN", mode="after")
    @classmethod
    def validate_vault_token_production(
        cls, v: SecretStr | None, info
    ) -> SecretStr | None:
        """Validate Vault token in production."""
        environment = info.data.get("ENVIRONMENT", "development")
        if environment == "production" and not v:
            raise ValueError("VAULT_TOKEN is required in production environment")
        return v

    RATE_LIMITS: dict[str, dict[str, int]] = Field(
        default_factory=lambda: {
            "/auth/login": {"requests": 5, "window": 60},
            "/auth/register": {"requests": 3, "window": 60},
            "/auth/refresh": {"requests": 10, "window": 60},
            "/auth/password-reset": {"requests": 3, "window": 3600},
            "/esp32": {"requests": 30, "window": 60},
            "/ai/generate": {"requests": 20, "window": 60},
            "/audio": {"requests": 15, "window": 60},
            "/api/v1/conversation": {"requests": 30, "window": 300},
            "/api/v1/voice": {"requests": 10, "window": 300},
            "/dashboard": {"requests": 100, "window": 60},
            "/children": {"requests": 50, "window": 60},
            "/reports": {"requests": 30, "window": 60},
            "/health": {"requests": 1000, "window": 60},
            "/metrics": {"requests": 1000, "window": 60},
            "/docs": {"requests": 60, "window": 60},
            "/redoc": {"requests": 60, "window": 60},
        },
    )

    @model_validator(mode="after")
    def validate_security_configuration(self) -> "SecuritySettings":
        """Validate security configuration with comprehensive JWT validation."""

        # Validate token expiration
        if self.ACCESS_TOKEN_EXPIRE_MINUTES >= (
            self.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60
        ):
            raise ValueError(
                "ACCESS_TOKEN_EXPIRE_MINUTES cannot exceed REFRESH_TOKEN_EXPIRE_DAYS"
            )

        # Enhanced SECRET_KEY validation (64 chars minimum)
        if len(self.SECRET_KEY) < self.MIN_SECRET_KEY_LENGTH:
            raise ValueError(
                f"SECRET_KEY must be at least {self.MIN_SECRET_KEY_LENGTH} characters long "
                f"(current: {len(self.SECRET_KEY)}). "
                f"Weak secrets compromise child data security."
            )

        # Enhanced JWT_SECRET_KEY validation (64 chars minimum)
        if len(self.JWT_SECRET_KEY) < self.MIN_JWT_SECRET_KEY_LENGTH:
            raise ValueError(
                f"JWT_SECRET_KEY must be at least {self.MIN_JWT_SECRET_KEY_LENGTH} characters long "
                f"(current: {len(self.JWT_SECRET_KEY)}). "
                f"Weak JWT secrets enable session hijacking and child data compromise."
            )

        # COPPA encryption key validation
        if len(self.COPPA_ENCRYPTION_KEY) != self.COPPA_ENCRYPTION_KEY_LENGTH:
            raise ValueError(
                f"COPPA_ENCRYPTION_KEY must be exactly {self.COPPA_ENCRYPTION_KEY_LENGTH} characters long "
                f"(current: {len(self.COPPA_ENCRYPTION_KEY)})"
            )

        # Enhanced validation: No development keys in production
        dev_indicators = [
            "DEVELOPMENT",
            "DEV",
            "TEST",
            "DEMO",
            "EXAMPLE",
            "SAMPLE",
            "CHANGE_IN_PRODUCTION",
            "CHANGEME",
            "CHANGE_ME",
            "PLACEHOLDER",
            "123456",
            "PASSWORD",
            "SECRET",
            "DEFAULT",
            "TEMP",
            "TEMPORARY",
            "ABCDEF",
            "QWERTY",
            "ASDFGH",
            "ZXCVBN",
        ]

        for key_name, key_value in [
            ("SECRET_KEY", self.SECRET_KEY),
            ("JWT_SECRET_KEY", self.JWT_SECRET_KEY),
            ("COPPA_ENCRYPTION_KEY", self.COPPA_ENCRYPTION_KEY),
        ]:
            key_upper = key_value.upper()
            for indicator in dev_indicators:
                if indicator in key_upper:
                    raise ValueError(
                        f"{key_name} contains development placeholder '{indicator}'. "
                        f"CRITICAL SECURITY ERROR: Use cryptographically secure secrets in production."
                    )

        return self
