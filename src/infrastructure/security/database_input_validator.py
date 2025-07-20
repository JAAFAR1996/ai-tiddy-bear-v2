"""🔒 AI Teddy Bear - Database Input Validation Middleware
Database input validation interface for secure data operations.
"""

import functools
from collections.abc import Callable
from datetime import datetime
from typing import Any

from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.sql_injection_protection import (
    QueryValidationResult,
    get_secure_query_builder,
    get_sql_injection_prevention,
)

logger = get_logger(__name__, component="security")


class DatabaseInputValidator:
    """Database input validation interface for secure data operations.
    Automatically applies:
    - SQL Injection prevention
    - Input sanitization
    - Data validation
    - Suspicious attempt logging.
    """

    def __init__(self) -> None:
        self.sql_prevention = get_sql_injection_prevention()
        self.query_builder = get_secure_query_builder()
        self.blocked_attempts = []

    def validate_input_data(
        self,
        data: dict[str, Any],
        table_name: str,
    ) -> dict[str, Any]:
        """Validate input data before inserting into database."""
        validated_data = {}
        threats_detected = []

        for field, value in data.items():
            if value is None:
                validated_data[field] = None
                continue

            # Validate field name
            if not self.sql_prevention.validate_column_name(field):
                raise ValueError(f"Invalid field name: {field}")

            # Determine input type based on field name and table
            input_type = self._determine_input_type(field, table_name)

            # Sanitize the input
            if isinstance(value, str):
                sanitization_result = self.sql_prevention.sanitize_input(
                    value,
                    input_type,
                )
                if not sanitization_result.safe:
                    threats_detected.extend(sanitization_result.threats_found)
                    logger.warning(
                        f"Threats detected in field '{field}': {sanitization_result.threats_found}",
                    )

                # Use sanitized value
                validated_data[field] = sanitization_result.sanitized_input

                # Log modifications if any
                if sanitization_result.modifications:
                    logger.info(
                        f"Input sanitized for field '{field}': {sanitization_result.modifications}",
                    )

            elif isinstance(value, int | float):
                # Validate numeric ranges
                validated_data[field] = self._validate_numeric_input(
                    field,
                    value,
                    table_name,
                )

            elif isinstance(value, bool):
                validated_data[field] = bool(value)

            elif isinstance(value, dict):
                # For JSON fields, validate nested data
                validated_data[field] = self._validate_json_input(value)

            else:
                # For other types, keep as-is but log
                validated_data[field] = value
                logger.debug(
                    f"Non-string field '{field}' passed through: {type(value)}",
                )

        # Log security events if threats were detected
        if threats_detected:
            self.sql_prevention.log_security_event(
                "input_validation_threats",
                {
                    "table": table_name,
                    "fields": list(data.keys()),
                    "threats": threats_detected,
                },
                "high",
            )

        return validated_data

    def _determine_input_type(self, field_name: str, table_name: str) -> str:
        """تحديد نوع المدخل بناءً على اسم الحقل والجدول."""
        # Map field names to input types for validation
        field_type_mapping = {
            # User fields
            "email": "email",
            "first_name": "name",
            "last_name": "name",
            "phone_number": "numeric",
            "password_hash": "text",
            # Child fields
            "name": "name",
            "age": "numeric",
            # ID fields
            "id": "uuid",
            "user_id": "uuid",
            "child_id": "uuid",
            "parent_id": "uuid",
            # Text fields
            "message": "text",
            "content": "text",
            "response": "text",
            "details": "text",
            "description": "text",
            "notes": "text",
            # Specific fields
            "role": "alphanumeric",
            "emotion": "alphanumeric",
            "sentiment": "alphanumeric",
            "event_type": "alphanumeric",
            "severity": "alphanumeric",
        }

        return field_type_mapping.get(field_name, "text")

    def _validate_numeric_input(
        self,
        field_name: str,
        value: float,
        table_name: str,
    ) -> int | float:
        """التحقق من المدخلات الرقمية."""
        # Define numeric ranges for different fields
        numeric_ranges = {
            "age": (0, 18),  # Child age limits for COPPA
            "safety_score": (0.0, 1.0),
            "confidence": (0.0, 1.0),
            "duration": (0, 86400),  # Max 24 hours in seconds
            "failed_login_attempts": (0, 100),
        }

        if field_name in numeric_ranges:
            min_val, max_val = numeric_ranges[field_name]
            if not (min_val <= value <= max_val):
                raise ValueError(
                    f"Value {value} for field '{field_name}' is outside valid range [{min_val}, {max_val}]",
                )

        # Additional validation for specific cases
        if field_name == "age" and table_name == "children" and value > 13:
            raise ValueError("Child age cannot exceed 13 years (COPPA compliance)")

        return value

    def _validate_json_input(self, json_data: dict[str, Any]) -> dict[str, Any]:
        """التحقق من البيانات JSON المتداخلة."""
        validated_json = {}

        for key, value in json_data.items():
            # Validate JSON keys
            if not isinstance(key, str):
                raise ValueError(f"JSON keys must be strings, got {type(key)}")

            if not self.sql_prevention.validate_column_name(key):
                raise ValueError(f"Invalid JSON key: {key}")

            # Recursively validate JSON values
            if isinstance(value, dict):
                validated_json[key] = self._validate_json_input(value)
            elif isinstance(value, str):
                sanitization_result = self.sql_prevention.sanitize_input(value, "text")
                validated_json[key] = sanitization_result.sanitized_input
            elif isinstance(value, list):
                validated_json[key] = [
                    (
                        self.sql_prevention.sanitize_input(item, "text").sanitized_input
                        if isinstance(item, str)
                        else item
                    )
                    for item in value
                ]
            else:
                validated_json[key] = value

        return validated_json

    def validate_query_execution(
        self,
        query: str,
        params: dict[str, Any] | None = None,
    ) -> QueryValidationResult:
        """التحقق من تنفيذ الاستعلام."""
        # Validate the query structure
        validation_result = self.sql_prevention.validate_sql_query(query, params)

        if not validation_result.safe:
            # Log critical security event
            self.sql_prevention.log_security_event(
                "dangerous_query_blocked",
                {
                    "query": query[:200],  # First 200 chars
                    "params": str(params)[:200] if params else None,
                    "errors": validation_result.errors,
                    "threat_level": validation_result.threat_level,
                },
                "critical",
            )

            # Store blocked attempt
            self.blocked_attempts.append(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "query": query[:100],
                    "threat_level": validation_result.threat_level,
                    "errors": validation_result.errors,
                },
            )

            raise DatabaseSecurityError(
                f"Dangerous SQL query blocked: {validation_result.errors}",
            )

        return validation_result


