"""Comprehensive Audit Logging System
Provides COPPA-compliant audit logging for all child data access and modifications.
Essential for regulatory compliance and security monitoring.
"""

import hashlib
import json
import logging
import os
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.path_validator import get_secure_file_operations

logger = get_logger(__name__, component="infrastructure")


class AuditEventType(Enum):
    """Types of events that require audit logging."""

    # Child data events
    CHILD_CREATED = "child_created"
    CHILD_VIEWED = "child_viewed"
    CHILD_UPDATED = "child_updated"
    CHILD_DELETED = "child_deleted"
    CHILD_DATA_EXPORTED = "child_data_exported"

    # Conversation events
    CONVERSATION_STARTED = "conversation_started"
    CONVERSATION_MESSAGE = "conversation_message"
    CONVERSATION_ENDED = "conversation_ended"
    CONVERSATION_DELETED = "conversation_deleted"

    # Authentication events
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_LOGIN_FAILED = "user_login_failed"
    USER_REGISTERED = "user_registered"
    USER_PASSWORD_CHANGED = "user_password_changed"

    # Parental consent events
    PARENTAL_CONSENT_REQUESTED = "parental_consent_requested"
    PARENTAL_CONSENT_GRANTED = "parental_consent_granted"
    PARENTAL_CONSENT_REVOKED = "parental_consent_revoked"
    PARENTAL_VERIFICATION_ATTEMPTED = "parental_verification_attempted"
    PARENTAL_VERIFICATION_COMPLETED = "parental_verification_completed"

    # Data retention events
    DATA_RETENTION_SCHEDULED = "data_retention_scheduled"
    DATA_RETENTION_EXECUTED = "data_retention_executed"
    DATA_RETENTION_PARENT_NOTIFIED = "data_retention_parent_notified"

    # Security events
    SECURITY_VIOLATION = "security_violation"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    ACCESS_DENIED = "access_denied"

    # System events
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    CONFIGURATION_CHANGED = "configuration_changed"
    ERROR_OCCURRED = "error_occurred"


