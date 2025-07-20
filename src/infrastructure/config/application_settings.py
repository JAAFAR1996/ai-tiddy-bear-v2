# src/infrastructure/config/application_settings.py
from pathlib import Path
from pydantic import Field
from src.common import constants
from src.infrastructure.config.base_settings import BaseApplicationSettings

class ApplicationSettings(BaseApplicationSettings):
    '''General application configuration settings.'''
    
    # إزالة env من جميع الحقول لمنع القراءة المباشرة
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=False)
    APP_NAME: str = Field(default="AI Teddy Bear System")
    APP_VERSION: str = Field(default="2.0.0")
    ENABLE_HTTPS: bool = Field(default=True)
    CORS_ORIGINS: list[str] | None = Field(default=None)
    TRUSTED_HOSTS: list[str] | None = Field(default=None)
    MAX_SESSION_DURATION_SECONDS: int = Field(default=3600)
    CHILD_ENDPOINTS: list[str] = Field(
        default_factory=lambda: constants.CHILD_SPECIFIC_API_ENDPOINTS
    )
    MIN_CHILD_AGE: int = Field(default=3)
    MAX_CHILD_AGE: int = Field(default=13)
    PROJECT_ROOT: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent.parent.resolve()
    )
    STATIC_FILES_DIR: str = Field(default="static")
    
    # المتغيرات الإضافية
    ENABLE_AI_SERVICES: bool = Field(default=True)
    USE_MOCK_SERVICES: bool = Field(default=False)
    
    # إعدادات السجلات
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="json")
    LOG_FILE: str = Field(default="logs/ai_teddy.log")
