from typing import Any

from src.infrastructure.logging_config import get_logger
from src.infrastructure.validators.security.path_validator import get_path_validator

logger = get_logger(__name__, component="security")


class RequestSecurityDetector:
    """Detects potential security threats within incoming requests."""

    def __init__(self):
        self.path_validator = get_path_validator()

    def detect_security_events(
        self,
        request_info: dict[str, Any],
        response_info: dict[str, Any],
    ) -> list[str]:
        """Detect and return a list of security events."""
        security_events = []

        # Detect potential attacks
        if response_info["status_code"] == 403:
            security_events.append("access_denied")
        if response_info["status_code"] == 429:
            security_events.append("rate_limit_exceeded")

        # Detect suspicious patterns in requests
        if self._detect_sql_injection_attempt(request_info):
            security_events.append("sql_injection_attempt")
        if self._detect_xss_attempt(request_info):
            security_events.append("xss_attempt")
        if self._detect_path_traversal_attempt(request_info):
            security_events.append("path_traversal_attempt")

        return security_events

    def _detect_sql_injection_attempt(self, request_info: dict[str, Any]) -> bool:
        """Detect potential SQL injection attempts."""
        sql_patterns = [
            "union select",
            "drop table",
            "insert into",
            "delete from",
            "--",
            "/*",
            "*/",
            "xp_",
            "sp_",
            "exec",
            "execute",
        ]

        # Check URL path and query parameters
        text_to_check = [
            request_info["path"].lower(),
            " ".join(
                str(v).lower() for v in request_info.get("query_params", {}).values()
            ),
        ]

        # Check request body if present
        if "body" in request_info and isinstance(request_info["body"], dict):
            text_to_check.append(
                " ".join(
                    str(v).lower()
                    for v in request_info["body"].values()
                    if isinstance(v, str)
                ),
            )

        for text in text_to_check:
            if any(pattern in text for pattern in sql_patterns):
                return True

        return False

    def _detect_xss_attempt(self, request_info: dict[str, Any]) -> bool:
        """Detect potential XSS attempts."""
        xss_patterns = [
            "<script",
            "javascript:",
            "onload=",
            "onerror=",
            "onclick=",
            "eval(",
            "alert(",
            "document.cookie",
            "window.location",
        ]

        # Check similar fields as SQL injection
        text_to_check = [
            request_info["path"].lower(),
            " ".join(
                str(v).lower() for v in request_info.get("query_params", {}).values()
            ),
        ]

        if "body" in request_info and isinstance(request_info["body"], dict):
            text_to_check.append(
                " ".join(
                    str(v).lower()
                    for v in request_info["body"].values()
                    if isinstance(v, str)
                ),
            )

        for text in text_to_check:
            if any(pattern in text for pattern in xss_patterns):
                return True

        return False

    def _detect_path_traversal_attempt(self, request_info: dict[str, Any]) -> bool:
        """Detect potential path traversal attempts."""
        path = request_info["path"]

        # Use comprehensive path validator for enhanced security
        is_safe = self.path_validator.validate_path(path, "read")

        # Also check query parameters for path traversal
        query_params = request_info.get("query_params", {})
        for param_value in query_params.values():
            if isinstance(param_value, str) and not self.path_validator.validate_path(
                param_value,
                "read",
            ):
                return True

        return not is_safe
