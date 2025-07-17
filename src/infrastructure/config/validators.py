from typing import List, Optional, Dict, Any, Union
import os
import secrets
import re
import logging
from pydantic import field_validator

logger = logging.getLogger(__name__)

class SettingsValidators:
    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate that SECRET_KEY is set and secure."""
        if not v or v == "...":  # Handle ellipsis default
            env = os.getenv("ENVIRONMENT")
            if env == "production":
                raise ValueError("SECRET_KEY must be set in production")
            # Generate secure key for dev only
            v = secrets.token_urlsafe(32)
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        insecure_values = {"secret", "password", "changeme", "default", "dev"}
        if v.lower() in insecure_values:
            raise ValueError("SECRET_KEY cannot be a common/insecure value")
        return v

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Ensure PostgreSQL in production."""
        if os.getenv("ENVIRONMENT") == "production" and not v.startswith("postgresql"):
            raise ValueError("PostgreSQL is required for production environments.")
        weak_patterns = [
            "user:password",
            "user:pass",
            "admin:admin",
            "root:root",
            "test:test",
            "password123",
            "12345",
            "admin123",
            "default",
            "changeme",
            "welcome",
            "letmein",
            "temp",
            "demo",
            "example",
            "sample",
        ]
        if any(pattern in v.lower() for pattern in weak_patterns):
            logger.critical(
                "SECURITY ALERT: Insecure default credentials detected in DATABASE_URL"
            )
            if os.getenv("ENVIRONMENT") == "production":
                raise ValueError(
                    "Production environment cannot use default/weak credentials in DATABASE_URL"
                )
        return v