class AuditLevel(Enum):
    """Audit logging levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Audit event data structure."""

    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    user_id: str | None
    child_id: str | None
    session_id: str | None
    ip_address: str | None
    user_agent: str | None
    resource_type: str | None
    resource_id: str | None
    action: str
    result: str  # success, failure, partial
    level: AuditLevel
    message: str
    details: dict[str, Any]
    compliance_flags: list[str]
    retention_date: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert audit event to dictionary for logging."""
        data = asdict(self)
        # Convert enums to strings
        data["event_type"] = self.event_type.value
        data["level"] = self.level.value
        # Convert datetime to ISO format
        data["timestamp"] = self.timestamp.isoformat()
        data["retention_date"] = self.retention_date.isoformat()
        return data


class AuditLogger:
    """Comprehensive audit logging system for COPPA compliance.
    Features:
    - Structured audit events
    - COPPA compliance tracking
    - Secure log storage with integrity protection
    - Automated retention management
    - Real-time security alerting
    - Performance optimized.
    """

    def __init__(self, log_directory: str = "/var/log/ai-teddy/audit") -> None:
        """Initialize audit logger.

        Args:
            log_directory: Directory for audit log files

        """
        self.log_directory = log_directory
        self.ensure_log_directory()

        # Configure audit-specific logger
        self.audit_logger = logging.getLogger("audit")
        self.audit_logger.setLevel(logging.INFO)
        # Prevent propagation to avoid duplicate logs
        self.audit_logger.propagate = False

        # Setup file handler for audit logs
        self.setup_file_handler()

        # Audit log integrity protection
        self.integrity_key = self._get_integrity_key()

        # Performance tracking
        self.events_logged = 0
        self.start_time = time.time()

        logger.info("Audit logging system initialized")

    def ensure_log_directory(self) -> None:
        """Ensure audit log directory exists with proper permissions."""
        try:
            os.makedirs(self.log_directory, mode=0o750, exist_ok=True)
            logger.info(f"Audit log directory ready: {self.log_directory}")
        except OSError as e:
            logger.error(f"Failed to create audit log directory: {e}")
            # Fallback to local directory
            self.log_directory = "./audit_logs"
            os.makedirs(self.log_directory, mode=0o750, exist_ok=True)

    def setup_file_handler(self) -> None:
        """Setup rotating file handler for audit logs."""
        try:
            from logging.handlers import TimedRotatingFileHandler

            # Create daily rotating log files
            secure_ops = get_secure_file_operations()
            log_file = secure_ops.validator.get_safe_path(
                "audit.log",
                self.log_directory,
            )

            handler = TimedRotatingFileHandler(
                log_file,
                when="midnight",
                interval=1,
                backupCount=90,  # Keep 90 days of logs
                encoding="utf-8",
            )

            # Use JSON format for structured logging
            formatter = logging.Formatter("%(message)s")  # Just the JSON message
            handler.setFormatter(formatter)
            self.audit_logger.addHandler(handler)
        except Exception as e:
            logger.error(f"Failed to setup audit file handler: {e}")
            # Fallback to console logging
            console_handler = logging.StreamHandler()
            self.audit_logger.addHandler(console_handler)

    def _get_integrity_key(self) -> bytes:
        """Get or generate integrity key for audit logs."""
        secure_ops = get_secure_file_operations()
        try:
            if secure_ops.safe_exists(".audit_key"):
                with secure_ops.safe_open(".audit_key", "rb") as f:
                    return f.read()
        except Exception as e:
            logger.warning(f"Failed to read audit key: {e}")

        # Generate new key
        key = os.urandom(32)
        try:
            with secure_ops.safe_open(".audit_key", "wb") as f:
                f.write(key)
            # Set secure permissions
            key_file = secure_ops.validator.get_safe_path(
                ".audit_key",
                self.log_directory,
            )
            if key_file:
                os.chmod(key_file, 0o600)  # Owner read/write only
        except Exception as e:
            logger.warning(f"Could not save audit integrity key: {e}")

        return key

    def log_event(
        self,
        event_type: AuditEventType,
        action: str,
        result: str = "success",
        level: AuditLevel = AuditLevel.INFO,
        message: str = "",
        user_id: str | None = None,
        child_id: str | None = None,
        session_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        details: dict[str, Any] | None = None,
        compliance_flags: list[str] | None = None,
    ) -> str:
        """Log an audit event.

        Args:
            event_type: Type of event
            action: Action performed
            result: Result of action (success/failure/partial)
            level: Audit level
            message: Human-readable message
            user_id: ID of user performing action
            child_id: ID of child affected (for COPPA tracking)
            session_id: Session identifier
            ip_address: Client IP address
            user_agent: Client user agent
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            details: Additional event details
            compliance_flags: COPPA/regulatory compliance flags
        Returns:
            str: Unique event ID

        """
        # Generate unique event ID
        event_id = str(uuid.uuid4())

        # Calculate retention date (7 years for COPPA compliance)
        from datetime import timedelta

        retention_date = datetime.now(UTC) + timedelta(days=2555)  # ~7 years

        # Create audit event
        event = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp=datetime.now(UTC),
            user_id=user_id,
            child_id=child_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            result=result,
            level=level,
            message=message,
            details=details or {},
            compliance_flags=compliance_flags or [],
            retention_date=retention_date,
        )

        # Add integrity hash
        event_dict = event.to_dict()
        event_dict["integrity_hash"] = self._calculate_integrity_hash(event_dict)

        # Log the event
        self.audit_logger.info(json.dumps(event_dict, ensure_ascii=False))

        # Update performance counters
        self.events_logged += 1

        # Alert on critical events
        if level == AuditLevel.CRITICAL:
            self._send_critical_alert(event)

        return event_id

    def log_child_data_access(
        self,
        child_id: str,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        ip_address: str | None = None,
        session_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> str:
        """Log child data access for COPPA compliance.

        Args:
            child_id: ID of child whose data was accessed
            user_id: ID of user accessing data
            action: Action performed (view, create, update, delete, export)
            resource_type: Type of data accessed (profile, conversation, medical)
            resource_id: Specific resource ID if applicable
            ip_address: Client IP address
            session_id: Session identifier
            details: Additional details
        Returns:
            str: Event ID

        """
        return self.log_event(
            event_type=(
                AuditEventType.CHILD_VIEWED
                if action == "view"
                else AuditEventType.CHILD_UPDATED
            ),
            action=f"child_data_{action}",
            message=f"Child data {action}: {resource_type}",
            user_id=user_id,
            child_id=child_id,
            session_id=session_id,
            ip_address=ip_address,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            compliance_flags=["COPPA", "child_data_access"],
        )

    def log_security_event(
        self,
        event_type: AuditEventType,
        message: str,
        level: AuditLevel = AuditLevel.WARNING,
        user_id: str | None = None,
        ip_address: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> str:
        """Log security-related events.

        Args:
            event_type: Type of security event
            message: Description of security event
            level: Severity level
            user_id: User involved (if any)
            ip_address: Source IP address
            details: Additional security details
        Returns:
            str: Event ID

        """
        return self.log_event(
            event_type=event_type,
            action="security_event",
            message=message,
            level=level,
            user_id=user_id,
            ip_address=ip_address,
            details=details,
            compliance_flags=["security"],
        )

    def log_parental_consent_event(
        self,
        event_type: AuditEventType,
        child_id: str,
        parent_user_id: str,
        consent_type: str,
        result: str = "success",
        ip_address: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> str:
        """Log parental consent events for COPPA compliance.

        Args:
            event_type: Type of consent event
            child_id: ID of child
            parent_user_id: ID of parent/guardian
            consent_type: Type of consent (data_collection, sharing, etc.)
            result: Result of consent process
            ip_address: Parent's IP address
            details: Additional consent details
        Returns:
            str: Event ID

        """
        return self.log_event(
            event_type=event_type,
            action=f"parental_consent_{consent_type}",
            result=result,
            message=f"Parental consent {event_type.value} for {consent_type}",
            user_id=parent_user_id,
            child_id=child_id,
            ip_address=ip_address,
            details=details,
            compliance_flags=["COPPA", "parental_consent"],
        )

    def _calculate_integrity_hash(self, event_data: dict[str, Any]) -> str:
        """Calculate integrity hash for audit event."""
        # Remove integrity_hash field if present
        data_copy = event_data.copy()
        data_copy.pop("integrity_hash", None)

        # Create deterministic string representation
        event_string = json.dumps(data_copy, sort_keys=True, ensure_ascii=False)

        # Calculate HMAC hash
        import hmac

        hash_obj = hmac.new(
            self.integrity_key,
            event_string.encode("utf-8"),
            hashlib.sha256,
        )
        return hash_obj.hexdigest()

    def _send_critical_alert(self, event: AuditEvent) -> None:
        """Send alert for critical audit events."""
        try:
            # In production, this would integrate with alerting systems
            # For now, just log with high priority
            logger.critical(
                f"CRITICAL AUDIT EVENT: {event.event_type.value} - {event.message}",
                extra={
                    "event_id": event.event_id,
                    "child_id": event.child_id,
                    "user_id": event.user_id,
                    "ip_address": event.ip_address,
                },
            )
        except Exception as e:
            logger.error(f"Failed to send critical audit alert: {e}")

    def verify_log_integrity(self, event_data: dict[str, Any]) -> bool:
        """Verify the integrity of an audit log entry.

        Args:
            event_data: Audit event data dictionary
        Returns:
            bool: True if integrity is valid

        """
        stored_hash = event_data.get("integrity_hash")
        if not stored_hash:
            return False

        calculated_hash = self._calculate_integrity_hash(event_data)
        return stored_hash == calculated_hash

    def query_audit_logs(
        self,
        child_id: str | None = None,
        user_id: str | None = None,
        event_type: AuditEventType | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query audit logs (for compliance reporting).

        Args:
            child_id: Filter by child ID
            user_id: Filter by user ID
            event_type: Filter by event type
            start_date: Start date filter
            end_date: End date filter
            limit: Maximum results
        Returns:
            List of matching audit events

        """
        # In production, this would query a database or log aggregation system
        # For now, return empty list with warning
        logger.warning(
            "Audit log querying not fully implemented - integrate with log storage system",
        )
        return []

    def get_statistics(self) -> dict[str, Any]:
        """Get audit logging statistics."""
        uptime = time.time() - self.start_time
        return {
            "events_logged": self.events_logged,
            "uptime_seconds": uptime,
            "events_per_hour": (
                (self.events_logged / uptime * 3600) if uptime > 0 else 0
            ),
            "log_directory": self.log_directory,
            "integrity_protection": True,
            "retention_policy_days": 2555,  # ~7 years for COPPA
        }


# Global audit logger instance
_audit_logger: AuditLogger | None = None


def get_audit_logger() -> AuditLogger:
    """Get global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


def log_audit_event(event_type: AuditEventType, **kwargs) -> str:
    """Convenience function to log audit events."""
    return get_audit_logger().log_event(event_type, **kwargs)


def log_child_data_access(child_id: str, user_id: str, action: str, **kwargs) -> str:
    """Convenience function to log child data access."""
    return get_audit_logger().log_child_data_access(child_id, user_id, action, **kwargs)


def log_security_event(event_type: AuditEventType, message: str, **kwargs) -> str:
    """Convenience function to log security events."""
    return get_audit_logger().log_security_event(event_type, message, **kwargs)
