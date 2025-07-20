"""
src/infrastructure/config/security_settings.py
تحديث SecuritySettings لإضافة قيم افتراضية
"""
from pydantic import Field, SecretStr, model_validator
from src.infrastructure.config.core.base_settings import BaseApplicationSettings

class SecuritySettings(BaseApplicationSettings):
    """Configuration settings for application security."""

    # Constants for key lengths
    MIN_SECRET_KEY_LENGTH: int = 32
    MIN_JWT_SECRET_KEY_LENGTH: int = 32
    COPPA_ENCRYPTION_KEY_LENGTH: int = 44

    # المفاتيح الأساسية - مع قيم افتراضية للتطوير
    SECRET_KEY: str = Field(
        default="DEVELOPMENT_SECRET_KEY_CHANGE_IN_PRODUCTION_123456789",
        env="SECRET_KEY"
    )
    JWT_SECRET_KEY: str = Field(
        default="DEVELOPMENT_JWT_SECRET_KEY_CHANGE_IN_PRODUCTION_123456789", 
        env="JWT_SECRET_KEY"
    )
    COPPA_ENCRYPTION_KEY: str = Field(
        default="DEVELOPMENT_COPPA_KEY_CHANGE_IN_PRODUCTION_44CHARS_HERE!!",
        env="COPPA_ENCRYPTION_KEY"
    )

    # المتغيرات الإضافية مع قيم افتراضية
    JWT_SECRET: str | None = Field(default=None, env="JWT_SECRET")
    JWT_REFRESH_SECRET: str | None = Field(default=None, env="JWT_REFRESH_SECRET")
    SESSION_SECRET: str | None = Field(default=None, env="SESSION_SECRET")
    ENCRYPTION_KEY: str | None = Field(default=None, env="ENCRYPTION_KEY")
    DATA_ENCRYPTION_KEY: str | None = Field(default=None, env="DATA_ENCRYPTION_KEY")
    FIELD_ENCRYPTION_KEY: str | None = Field(default=None, env="FIELD_ENCRYPTION_KEY")
    
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(60, env="RATE_LIMIT_REQUESTS_PER_MINUTE")
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

    VAULT_URL: str | None = Field(None, env="VAULT_URL")
    VAULT_TOKEN: SecretStr | None = Field(None, env="VAULT_TOKEN")
    VAULT_ENABLED: bool = Field(False, env="VAULT_ENABLED")

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
    def validate_token_expiration(self) -> "SecuritySettings":
        """Validate that access token expiration does not exceed refresh token expiration."""
        if self.ACCESS_TOKEN_EXPIRE_MINUTES >= (
            self.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60
        ):
            raise ValueError(
                "ACCESS_TOKEN_EXPIRE_MINUTES cannot exceed REFRESH_TOKEN_EXPIRE_DAYS.",
            )
        return self
