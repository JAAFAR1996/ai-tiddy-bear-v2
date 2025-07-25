"""🔒 SQL Query Validation Service
Advanced SQL injection prevention and query safety
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.audit.child_safe_audit_logger import (
    get_child_safe_audit_logger,
)

logger = get_logger(__name__, component="security")
child_safe_audit = get_child_safe_audit_logger()


@dataclass
class QueryValidationResult:
    """Result of SQL query validation"""

    safe: bool
    errors: list[str]
    warnings: list[str]
    sanitized_query: str | None = None
    threat_level: str = "low"  # low, medium, high, critical


class SQLQueryValidator:
    """Enterprise-grade SQL injection prevention
    Features:
    - Advanced SQL injection pattern detection
    - NoSQL injection prevention
    - Parameterized query validation
    - Query structure analysis
    - Threat level assessment
    """

    def __init__(self) -> None:
        # Critical SQL injection patterns
        self.critical_patterns = [
            r"(\b(UNION|union)\s+(SELECT|select))",
            r"(\b(DROP|drop)\s+(TABLE|table|DATABASE|database))",
            r"(\b(DELETE|delete)\s+(FROM|from))",
            r"(\b(INSERT|insert)\s+(INTO|into))",
            r"(\b(UPDATE|update)\s+\w+\s+(SET|set))",
            r"(\b(ALTER|alter)\s+(TABLE|table))",
            r"(\b(EXEC|exec|EXECUTE|execute))",
            r"(\b(TRUNCATE|truncate))",
        ]

        # High-risk patterns
        self.high_risk_patterns = [
            r"(/\*.*?\*/)",  # SQL comments
            r"(--\s*.*)",  # SQL line comments
            r"(;\s*(DROP|DELETE|UPDATE|INSERT|CREATE|ALTER))",  # Chained commands
            r"(\b(OR|or)\s+\w+\s*(=|!=|<>)\s*\w+)",  # OR conditions
            r"(1\s*(=|!=)\s*1)",  # Always true/false
            r"(''\s*(=|!=)\s*'')",  # Empty string comparisons
        ]

        # NoSQL injection patterns
        self.nosql_patterns = [
            r"(\$ne|\$eq|\$gt|\$lt|\$gte|\$lte)",
            r"(\$where|\$regex|\$in|\$nin)",
            r"(\$or|\$and|\$not|\$nor)",
            r"(this\.)",
            r"(function\s*\()",
            r"(ObjectId\s*\()",
        ]

        # Safe table whitelist for child safety app
        self.safe_tables = [
            "parents",
            "children",
            "conversations",
            "messages",
            "safety_events",
            "consents",
            "audit_logs",
        ]

        logger.info("SQL Query Validator initialized")

    def validate_query_parameters(
        self, params: dict[str, Any]
    ) -> QueryValidationResult:
        """Validate query parameters for SQL injection"""
        validation = QueryValidationResult(
            safe=True, errors=[], warnings=[], threat_level="low"
        )

        for key, value in params.items():
            if value is None:
                continue

            str_value = str(value)

            # Check critical patterns
            for pattern in self.critical_patterns:
                if re.search(pattern, str_value, re.IGNORECASE):
                    validation.safe = False
                    validation.errors.append(
                        f"Critical SQL injection pattern in '{key}': {pattern}"
                    )
                    validation.threat_level = "critical"
                    child_safe_audit.log_security_event(
                        event_type="critical_sql_injection",
                        threat_level="critical",
                        input_data=str_value,
                        context={"parameter_name": key, "pattern": pattern},
                    )

            # Check high-risk patterns
            for pattern in self.high_risk_patterns:
                if re.search(pattern, str_value, re.IGNORECASE):
                    validation.safe = False
                    validation.errors.append(
                        f"High-risk SQL pattern in '{key}': {pattern}"
                    )
                    validation.threat_level = (
                        "high" if validation.threat_level != "critical" else "critical"
                    )
                    child_safe_audit.log_security_event(
                        event_type="high_risk_sql_pattern",
                        threat_level="high",
                        input_data=str_value,
                        context={"parameter_name": key, "pattern": pattern},
                    )

            # Check NoSQL patterns
            for pattern in self.nosql_patterns:
                if re.search(pattern, str_value, re.IGNORECASE):
                    validation.safe = False
                    validation.errors.append(
                        f"NoSQL injection pattern in '{key}': {pattern}"
                    )
                    if validation.threat_level == "low":
                        validation.threat_level = "medium"
                    child_safe_audit.log_security_event(
                        event_type="nosql_injection_attempt",
                        threat_level="medium",
                        input_data=str_value,
                        context={"parameter_name": key, "pattern": pattern},
                    )

        return validation

    def validate_table_name(self, table_name: str) -> bool:
        """Validate table name against whitelist"""
        # Must be alphanumeric with underscores
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name):
            child_safe_audit.log_security_event(
                event_type="invalid_table_name_format",
                threat_level="medium",
                input_data=table_name,
                context={"validation_type": "table_name_format"},
            )
            return False

        # Must be in whitelist
        if table_name not in self.safe_tables:
            child_safe_audit.log_security_event(
                event_type="table_name_not_whitelisted",
                threat_level="medium",
                input_data=table_name,
                context={
                    "validation_type": "table_name_whitelist",
                    "safe_tables": self.safe_tables,
                },
            )
            return False

        return True

    def validate_column_name(self, column_name: str) -> bool:
        """Validate column name format"""
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", column_name):
            child_safe_audit.log_security_event(
                event_type="invalid_column_name",
                threat_level="medium",
                input_data=column_name,
                context={"validation_type": "column_name_format"},
            )
            return False

        # Check for SQL reserved words
        sql_reserved = [
            "SELECT",
            "FROM",
            "WHERE",
            "INSERT",
            "UPDATE",
            "DELETE",
            "DROP",
            "CREATE",
            "ALTER",
            "UNION",
            "EXEC",
            "EXECUTE",
            "DECLARE",
            "CAST",
        ]
        if column_name.upper() in sql_reserved:
            child_safe_audit.log_security_event(
                event_type="sql_reserved_word_detected",
                threat_level="high",
                input_data=column_name,
                context={"validation_type": "sql_reserved_word"},
            )
            return False

        return True

    def create_safe_where_clause(
        self, conditions: dict[str, Any]
    ) -> tuple[str, list[Any]]:
        """Create safe parameterized WHERE clause"""
        where_parts = []
        params = []

        for column, value in conditions.items():
            # Validate column name
            if not self.validate_column_name(column):
                raise ValueError(f"Invalid column name: {column}")

            # Validate value safety
            if isinstance(value, str):
                param_validation = self.validate_query_parameters({column: value})
                if not param_validation.safe:
                    raise ValueError(
                        f"Unsafe value for column {column}: {param_validation.errors}"
                    )

            where_parts.append(f"{column} = ?")
            params.append(value)

        where_clause = " AND ".join(where_parts) if where_parts else "1=1"
        return where_clause, params

    def validate_child_data_query(
        self, table_name: str, conditions: dict[str, Any]
    ) -> QueryValidationResult:
        """Special validation for queries involving child data"""
        validation = QueryValidationResult(
            safe=True, errors=[], warnings=[], threat_level="low"
        )

        # Validate table name
        if not self.validate_table_name(table_name):
            validation.safe = False
            validation.errors.append(f"Invalid or unsafe table name: {table_name}")
            validation.threat_level = "high"

        # Extra validation for child-related tables
        if table_name in ["children", "conversations", "messages"]:
            # Ensure child_id is present for data isolation
            if "child_id" not in conditions:
                validation.warnings.append(
                    "Child data query without child_id filter - potential data leak"
                )

            # Validate all conditions
            param_validation = self.validate_query_parameters(conditions)
            if not param_validation.safe:
                validation.safe = False
                validation.errors.extend(param_validation.errors)
                validation.threat_level = param_validation.threat_level

        return validation

    def log_security_event(
        self,
        event_type: str,
        details: dict[str, Any],
        severity: str = "medium",
    ) -> None:
        """Log security event for monitoring"""
        security_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "details": details,
            "source": "sql_query_validator",
        }

        # Log the security event
        if severity in ["high", "critical"]:
            logger.error(f"Security Event ({severity}): {event_type} - {details}")
        else:
            logger.warning(f"Security Event ({severity}): {event_type} - {details}")

        # In production, this would also send to SIEM/monitoring system
        # Example: send_to_security_monitoring(security_event)

    def sanitize_query_string(self, query: str) -> str:
        """Sanitize a raw query string (use with extreme caution)"""
        # Remove SQL comments
        query = re.sub(r"--.*$", "", query, flags=re.MULTILINE)
        query = re.sub(r"/\*.*?\*/", "", query, flags=re.DOTALL)

        # Remove dangerous keywords
        dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "EXEC", "EXECUTE"]
        for keyword in dangerous_keywords:
            query = re.sub(rf"\b{keyword}\b", "", query, flags=re.IGNORECASE)

        # Remove multiple spaces
        query = re.sub(r"\s+", " ", query).strip()

        child_safe_audit.log_security_event(
            event_type="query_sanitization",
            threat_level="high",
            input_data=query,
            context={"operation": "query_sanitization"},
        )
        return query

    def get_safe_limit_offset(
        self, limit: int = None, offset: int = None
    ) -> tuple[int, int]:
        """Get safe LIMIT and OFFSET values"""
        # Default and maximum limits for child safety
        DEFAULT_LIMIT = 50
        MAX_LIMIT = 1000
        MAX_OFFSET = 10000

        # Validate and sanitize limit
        if limit is None:
            limit = DEFAULT_LIMIT
        else:
            try:
                limit = int(limit)
                if limit <= 0:
                    limit = DEFAULT_LIMIT
                elif limit > MAX_LIMIT:
                    limit = MAX_LIMIT
                    logger.warning(f"Limit capped at maximum: {MAX_LIMIT}")
            except (ValueError, TypeError):
                limit = DEFAULT_LIMIT
                logger.warning("Invalid limit value, using default")

        # Validate and sanitize offset
        if offset is None:
            offset = 0
        else:
            try:
                offset = int(offset)
                if offset < 0:
                    offset = 0
                elif offset > MAX_OFFSET:
                    offset = MAX_OFFSET
                    logger.warning(f"Offset capped at maximum: {MAX_OFFSET}")
            except (ValueError, TypeError):
                offset = 0
                logger.warning("Invalid offset value, using default")

        return limit, offset


# Global instance
_query_validator: SQLQueryValidator | None = None


def get_query_validator() -> SQLQueryValidator:
    """Get global query validator instance"""
    global _query_validator
    if _query_validator is None:
        _query_validator = SQLQueryValidator()
    return _query_validator


# Convenience functions for common operations
def validate_params(params: dict[str, Any]) -> QueryValidationResult:
    """Quick parameter validation"""
    validator = get_query_validator()
    return validator.validate_query_parameters(params)


def is_safe_table(table_name: str) -> bool:
    """Quick table name validation"""
    validator = get_query_validator()
    return validator.validate_table_name(table_name)


def is_safe_column(column_name: str) -> bool:
    """Quick column name validation"""
    validator = get_query_validator()
    return validator.validate_column_name(column_name)


def create_safe_where(conditions: dict[str, Any]) -> tuple[str, list[Any]]:
    """Quick safe WHERE clause creation"""
    validator = get_query_validator()
    return validator.create_safe_where_clause(conditions)


def validate_child_query(
    table_name: str, conditions: dict[str, Any]
) -> QueryValidationResult:
    """Quick child data query validation"""
    validator = get_query_validator()
    return validator.validate_child_data_query(table_name, conditions)


QueryValidator = SQLQueryValidator