class DatabaseSecurityError(Exception):
    """خطأ أمني مخصص لمنع SQL Injection."""


def database_input_validation(table_name: str):
    """Decorator للتحقق التلقائي من مدخلات قاعدة البيانات
    Usage:
    @database_input_validation("users")
    async def create_user(self, user_data: Dict[str, Any]):
        # The user_data will be automatically validated.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            validator = DatabaseInputValidator()

            # Find data parameters in kwargs
            for param_name in [
                "data",
                "user_data",
                "child_data",
                "update_data",
            ]:
                if param_name in kwargs:
                    validated_data = validator.validate_input_data(
                        kwargs[param_name],
                        table_name,
                    )
                    kwargs[param_name] = validated_data
                    logger.debug(f"Validated input data for table '{table_name}'")

            # Find query parameters
            if "query" in kwargs and "params" in kwargs:
                validation_result = validator.validate_query_execution(
                    kwargs["query"],
                    kwargs["params"],
                )
                if not validation_result.safe:
                    raise DatabaseSecurityError("Query validation failed")

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def validate_database_operation(
    operation: str,
    table_name: str,
    data: dict[str, Any] | None = None,
    where_conditions: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """التحقق من عملية قاعدة البيانات قبل التنفيذ
    Args:
        operation: نوع العملية (SELECT, INSERT, UPDATE, DELETE)
        table_name: اسم الجدول
        data: البيانات للإدراج/التحديث
        where_conditions: شروط WHERE
    Returns:
        Dict containing validated operation details.
    """
    validator = DatabaseInputValidator()

    # Validate table name
    if not validator.sql_prevention.validate_table_name(table_name):
        raise DatabaseSecurityError(f"Invalid table name: {table_name}")

    validated_operation = {
        "operation": operation.upper(),
        "table": table_name,
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Validate data if provided
    if data:
        validated_operation["data"] = validator.validate_input_data(data, table_name)

    # Validate WHERE conditions if provided
    if where_conditions:
        validated_operation["where_conditions"] = validator.validate_input_data(
            where_conditions,
            table_name,
        )

    # Log the operation
    logger.info(f"Database operation validated: {operation} on {table_name}")

    return validated_operation


class SafeDatabaseSession:
    """جلسة قاعدة بيانات آمنة مع حماية من SQL Injection."""

    def __init__(self, database_session) -> None:
        self.session = database_session
        self.validator = DatabaseInputValidator()
        self.operations_log = []

    async def safe_execute(
        self,
        query: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """تنفيذ آمن للاستعلامات."""
        # Validate query before execution
        validation_result = self.validator.validate_query_execution(query, params)
        if not validation_result.safe:
            raise DatabaseSecurityError("Query validation failed")

        # Log the operation
        self.operations_log.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "query": query[:100],
                "param_count": len(params) if params else 0,
                "validation_passed": True,
            },
        )

        # Execute the validated query
        try:
            if params:
                result = await self.session.execute(query, params)
            else:
                result = await self.session.execute(query)
            return result
        except Exception as e:
            logger.error(f"Database execution error: {e}")
            raise

    async def safe_insert(self, table_name: str, data: dict[str, Any]) -> Any:
        """إدراج آمن للبيانات."""
        validated_data = self.validator.validate_input_data(data, table_name)
        query, params = self.validator.query_builder.build_insert(
            table_name,
            validated_data,
        )
        return await self.safe_execute(query, params)

    async def safe_update(
        self,
        table_name: str,
        data: dict[str, Any],
        where_conditions: dict[str, Any],
    ) -> Any:
        """تحديث آمن للبيانات."""
        validated_data = self.validator.validate_input_data(data, table_name)
        validated_where = self.validator.validate_input_data(
            where_conditions,
            table_name,
        )
        query, params = self.validator.query_builder.build_update(
            table_name,
            validated_data,
            validated_where,
        )
        return await self.safe_execute(query, params)

    async def safe_select(
        self,
        table_name: str,
        columns: list[str],
        where_conditions: dict[str, Any] | None = None,
        limit: int | None = None,
    ):
        """استعلام آمن للبيانات."""
        validated_where = None
        if where_conditions:
            validated_where = self.validator.validate_input_data(
                where_conditions,
                table_name,
            )

        query, params = self.validator.query_builder.build_select(
            table_name,
            columns,
            validated_where,
            limit,
        )
        return await self.safe_execute(query, params)

    def get_security_log(self) -> list[dict[str, Any]]:
        """الحصول على سجل العمليات الأمنية."""
        return self.operations_log.copy()


def create_safe_database_session(database_session) -> SafeDatabaseSession:
    """إنشاء جلسة قاعدة بيانات آمنة."""
    return SafeDatabaseSession(database_session)
