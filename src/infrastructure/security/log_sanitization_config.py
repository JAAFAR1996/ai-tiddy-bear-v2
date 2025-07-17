from dataclasses import dataclass
from typing import List

@dataclass
class LogSanitizationConfig:
    """Configuration for log sanitization."""
    # Patterns to redact completely
    redact_patterns: List[str]
    # Patterns to partially mask (show first/last few characters)
    mask_patterns: List[str]
    # Fields that should never be logged
    forbidden_fields: List[str]
    # Maximum length for log values
    max_value_length: int = 100

def get_default_log_sanitization_config() -> LogSanitizationConfig:
    """Get default sanitization configuration for child-safe system."""
    return LogSanitizationConfig(
        redact_patterns=[
            r"password",
            r"secret",
            r"token",
            r"api_key",
            r"private_key",
            r"auth",
            r"credential",
            r"session",
            r"cookie",
            r"bearer",
        ],
        mask_patterns=[
            r"email",
            r"phone",
            r"address",
            r"ssn",
            r"credit",
            r"card",
            r"account",
        ],
        forbidden_fields=[
            "password",
            "secret_key",
            "api_key",
            "private_key",
            "token",
            "session_id",
            "auth_header",
            "bearer_token",
            "child_personal_info",
            "parent_contact_info",
        ],
        max_value_length=100,
    )

def create_child_safe_log_sanitization_config() -> LogSanitizationConfig:
    """Create a log sanitization configuration specifically for child-safe logging."""
    return LogSanitizationConfig(
        redact_patterns=[
            r"password",
            r"secret",
            r"token",
            r"api_key",
            r"private_key",
            r"auth",
            r"credential",
            r"session",
            r"cookie",
            r"bearer",
            r"personal",
            r"contact",
            r"address",
            r"phone",
        ],
        mask_patterns=[
            r"child_id",
            r"parent_id",
            r"user_id",
            r"email",
        ],
        forbidden_fields=[
            "password",
            "secret_key",
            "api_key",
            "private_key",
            "token",
            "session_id",
            "auth_header",
            "bearer_token",
            "child_name",
            "child_dob",
            "parent_name",
            "parent_email",
            "parent_phone",
            "address",
            "ip_address",
        ],
        max_value_length=80,  # Stricter length limit
    )