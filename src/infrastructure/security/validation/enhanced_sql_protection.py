"""🔒 Enhanced SQL Injection Protection - Production Security Implementation

Enterprise-grade SQL injection protection for the AI Teddy Bear child safety platform.
"""

import re
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.sql import ClauseElement

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


class EnhancedSQLProtection:
    """Enhanced SQL injection protection with comprehensive validation."""

    def __init__(self):
        """Initialize enhanced SQL protection system."""
        self.blocked_attempts = []

        # Critical SQL injection patterns for child data protection
        self.critical_patterns = [
            r"(\bunion\s+select\b)",
            r"(\bdrop\s+(table|database|schema)\b)",
            r"(\bdelete\s+from\b)",
            r"(\binsert\s+into\b)",
            r"(\bupdate\s+\w+\s+set\b)",
            r"(\balter\s+table\b)",
            r"(\btruncate\s+table\b)",
            r"(\bexec\w*\s*\()",
            r"(\beval\s*\()",
            r"(\bcreate\s+(table|view|function|procedure)\b)",
        ]

        # High-risk patterns
        self.high_risk_patterns = [
            r"(--[^\r\n]*)",  # SQL comments
            r"(/\*.*?\*/)",  # Multi-line comments
            r"(\bor\s+\d+\s*=\s*\d+)",  # Always true conditions
            r"(\band\s+\d+\s*=\s*\d+)",  # Always true conditions
            r"('.*';\s*\w+)",  # Statement termination with command
            r"(\bxp_cmdshell\b)",  # SQL Server command execution
            r"(\bsp_\w+\b)",  # Stored procedures
            r"(\binto\s+outfile\b)",  # File operations
            r"(\bload_file\s*\()",  # File reading
        ]

        # Child data table whitelist for extra protection
        self.allowed_child_tables = {
            "children",
            "conversations",
            "safety_events",
            "parent_consent",
            "audit_logs",
            "data_retention_records",
            "emergency_contacts",
        }

        # Allowed operations for child data
        self.allowed_operations = {
            "SELECT",
            "INSERT",
            "UPDATE",  # DELETE only through secure service
        }

    def validate_input(self, value: Any) -> bool:
        """Validate input for SQL injection patterns."""
        if value is None:
            return True

        if not isinstance(value, (str, int, float, bool)):
            value = str(value)

        str_value = str(value).strip()

        if not str_value:
            return True

        # Check critical patterns first
        for pattern in self.critical_patterns:
            if re.search(pattern, str_value, re.IGNORECASE | re.MULTILINE):
                self._log_blocked_attempt("CRITICAL", pattern, str_value)
                return False

        # Check high-risk patterns
        for pattern in self.high_risk_patterns:
            if re.search(pattern, str_value, re.IGNORECASE | re.MULTILINE):
                self._log_blocked_attempt("HIGH", pattern, str_value)
                return False

        # Check for dangerous character combinations
        dangerous_chars = ["';", '";', "';--", '";--', "' OR ", '" OR ']
        for chars in dangerous_chars:
            if chars in str_value.upper():
                self._log_blocked_attempt(
                    "MEDIUM", f"dangerous_chars:{chars}", str_value
                )
                return False

        return True

    def validate_table_access(self, table_name: str, operation: str) -> bool:
        """Validate table access for child data protection."""
        if not table_name or not operation:
            return False

        table_clean = table_name.lower().strip()
        operation_clean = operation.upper().strip()

        # Extra protection for child tables
        if table_clean in self.allowed_child_tables:
            if operation_clean not in self.allowed_operations:
                self._log_blocked_attempt(
                    "CRITICAL",
                    f"unauthorized_child_table_operation:{operation_clean}",
                    f"table:{table_name}",
                )
                return False

        # Validate table name format
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_clean):
            self._log_blocked_attempt("HIGH", "invalid_table_name", table_name)
            return False

        return True

    def sanitize_input(self, value: str) -> str:
        """Sanitize input string with comprehensive cleaning."""
        if not value:
            return ""

        # Remove SQL comments
        value = re.sub(r"--[^\r\n]*", "", value)
        value = re.sub(r"/\*.*?\*/", "", value, flags=re.DOTALL)

        # Remove dangerous SQL keywords (preserve as escaped)
        dangerous_keywords = [
            "UNION",
            "SELECT",
            "INSERT",
            "UPDATE",
            "DELETE",
            "DROP",
            "CREATE",
            "ALTER",
            "EXEC",
            "EXECUTE",
            "TRUNCATE",
        ]

        for keyword in dangerous_keywords:
            # Replace standalone keywords with escaped version
            pattern = r"\b" + re.escape(keyword) + r"\b"
            value = re.sub(pattern, f"[{keyword}]", value, flags=re.IGNORECASE)

        # Remove or escape dangerous characters
        value = value.replace(";", "\\;")
        value = value.replace("'", "\\'")
        value = value.replace('"', '\\"')
        value = re.sub(r"[<>]", "", value)  # Remove angle brackets

        # Normalize whitespace
        value = re.sub(r"\s+", " ", value).strip()

        return value

    def _log_blocked_attempt(self, severity: str, pattern: str, input_value: str):
        """Log blocked SQL injection attempt with audit trail."""
        attempt = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "severity": severity,
            "pattern": pattern,
            "input_preview": input_value[:100],  # First 100 chars only
            "input_hash": self._hash_input(input_value),
        }

        self.blocked_attempts.append(attempt)

        # Keep only last 1000 attempts to prevent memory issues
        if len(self.blocked_attempts) > 1000:
            self.blocked_attempts = self.blocked_attempts[-1000:]

        logger.warning(
            f"SQL injection attempt blocked - Severity: {severity}, "
            f"Pattern: {pattern}, Input hash: {attempt['input_hash']}"
        )

    def _hash_input(self, input_value: str) -> str:
        """Create hash of input for audit purposes."""
        import hashlib

        return hashlib.sha256(input_value.encode()).hexdigest()[:16]

    def get_security_summary(self) -> dict[str, Any]:
        """Get summary of blocked attempts for security monitoring."""
        total_attempts = len(self.blocked_attempts)
        severity_counts = {}

        for attempt in self.blocked_attempts:
            severity = attempt["severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return {
            "total_blocked": total_attempts,
            "severity_breakdown": severity_counts,
            "recent_attempts": (
                self.blocked_attempts[-10:] if self.blocked_attempts else []
            ),
        }


