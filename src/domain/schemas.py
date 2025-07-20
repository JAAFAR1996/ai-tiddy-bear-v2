"""COPPA-Compliant Schema Validation for AI Teddy Bear
Comprehensive data validation with child privacy protection
"""

import logging
import re
from datetime import datetime
from enum import Enum
from typing import Any


class COPPAViolationType(Enum):
    """Types of COPPA violations that can be detected."""

    UNDERAGE_WITHOUT_CONSENT = "underage_without_consent"
    PERSONAL_INFO_COLLECTION = "personal_info_collection"
    EXCESSIVE_DATA_RETENTION = "excessive_data_retention"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    MISSING_PARENTAL_CONSENT = "missing_parental_consent"


class ValidationResult:
    """Result of schema validation with COPPA compliance details."""
    
    def __init__(
        self,
        is_valid: bool,
        errors: list[str] = None,
        coppa_violations: list[COPPAViolationType] = None,
        warnings: list[str] = None,
        metadata: dict[str, Any] = None,
        security_flags: list[str] = None,
    ) -> None:
        self.is_valid = is_valid
        self.errors = errors or []
        self.coppa_violations = coppa_violations or []
        self.warnings = warnings or []
        self.metadata = metadata or {}
        self.security_flags = security_flags or []
        self.timestamp = datetime.utcnow()

    def add_error(self, error: str) -> None:
        """Add validation error."""
        self.errors.append(error)
        self.is_valid = False

    def add_coppa_violation(
        self, violation: COPPAViolationType, description: str
    ) -> None:
        """Add COPPA violation."""
        self.coppa_violations.append(violation)
        self.add_error(f"COPPA Violation - {violation.value}: {description}")


def validate_against_schema(
    data: Any, schema: dict[str, Any], context: dict[str, Any] = None
) -> ValidationResult:
    """Validate data against a schema with comprehensive COPPA compliance checking.
    Args: data: Data to validate
        schema: Schema definition to validate against
        context: Additional context for validation(child_age, parent_consent, etc.)
    Returns: ValidationResult with detailed validation and COPPA compliance information
    """
    context = context or {}
    result = ValidationResult(is_valid=True)
    try:
        # Basic schema validation
        _validate_basic_schema(data, schema, result)
        # COPPA-specific validations
        _validate_coppa_compliance(data, schema, context, result)
        # Child safety validations
        _validate_child_safety(data, schema, context, result)
        # Data retention validations
        _validate_data_retention(data, schema, context, result)

        if result.errors:
            result.is_valid = False

        if result.coppa_violations:
            violations_list = [v.value for v in result.coppa_violations]
            logging.warning(f"COPPA violations detected: {violations_list}")

        return result
    except Exception as e:
        result.add_error(f"Validation system error: {e}")
        return result


def _validate_basic_schema(
    data: Any, schema: dict[str, Any], result: ValidationResult
) -> None:
    """Perform basic schema validation."""
    schema_type = schema.get("type", "object")
    if schema_type == "object" and isinstance(data, dict):
        _validate_object_schema(data, schema, result)
    elif schema_type == "array" and isinstance(data, list):
        _validate_array_schema(data, schema, result)
    elif schema_type == "string" and isinstance(data, str):
        _validate_string_schema(data, schema, result)
    elif schema_type == "integer" and isinstance(data, int):
        _validate_integer_schema(data, schema, result)
    elif schema_type == "boolean" and isinstance(data, bool):
        pass  # Boolean validation is straightforward
    else:
        result.add_error(
            f"Type mismatch: expected '{schema_type}', got '{type(data).__name__}'"
        )


def _validate_object_schema(
    data: dict[str, Any], schema: dict[str, Any], result: ValidationResult
) -> None:
    """Validate object against schema."""
    required_fields = schema.get("required", [])
    properties = schema.get("properties", {})
    # Check required fields
    for field in required_fields:
        if field not in data:
            result.add_error(f"Missing required field: {field}")
    # Validate each property
    for field, value in data.items():
        if field in properties:
            field_result = validate_against_schema(value, properties[field])
            result.errors.extend(field_result.errors)
            result.coppa_violations.extend(field_result.coppa_violations)


def _validate_array_schema(
    data: list[Any], schema: dict[str, Any], result: ValidationResult
) -> None:
    """Validate array against schema."""
    min_items = schema.get("minItems", 0)
    max_items = schema.get("maxItems", float("inf"))
    if len(data) < min_items:
        result.add_error(f"Array too short: {len(data)} < {min_items}")
    if len(data) > max_items:
        result.add_error(f"Array too long: {len(data)} > {max_items}")
    # Validate each item
    item_schema = schema.get("items", {})
    if item_schema:
        for i, item in enumerate(data):
            item_result = validate_against_schema(item, item_schema)
            for error in item_result.errors:
                result.add_error(f"Item {i}: {error}")


def _validate_string_schema(
    data: str, schema: dict[str, Any], result: ValidationResult
) -> None:
    """Validate string against schema."""
    min_length = schema.get("minLength", 0)
    max_length = schema.get("maxLength", float("inf"))
    pattern = schema.get("pattern")
    if len(data) < min_length:
        result.add_error(f"String too short: {len(data)} < {min_length}")
    if len(data) > max_length:
        result.add_error(f"String too long: {len(data)} > {max_length}")
    if pattern and not re.match(pattern, data):
        result.add_error(f"String does not match pattern: {pattern}")


