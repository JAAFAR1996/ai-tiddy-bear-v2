"""Production configuration settings using composition."""
from pathlib import Path
from typing import Any

from pydantic import field_validator, model_validator
from pydantic_settings import SettingsConfigDict

from src.infrastructure.logging_config import get_logger
from src.infrastructure.config.services.ai_settings import AISettings
from .base_settings import BaseApplicationSettings
from .infrastructure_settings import InfrastructureSettings
from src.infrastructure.config.security.security_settings import SecuritySettings

logger = get_logger(__name__, component="config")


class ProductionSettings(BaseApplicationSettings):
    """Production settings using composition pattern to avoid MRO conflicts."""
    
    model_config = SettingsConfigDict(
        env_file=".env.production",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # Production-specific settings
    FORCE_HTTPS: bool = True
    SECURE_COOKIES: bool = True
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Strict"
    
    # Composed settings
    _security: SecuritySettings | None = None
    _infrastructure: InfrastructureSettings | None = None
    _ai: AISettings | None = None
    
    @property
    def security(self) -> SecuritySettings:
        """Lazy-load security settings."""
        if self._security is None:
            self._security = SecuritySettings()
        return self._security
    
    @property
    def infrastructure(self) -> InfrastructureSettings:
        """Lazy-load infrastructure settings."""
        if self._infrastructure is None:
            self._infrastructure = InfrastructureSettings()
        return self._infrastructure
    
    @property
    def ai(self) -> AISettings:
        """Lazy-load AI settings."""
        if self._ai is None:
            self._ai = AISettings()
        return self._ai
    
    @field_validator("FORCE_HTTPS", "SECURE_COOKIES", "SESSION_COOKIE_SECURE", mode="before")
    @classmethod
    def validate_security_flags(cls, v: Any) -> bool:
        """Ensure security flags are properly set in production."""
        if not v:
            logger.warning("Security flag disabled in production - this is not recommended")
        return bool(v)
    
    @model_validator(mode="before")
    @classmethod
    def validate_production_config(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Validate production configuration."""
        # Check for debug mode
        if values.get("DEBUG", False):
            logger.error("DEBUG mode is ON in production! This is a security risk!")
            values["DEBUG"] = False
        
        # Ensure HTTPS
        if not values.get("FORCE_HTTPS", True):
            logger.warning("HTTPS is not enforced in production")
        
        return values
