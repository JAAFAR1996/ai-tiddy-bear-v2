"""Reusable validation mixins for Pydantic models."""

from pydantic import field_validator

MIN_CHILD_AGE = 1
MAX_CHILD_AGE = 13  # COPPA compliance limit
MAX_NAME_LENGTH = 50
MAX_INTERESTS_COUNT = 20
ALLOWED_LANGUAGES = ["en", "ar", "fr", "es", "de"]


class ChildValidationMixin:
    @field_validator("age")
    @classmethod
    def validate_age(cls, v) -> int:
        if v is not None and v > MAX_CHILD_AGE:
            raise ValueError(
                f"Age must be {MAX_CHILD_AGE} or under for COPPA compliance",
            )
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v) -> str:
        if v is None:
            return v
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        sanitized_name = v.strip()
        if any(char in sanitized_name for char in ["<", ">", "&", '"', "'", "\x00"]):
            raise ValueError("Name contains invalid characters")
        dangerous_patterns = [
            "--",
            ";",
            "DROP",
            "DELETE",
            "INSERT",
            "UPDATE",
            "SELECT",
        ]
        name_upper = sanitized_name.upper()
        if any(pattern in name_upper for pattern in dangerous_patterns):
            raise ValueError("Name contains prohibited patterns")
        return sanitized_name

    @field_validator("interests")
    @classmethod
    def validate_interests(cls, v) -> list[str]:
        if v is None:
            return v
        if len(v) > MAX_INTERESTS_COUNT:
            raise ValueError(f"Maximum {MAX_INTERESTS_COUNT} interests allowed")
        sanitized_interests = []
        for interest in v:
            if not isinstance(interest, str):
                raise ValueError("All interests must be strings")
            sanitized_interest = interest.strip()
            if not sanitized_interest:
                continue
            if any(
                char in sanitized_interest for char in ["<", ">", "&", '"', "'", "\x00"]
            ):
                raise ValueError(
                    f'Interest "{sanitized_interest}" contains invalid characters',
                )
            if len(sanitized_interest) > 50:
                raise ValueError(
                    f'Interest "{sanitized_interest}" is too long (max 50 characters)',
                )
            sanitized_interests.append(sanitized_interest)
        return sanitized_interests

    @field_validator("language")
    @classmethod
    def validate_language(cls, v) -> str:
        if v is not None and v not in ALLOWED_LANGUAGES:
            raise ValueError(f"Language must be one of: {ALLOWED_LANGUAGES}")
        return v
