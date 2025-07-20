# src/infrastructure/config/base_settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseApplicationSettings(BaseSettings):
    '''Base settings for all environments.'''
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        env_nested_delimiter="__",
    )