def _validate_integer_schema(
    data: int, schema: dict[str, Any], result: ValidationResult
) -> None:
    """Validate integer against schema."""
    minimum = schema.get("minimum")
    maximum = schema.get("maximum")
    if minimum is not None and data < minimum:
        result.add_error(f"Integer too small: {data} < {minimum}")
    if maximum is not None and data > maximum:
        result.add_error(f"Integer too large: {data} > {maximum}")


def _validate_coppa_compliance(
    data: Any, schema: dict[str, Any], context: dict[str, Any], result: ValidationResult
) -> None:
    """Validate COPPA compliance requirements."""
    child_age = context.get("child_age")
    parent_consent = context.get("parent_consent", False)
    # COPPA applies to children under 13
    if child_age is not None and child_age < 13:
        if not parent_consent:
            result.add_coppa_violation(
                COPPAViolationType.UNDERAGE_WITHOUT_CONSENT,
                "Child under 13 requires verifiable parental consent",
            )
        # Check for prohibited personal information collection
        if isinstance(data, dict):
            prohibited_fields = ["address", "phone", "email", "location", "school"]
            for field in prohibited_fields:
                if data.get(field):
                    result.add_coppa_violation(
                        COPPAViolationType.PERSONAL_INFO_COLLECTION,
                        f"Collection of {field} from children under 13 requires special consent",
                    )


def _validate_child_safety(
    data: Any, schema: dict[str, Any], context: dict[str, Any], result: ValidationResult
) -> None:
    """Validate child safety requirements."""
    if isinstance(data, dict):
        # Check for inappropriate content indicators
        content_fields = ["message", "response", "content", "text"]
        inappropriate_patterns = [
            r"\b(?:meet\\s+me|where\\s+do\\s+you\\s+live|send\\s+photo)\b",
            r"\b(?:secret|password|personal\\s+information)\b",
            r"\b(?:violence|hurt|kill|death)\b",
            r"\b(?:drugs|alcohol|smoking)\b",
        ]
        for field in content_fields:
            if field in data and isinstance(data[field], str):
                for pattern in inappropriate_patterns:
                    if re.search(pattern, data[field], re.IGNORECASE):
                        result.add_coppa_violation(
                            COPPAViolationType.INAPPROPRIATE_CONTENT,
                            f"Inappropriate content detected in {field}",
                        )


def _validate_data_retention(
    data: Any, schema: dict[str, Any], context: dict[str, Any], result: ValidationResult
) -> None:
    """Validate data retention compliance."""
    retention_days = context.get("retention_days", 90)  # Default COPPA retention period
    created_at = context.get("created_at")
    if created_at and isinstance(created_at, datetime):
        age_days = (datetime.utcnow() - created_at).days
        if age_days > retention_days:
            result.add_coppa_violation(
                COPPAViolationType.EXCESSIVE_DATA_RETENTION,
                f"Data retained for {age_days} days exceeds {retention_days} day limit",
            )


# COPPA-compliant schema definitions
CHILD_PROFILE_SCHEMA = {
    "type": "object",
    "required": ["name", "age"],
    "properties": {
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 50,
            "pattern": r"^[a-zA-Z\s\u0600-\u06FF]+$",  # Letters and Arabic characters only
        },
        "age": {"type": "integer", "minimum": 3, "maximum": 13},  # COPPA compliance
        "interests": {
            "type": "array",
            "maxItems": 10,
            "items": {"type": "string", "maxLength": 30},
        },
        "language_preference": {"type": "string", "enum": ["ar", "en", "fr", "es"]},
    },
}

CONVERSATION_SCHEMA = {
    "type": "object",
    "required": ["child_id", "message"],
    "properties": {
        "child_id": {"type": "string", "pattern": r"^[a-zA-Z0-9\-_]+$"},
        "message": {"type": "string", "minLength": 1, "maxLength": 1000},
        "response": {"type": "string", "maxLength": 2000},
        "safety_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    },
}

PARENT_CONSENT_SCHEMA = {
    "type": "object",
    "required": ["parent_email", "child_name", "consent_given", "consent_date"],
    "properties": {
        "parent_email": {
            "type": "string",
            "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        },
        "child_name": {"type": "string", "minLength": 1, "maxLength": 50},
        "consent_given": {"type": "boolean"},
        "consent_date": {
            "type": "string",
            "pattern": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
        },
        "consent_method": {
            "type": "string",
            "enum": ["email_verification", "digital_signature", "phone_verification"],
        },
    },
}

# Export validation functions and schemas
__all__ = [
    "CHILD_PROFILE_SCHEMA",
    "CONVERSATION_SCHEMA",
    "PARENT_CONSENT_SCHEMA",
    "COPPAViolationType",
    "ValidationResult",
    "validate_against_schema",
]


class ValidationSeverity(Enum):
    """Validation issue severity levels."""
    
    INFO = "info"
    WARNING = "warning"  
    ERROR = "error"
    CRITICAL = "critical"


# Validation constants
VALIDATION_PATTERNS = {
    "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "phone": r"^\+?[\d\s\-\(\)]{7,15}$",
    "child_id": r"^child_[a-zA-Z0-9]{8,16}$",
    "parent_id": r"^parent_[a-zA-Z0-9]{8,16}$",
    "safe_text": r"^[\w\s\.\,\!\?\-\'\"]*$",
}

AGE_THRESHOLDS = {
    "min_age": 3,
    "max_age": 17, 
    "coppa_age": 13,
    "teen_age": 13,
}

LENGTH_LIMITS = {
    "child_name": {"min": 1, "max": 50},
    "parent_name": {"min": 1, "max": 100},
    "message": {"min": 1, "max": 1000},
    "email": {"min": 5, "max": 254},
}