class SecureQueryHelper:
    """Secure query helper for child data protection."""

    def __init__(self):
        """Initialize secure query helper."""
        self.protection = EnhancedSQLProtection()
        self.audit_trail = []

    def build_safe_select(
        self,
        table_name: str,
        columns: list[str],
        where_conditions: dict[str, Any] | None = None,
        limit: int | None = None,
        order_by: str | None = None,
    ) -> tuple[ClauseElement, dict[str, Any]]:
        """Build secure SELECT query using SQLAlchemy."""
        # Validate inputs
        if not self.protection.validate_table_access(table_name, "SELECT"):
            raise SecurityError(f"Unauthorized table access: {table_name}")

        # Validate columns
        safe_columns = []
        for col in columns:
            if not self._validate_column_name(col):
                raise SecurityError(f"Invalid column name: {col}")
            safe_columns.append(col)

        # Build query using SQLAlchemy text for maximum security
        column_list = ", ".join(safe_columns)
        base_query = f"SELECT {column_list} FROM {table_name}"

        params = {}

        # Add WHERE conditions safely
        if where_conditions:
            where_clause, where_params = self._build_where_clause(where_conditions)
            base_query += f" WHERE {where_clause}"
            params.update(where_params)

        # Add ORDER BY safely
        if order_by and self._validate_column_name(order_by):
            base_query += f" ORDER BY {order_by}"

        # Add LIMIT safely
        if limit and isinstance(limit, int) and 0 < limit <= 10000:
            base_query += f" LIMIT {limit}"

        query = text(base_query)

        self._log_query_build("SELECT", table_name, params)

        return query, params

    def build_safe_insert(
        self, table_name: str, data: dict[str, Any]
    ) -> tuple[ClauseElement, dict[str, Any]]:
        """Build secure INSERT query using SQLAlchemy."""
        if not self.protection.validate_table_access(table_name, "INSERT"):
            raise SecurityError(f"Unauthorized table access: {table_name}")

        # Validate and sanitize data
        safe_data = {}
        for key, value in data.items():
            if not self._validate_column_name(key):
                raise SecurityError(f"Invalid column name: {key}")
            if not self.protection.validate_input(value):
                raise SecurityError(f"Invalid value for column {key}")
            safe_data[key] = value

        # Build parameterized INSERT
        columns = list(safe_data.keys())
        placeholders = [f":{col}" for col in columns]

        query_text = (
            f"INSERT INTO {table_name} ({', '.join(columns)}) "
            f"VALUES ({', '.join(placeholders)})"
        )
        query = text(query_text)

        self._log_query_build("INSERT", table_name, safe_data)

        return query, safe_data

    def build_safe_update(
        self, table_name: str, data: dict[str, Any], where_conditions: dict[str, Any]
    ) -> tuple[ClauseElement, dict[str, Any]]:
        """Build secure UPDATE query using SQLAlchemy."""
        if not self.protection.validate_table_access(table_name, "UPDATE"):
            raise SecurityError(f"Unauthorized table access: {table_name}")

        if not where_conditions:
            raise SecurityError("UPDATE queries must have WHERE conditions")

        # Validate and prepare SET clause
        set_clauses = []
        params = {}

        for key, value in data.items():
            if not self._validate_column_name(key):
                raise SecurityError(f"Invalid column name: {key}")
            if not self.protection.validate_input(value):
                raise SecurityError(f"Invalid value for column {key}")

            param_name = f"set_{key}"
            set_clauses.append(f"{key} = :{param_name}")
            params[param_name] = value

        # Build WHERE clause
        where_clause, where_params = self._build_where_clause(
            where_conditions, "where_"
        )
        params.update(where_params)

        query_text = (
            f"UPDATE {table_name} SET {', '.join(set_clauses)} " f"WHERE {where_clause}"
        )
        query = text(query_text)

        self._log_query_build("UPDATE", table_name, params)

        return query, params

    def build_safe_delete(
        self,
        table_name: str,
        where_conditions: dict[str, Any],
        require_child_id: bool = True,
    ) -> tuple[ClauseElement, dict[str, Any]]:
        """Build secure DELETE query with extra child data protection."""
        # Extra protection: require explicit child_id for child data deletion
        if require_child_id and "child_id" not in where_conditions:
            raise SecurityError("DELETE operations on child data require child_id")

        if not where_conditions:
            raise SecurityError("DELETE queries must have WHERE conditions")

        # Build WHERE clause
        where_clause, params = self._build_where_clause(where_conditions)

        query_text = f"DELETE FROM {table_name} WHERE {where_clause}"
        query = text(query_text)

        self._log_query_build("DELETE", table_name, params)

        return query, params

    def _build_where_clause(
        self, conditions: dict[str, Any], param_prefix: str = ""
    ) -> tuple[str, dict[str, Any]]:
        """Build safe parameterized WHERE clause."""
        clauses = []
        params = {}

        for key, value in conditions.items():
            if not self._validate_column_name(key):
                raise SecurityError(f"Invalid column name in WHERE: {key}")

            if not self.protection.validate_input(value):
                raise SecurityError(f"Invalid value in WHERE clause for {key}")

            param_name = f"{param_prefix}{key}"
            clauses.append(f"{key} = :{param_name}")
            params[param_name] = value

        return " AND ".join(clauses), params

    def _validate_column_name(self, column_name: str) -> bool:
        """Validate column name format."""
        if not column_name:
            return False

        # Allow only alphanumeric characters, underscores, and dots
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_.]*$", column_name):
            return False

        # Check for SQL reserved words
        sql_reserved = {
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
            "ORDER",
            "GROUP",
            "HAVING",
            "LIMIT",
            "OFFSET",
        }

        if column_name.upper() in sql_reserved:
            return False

        return True

    def _log_query_build(self, operation: str, table: str, params: dict[str, Any]):
        """Log query building for audit trail."""
        audit_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "table": table,
            "param_count": len(params),
            "param_keys": list(params.keys()),
        }

        self.audit_trail.append(audit_entry)

        # Keep only last 1000 entries
        if len(self.audit_trail) > 1000:
            self.audit_trail = self.audit_trail[-1000:]

        logger.info(
            f"Secure query built: {operation} on {table} with {len(params)} parameters"
        )


class SecurityError(Exception):
    """Custom exception for security validation failures."""


# Global instances
_enhanced_protection = None
_secure_query_helper = None


def get_enhanced_sql_protection() -> EnhancedSQLProtection:
    """Get enhanced SQL protection singleton."""
    global _enhanced_protection
    if _enhanced_protection is None:
        _enhanced_protection = EnhancedSQLProtection()
    return _enhanced_protection


def get_secure_query_helper() -> SecureQueryHelper:
    """Get secure query helper singleton."""
    global _secure_query_helper
    if _secure_query_helper is None:
        _secure_query_helper = SecureQueryHelper()
    return _secure_query_helper
