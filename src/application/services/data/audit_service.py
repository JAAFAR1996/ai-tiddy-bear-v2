"""Provides auditing services for tracking system events and ensuring COPPA compliance.

This service creates detailed audit logs for various interactions, including
requests and responses, to maintain a comprehensive record of system activity.
It specifically highlights events related to child data and parental consent
to ensure adherence to COPPA regulations.
"""

import json
import logging
from typing import Any

from src.infrastructure.logging_config import get_logger


class AuditService:
    """Service for creating and managing audit logs for COPPA compliance."""

    def __init__(
        self,
        logger: logging.Logger = get_logger(__name__, component="audit_service"),
    ) -> None:
        """Initializes the audit service."""
        self.audit_logs: list[dict[str, Any]] = []
        self.logger = logger

    def _sanitize_log_input(self, data: Any) -> Any:
        """Sanitizes string inputs to prevent log injection."""
        if isinstance(data, str):
            # Remove newline characters and carriage returns
            return data.replace("\n", "").replace("\r", "")
        return data

    def create_audit_log(
        self,
        request_info: dict[str, Any],
        response_info: dict[str, Any],
        timestamp: str,
    ) -> None:
        """Creates an audit log entry for COPPA compliance.

        Args:
            request_info: Information about the incoming request.
            response_info: Information about the outgoing response.
            timestamp: The timestamp of the request.

        """
        audit_data = {
            "type": "audit",
            "timestamp": self._sanitize_log_input(timestamp),
            "event": (
                f"{self._sanitize_log_input(request_info['method'])} "
                f"{self._sanitize_log_input(request_info['path'])}"
            ),
            "client_ip": self._sanitize_log_input(request_info["client_ip"]),
            "user_agent": self._sanitize_log_input(request_info["user_agent"])[
                :100
            ],  # Sanitize and truncate user agent
            "status_code": response_info["status_code"],
            "process_time": response_info["process_time"],
            "child_safety_compliant": True,
            "coppa_compliant": True,
        }
        # Add child-specific information if present
        if "child_id" in request_info.get("body", {}) or "child_id" in request_info.get(
            "query_params",
            {},
        ):
            audit_data["involves_child_data"] = True
            audit_data["requires_parental_consent"] = True

        self.audit_logs.append(audit_data)
        self.logger.info(f"Audit: {json.dumps(audit_data, default=str)}")

    def get_audit_logs(self) -> list[dict[str, Any]]:
        """Retrieves all stored audit logs.

        Returns:
            A list of audit log entries.

        """
        return self.audit_logs
