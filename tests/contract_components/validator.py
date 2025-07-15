import logging
from typing import Any, Dict

from pydantic import ValidationError

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="test")

_validation_functions = {}


def _validate_string(value: Any, schema: Dict, field_name: str):
    if not isinstance(value, str):
        raise ValidationError(f"Field {field_name} must be a string")
    if "enum" in schema and value not in schema["enum"]:
        raise ValidationError(f"Field {field_name} must be one of {schema['enum']}")


def _validate_integer(value: Any, schema: Dict, field_name: str):
    if not isinstance(value, int):
        raise ValidationError(f"Field {field_name} must be an integer")
    if "minimum" in schema and value < schema["minimum"]:
        raise ValidationError(f"Field {field_name} must be >= {schema['minimum']}")
    if "maximum" in schema and value > schema["maximum"]:
        raise ValidationError(f"Field {field_name} must be <= {schema['maximum']}")


def _validate_number(value: Any, schema: Dict, field_name: str):
    if not isinstance(value, (int, float)):
        raise ValidationError(f"Field {field_name} must be a number")


def _validate_boolean(value: Any, schema: Dict, field_name: str):
    if not isinstance(value, bool):
        raise ValidationError(f"Field {field_name} must be a boolean")


def _validate_array(value: Any, schema: Dict, field_name: str):
    if not isinstance(value, list):
        raise ValidationError(f"Field {field_name} must be an array")


def _validate_object(value: Any, schema: Dict, field_name: str):
    if not isinstance(value, dict):
        raise ValidationError(f"Field {field_name} must be an object")


_validation_functions.update(
    {
        "string": _validate_string,
        "integer": _validate_integer,
        "number": _validate_number,
        "boolean": _validate_boolean,
        "array": _validate_array,
        "object": _validate_object,
    }
)


def _validate_field(value: Any, schema: Dict[str, Any], field_name: str) -> None:
    """Dispatches validation to the correct function based on field type."""
    field_type = schema.get("type")
    validation_function = _validation_functions.get(field_type)

    if validation_function:
        validation_function(value, schema, field_name)
    else:
        logger.warning(f"No validation function for type: {field_type}")


def validate_against_schema(data: Any, schema: Dict[str, Any]) -> None:
    """التحقق من صحة البيانات ضد المخطط"""
    # This is a simplified validation - in production, use a proper JSON
    # schema validator
    if not isinstance(data, dict):
        raise ValidationError("Data must be an object")

    required_fields = schema.get("required", [])
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")

    properties = schema.get("properties", {})
    for field, value in data.items():
        if field in properties:
            field_schema = properties[field]
            _validate_field(value, field_schema, field)
