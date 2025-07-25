"""Comprehensive Validator

Main validation service that combines all validation modules for unified
validation. Provides a single interface for all validation needs with proper
delegation.
"""

from typing import Any

from src.domain.schemas import ValidationResult
from src.infrastructure.logging_config import get_logger
from src.infrastructure.validators.security.child_safety_validator import (
    get_child_safety_validator,
)

from .general_input_validator import get_general_input_validator

logger = get_logger(__name__, component="validation")


class ComprehensiveValidator:
    """Comprehensive validation service that combines all validators.

    Features:
    - Unified validation interface
    - Child safety validation (COPPA compliant)
    - General input validation
    - Security-focused validation
    - Proper error handling and logging
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize comprehensive validator with all sub-validators."""
        config = config or {}

        # Initialize sub-validators
        self.child_safety = get_child_safety_validator()
        self.general_input = get_general_input_validator()

        # Validation configuration
        self.strict_mode = config.get("strict_mode", True)
        self.enable_logging = config.get("enable_logging", True)

        logger.info("Comprehensive validator initialized")

    def validate_child_registration(
        self,
        child_data: dict[str, Any],
    ) -> ValidationResult:
        """Comprehensive validation for child registration data.

        Args:
            child_data: Dictionary containing child registration information

        Returns:
            ValidationResult with comprehensive validation results.
        """
        errors = []
        metadata = {}
        security_flags = []

        # Validate required fields
        required_fields = ["name", "age"]
        for field in required_fields:
            if field not in child_data or not child_data[field]:
                errors.append(f"Field '{field}' is required")

        if errors:
            return ValidationResult(
                valid=False,
                errors=errors,
                metadata={"code": "MISSING_REQUIRED_FIELDS"},
            )

        # Validate child name
        name_result = self._validate_child_name(child_data["name"])
        if not name_result.valid:
            errors.extend(name_result.errors)
        else:
            child_data["name"] = name_result.sanitized_value

        # Validate child age
        age_result = self.child_safety.validate_child_age(child_data["age"])
        if not age_result.valid:
            errors.extend(age_result.errors)
        else:
            child_data["age"] = age_result.sanitized_value
            metadata.update(age_result.metadata)

        # Validate parent email if provided
        if child_data.get("parent_email"):
            email_result = self.general_input.validate_email(child_data["parent_email"])
            if not email_result.valid:
                errors.extend(
                    [f"Parent email: {error}" for error in email_result.errors],
                )
            else:
                child_data["parent_email"] = email_result.sanitized_value

        # Additional validations based on age
        if age_result.valid and age_result.metadata.get("coppa_applicable"):
            if "parent_email" not in child_data or not child_data["parent_email"]:
                errors.append(
                    "Parent email is required for children under 13 "
                    "(COPPA compliance)",
                )

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            sanitized_value=child_data if len(errors) == 0 else None,
            metadata=metadata,
            security_flags=security_flags,
        )

    def validate_message_input(self, message_data: dict[str, Any]) -> ValidationResult:
        """Validate message input from child with comprehensive safety checks.

        Args:
            message_data: Dictionary containing message and context

        Returns:
            ValidationResult with validation results.
        """
        errors = []
        metadata = {}

        # Extract message and child info
        message = message_data.get("message", "")
        child_age = message_data.get("child_age")

        if not message:
            return ValidationResult(
                valid=False,
                errors=["Message cannot be empty"],
                metadata={"code": "EMPTY_MESSAGE"},
            )

        # Validate message safety
        message_result = self.child_safety.validate_child_message(message, child_age)

        # Handle dict result from child_safety validator
        if isinstance(message_result, dict):
            if not message_result.get("valid", False):
                errors.append(message_result.get("reason", "Invalid message"))
            else:
                metadata.update(
                    {
                        "appropriateness_score": message_result.get(
                            "appropriateness_score"
                        ),
                        "age_appropriate": message_result.get("age_appropriate"),
                    }
                )
                message_data["message"] = message_result.get(
                    "sanitized_message", message
                )
        elif not message_result.valid:
            errors.extend(message_result.errors)
            if hasattr(message_result, "security_flags"):
                metadata["security_flags"] = message_result.security_flags
        else:
            metadata.update(message_result.metadata)
            message_data["message"] = message_result.sanitized_value

        # Additional text validation for security
        text_result = self.general_input.validate_text_input(message, max_length=1000)
        if not text_result.valid:
            errors.extend(text_result.errors)
            if hasattr(text_result, "security_flags"):
                metadata.setdefault("security_flags", []).extend(
                    text_result.security_flags,
                )

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            sanitized_value=message_data if len(errors) == 0 else None,
            metadata=metadata,
        )

    def validate_file_upload(self, file_data: dict[str, Any]) -> ValidationResult:
        """Validate file upload with security and safety checks.

        Args:
            file_data: Dictionary containing file information

        Returns:
            ValidationResult with validation results.
        """
        required_fields = ["filename", "file_size"]
        errors = []

        # Check required fields
        for field in required_fields:
            if field not in file_data:
                errors.append(f"Field '{field}' is required")

        if errors:
            return ValidationResult(
                valid=False,
                errors=errors,
                metadata={"code": "MISSING_FILE_DATA"},
            )

        # Validate file upload
        file_result = self.general_input.validate_file_upload(
            filename=file_data["filename"],
            file_size=file_data["file_size"],
            file_content=file_data.get("file_content"),
        )

        if file_result.valid:
            file_data["filename"] = file_result.sanitized_value

        return file_result

    def validate_parent_data(self, parent_data: dict[str, Any]) -> ValidationResult:
        """Validate parent/guardian data.

        Args:
            parent_data: Dictionary containing parent information

        Returns:
            ValidationResult with validation results.
        """
        errors = []
        sanitized_data = parent_data.copy()

        # Validate email
        if parent_data.get("email"):
            email_result = self.general_input.validate_email(parent_data["email"])
            if not email_result.valid:
                errors.extend([f"Email: {error}" for error in email_result.errors])
            else:
                sanitized_data["email"] = email_result.sanitized_value

        # Validate name if provided
        if parent_data.get("name"):
            name_text = parent_data["name"]
            if len(name_text) < 2 or len(name_text) > 100:
                errors.append("Parent name must be between 2 and 100 characters")
            else:
                # Basic text validation
                text_result = self.general_input.validate_text_input(
                    name_text,
                    max_length=100,
                )
                if not text_result.valid:
                    errors.extend([f"Name: {error}" for error in text_result.errors])
                else:
                    sanitized_data["name"] = text_result.sanitized_value

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            sanitized_value=sanitized_data if len(errors) == 0 else None,
        )

    def validate_search_query(
        self,
        query: str,
        child_age: int | None = None,
    ) -> ValidationResult:
        """Validate search query for child safety.

        Args:
            query: Search query string
            child_age: Optional child age for context

        Returns:
            ValidationResult with validation results.
        """
        if not query or not isinstance(query, str):
            return ValidationResult(
                valid=False,
                errors=["Search query cannot be empty"],
                metadata={"code": "EMPTY_QUERY"},
            )

        # Basic text validation
        text_result = self.general_input.validate_text_input(query, max_length=200)
        if not text_result.valid:
            return text_result

        # Child safety validation if age provided
        if child_age is not None:
            message_result = self.child_safety.validate_child_message(query, child_age)

            # Handle dict result
            if isinstance(message_result, dict):
                if not message_result.get("valid", False):
                    return ValidationResult(
                        valid=False,
                        errors=[message_result.get("reason", "Invalid query")],
                        metadata={"code": message_result.get("code")},
                    )
            elif not message_result.valid:
                return message_result

        return ValidationResult(
            valid=True,
            original_value=query,
            sanitized_value=text_result.sanitized_value,
        )

    def _validate_child_name(self, name: str) -> ValidationResult:
        """Validate child's name."""
        if not name or not isinstance(name, str):
            return ValidationResult(
                valid=False,
                errors=["Name is required"],
            )

        if len(name) < 2 or len(name) > 50:
            return ValidationResult(
                valid=False,
                errors=["Name must be between 2 and 50 characters"],
            )

        # Use general text validation
        return self.general_input.validate_text_input(name, max_length=50)


# Factory function for dependency injection
def get_comprehensive_validator(
    config: dict[str, Any] | None = None,
) -> ComprehensiveValidator:
    """Create and configure comprehensive validator instance."""
    return ComprehensiveValidator(config)


# Convenient validation functions
def validate_child_registration(
    child_data: dict[str, Any],
) -> ValidationResult:
    """Convenient function for child registration validation."""
    validator = get_comprehensive_validator()
    return validator.validate_child_registration(child_data)


def validate_message_input(message_data: dict[str, Any]) -> ValidationResult:
    """Convenient function for message validation."""
    validator = get_comprehensive_validator()
    return validator.validate_message_input(message_data)


def validate_file_upload(file_data: dict[str, Any]) -> ValidationResult:
    """Convenient function for file upload validation."""
    validator = get_comprehensive_validator()
    return validator.validate_file_upload(file_data)
