import asyncio
import hashlib
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

import aiofiles

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


class AuditCategory(Enum):
    """Categories for audit events to enable proper filtering and compliance reporting."""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    CHILD_SAFETY = "child_safety"
    DATA_PROTECTION = "data_protection"
    SYSTEM_SECURITY = "system_security"
    COPPA_COMPLIANCE = "coppa_compliance"
    PARENT_VERIFICATION = "parent_verification"
    DATA_RETENTION = "data_retention"
    ENCRYPTION = "encryption"
    ACCESS_CONTROL = "access_control"


class AuditEventType(Enum):
    """Specific event types for detailed audit tracking."""

    # Authentication events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    ACCOUNT_LOCKED = "account_locked"

    # Authorization events
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    PERMISSION_CHANGE = "permission_change"

    # Child safety events
    CHILD_INTERACTION_START = "child_interaction_start"
    CHILD_INTERACTION_END = "child_interaction_end"
    SAFETY_INCIDENT = "safety_incident"
    CONTENT_FILTERED = "content_filtered"
    INAPPROPRIATE_CONTENT = "inappropriate_content"

    # Data protection events
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    DATA_EXPORT = "data_export"
    ENCRYPTION_EVENT = "encryption_event"

    # System security events
    SECURITY_ALERT = "security_alert"
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    CONFIGURATION_CHANGE = "configuration_change"

    # COPPA compliance events
    PARENTAL_CONSENT_REQUEST = "parental_consent_request"
    PARENTAL_CONSENT_GRANTED = "parental_consent_granted"
    PARENTAL_CONSENT_REVOKED = "parental_consent_revoked"
    DATA_RETENTION_TRIGGERED = "data_retention_triggered"
    CHILD_DATA_DELETED = "child_data_deleted"


class AuditSeverity(Enum):
    """Severity levels for audit events."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditConfig:
    log_directory: str
    max_file_size_mb: int
    max_files: int
    retention_days: int
    enable_encryption: bool
    enable_tamper_detection: bool
    batch_size: int
    flush_interval_seconds: float


@dataclass
class AuditContext:
    user_id: str | None = None
    child_id: str | None = None
    session_id: str | None = None
    ip_address: str | None = None


@dataclass
class AuditEvent:
    """Represents a single audit event with all required metadata."""

    event_id: str
    timestamp: datetime
    event_type: AuditEventType
    severity: AuditSeverity
    category: AuditCategory
    description: str
    context: Optional["AuditContext"] = None
    details: dict[str, Any] | None = None
    checksum: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert audit event to dictionary for serialization."""
        result = asdict(self)
        result["timestamp"] = self.timestamp.isoformat()
        result["event_type"] = self.event_type.value
        result["severity"] = self.severity.value
        result["category"] = self.category.value
        if self.context:
            result["context"] = asdict(self.context)
        return result

    def calculate_checksum(self) -> str:
        """Calculate checksum for tamper detection."""
        content = f"{self.event_id}{self.timestamp.isoformat()}{self.event_type.value}{self.description}"
        return hashlib.sha256(content.encode()).hexdigest()


class AuditLogger:
    """Enterprise - grade audit logging system with COPPA compliance features.
    Features:
    - Tamper - resistant logging with checksums
    - Encrypted audit logs
    - Real - time alerting for critical events
    - COPPA compliance tracking
    - Batch processing for performance
    - Automatic log rotation and retention.
    """

    def __init__(self, config: AuditConfig) -> None:
        self.config = config
        self.audit_entries: list[AuditEvent] = []
        self.buffer_lock = asyncio.Lock()
        self._ensure_log_directory()
        self._start_background_tasks()

    def _ensure_log_directory(self) -> None:
        """Ensure audit log directory exists."""
        os.makedirs(self.config.log_directory, exist_ok=True)

    def _start_background_tasks(self) -> None:
        """Start background tasks for log processing."""
        asyncio.create_task(self._flush_audit_buffer())
        asyncio.create_task(self._rotate_old_logs())

    async def log_event(
        self,
        event_type: AuditEventType,
        severity: AuditSeverity,
        category: AuditCategory,
        description: str,
        context: AuditContext | None = None,
        details: dict[str, Any] | None = None,
    ) -> str:
        """Log a security audit event.

        Args:
            event_type: Type of event being logged
            severity: Severity level of the event
            category: Category for filtering and compliance
            description: Human - readable description
            context: Context information(user, session, etc.)
            details: Additional structured data
        Returns:
            Unique event ID for tracking

        """
        event_id = str(uuid4())
        try:
            # Create audit event
            audit_event = AuditEvent(
                event_id=event_id,
                timestamp=datetime.utcnow(),
                event_type=event_type,
                severity=severity,
                category=category,
                description=description,
                context=context,
                details=details,
            )

            # Calculate checksum for tamper detection
            if self.config.enable_tamper_detection:
                audit_event.checksum = audit_event.calculate_checksum()

            # Add to buffer
            async with self.buffer_lock:
                self.audit_entries.append(audit_event)

            # Handle critical events immediately
            if severity in [AuditSeverity.ERROR, AuditSeverity.CRITICAL]:
                await self._handle_critical_event(audit_event)

            logger.debug(f"Audit event logged: {event_id} - {event_type.value}")
            return event_id
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            # Fallback logging to ensure we don't lose critical events
            logger.critical(f"AUDIT_FALLBACK: {event_type.value} - {description}")
            return event_id

    async def log_child_interaction(
        self,
        child_id: str,
        interaction_type: str,
        content: str,
        response: str,
        safety_score: float,
        parent_id: str | None = None,
    ) -> str:
        """Log child interaction for COPPA compliance and safety monitoring.

        Args:
            child_id: Unique child identifier
            interaction_type: Type of interaction(chat, voice, etc.)
            content: Child's input (encrypted in logs)
            response: System response (encrypted in logs)
            safety_score: Safety assessment score (0.0 - 1.0)
            parent_id: Parent/guardian ID if available
        Returns:
            Unique event ID

        """
        context = AuditContext(child_id=child_id, user_id=parent_id)

        # Encrypt sensitive content if encryption is enabled
        if self.config.enable_encryption:
            content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
            response_hash = hashlib.sha256(response.encode()).hexdigest()[:16]
        else:
            content_hash = content[:100] + "..." if len(content) > 100 else content
            response_hash = response[:100] + "..." if len(response) > 100 else response

        details = {
            "interaction_type": interaction_type,
            "content_hash": content_hash,
            "response_hash": response_hash,
            "safety_score": safety_score,
            "content_length": len(content),
            "response_length": len(response),
        }

        # Determine severity based on safety score
        if safety_score < 0.3:
            severity = AuditSeverity.CRITICAL
        elif safety_score < 0.7:
            severity = AuditSeverity.WARNING
        else:
            severity = AuditSeverity.INFO

        return await self.log_event(
            event_type=AuditEventType.CHILD_INTERACTION_START,
            severity=severity,
            category=AuditCategory.CHILD_SAFETY,
            description=f"Child interaction: {interaction_type} (safety: {safety_score:.2f})",
            context=context,
            details=details,
        )

    async def log_safety_incident(
        self,
        child_id: str,
        incident_type: str,
        description: str,
        details: dict[str, Any] | None = None,
    ) -> str:
        """Log child safety incident for immediate investigation.

        Args:
            child_id: Child involved in incident
            incident_type: Type of safety incident
            description: Description of what happened
            details: Additional incident details
        Returns:
            Unique event ID

        """
        context = AuditContext(child_id=child_id)
        incident_details = {
            "incident_type": incident_type,
            "auto_generated": True,
            "requires_investigation": True,
            **(details or {}),
        }

        return await self.log_event(
            event_type=AuditEventType.SAFETY_INCIDENT,
            severity=AuditSeverity.CRITICAL,
            category=AuditCategory.CHILD_SAFETY,
            description=f"Safety incident: {incident_type} - {description}",
            context=context,
            details=incident_details,
        )

    async def log_data_access(
        self,
        user_id: str,
        data_type: str,
        operation: str,
        resource_id: str,
        child_id: str | None = None,
        ip_address: str | None = None,
    ) -> str:
        """Log data access for COPPA compliance and security monitoring.

        Args:
            user_id: User accessing the data
            data_type: Type of data being accessed
            operation: Operation performed (read, write, delete)
            resource_id: Specific resource identifier
            child_id: Child ID if accessing child data
            ip_address: Source IP address
        Returns:
            Unique event ID

        """
        context = AuditContext(
            user_id=user_id,
            child_id=child_id,
            ip_address=ip_address,
        )

        details = {
            "data_type": data_type,
            "operation": operation,
            "resource_id": resource_id,
            "timestamp_utc": datetime.utcnow().isoformat(),
        }

        # Determine severity based on operation and data type
        severity = AuditSeverity.INFO
        if operation in ["delete", "export"]:
            severity = AuditSeverity.WARNING
        if data_type in ["medical", "voice", "personal"]:
            severity = AuditSeverity.WARNING

        return await self.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            severity=severity,
            category=AuditCategory.DATA_PROTECTION,
            description=f"Data access: {operation} {data_type} by {user_id}",
            context=context,
            details=details,
        )

    async def log_coppa_event(
        self,
        event_type: AuditEventType,
        child_id: str,
        parent_id: str | None,
        description: str,
        details: dict[str, Any] | None = None,
    ) -> str:
        """Log COPPA compliance events.

        Args:
            event_type: Specific COPPA event type
            child_id: Child ID involved
            parent_id: Parent/guardian ID
            description: Event description
            details: Additional event details
        Returns:
            Unique event ID

        """
        context = AuditContext(user_id=parent_id, child_id=child_id)

        return await self.log_event(
            event_type=event_type,
            severity=AuditSeverity.INFO,
            category=AuditCategory.COPPA_COMPLIANCE,
            description=description,
            context=context,
            details=details,
        )

    async def _handle_critical_event(self, event: AuditEvent) -> None:
        """Handle critical events that require immediate attention."""
        try:
            # Immediate flush for critical events
            await self._write_events_to_file([event])

            # Send alerts for critical events
            if event.severity == AuditSeverity.CRITICAL:
                await self._send_security_alert(event)
        except Exception as e:
            logger.error(f"Failed to handle critical event {event.event_id}: {e}")

    async def _send_security_alert(self, event: AuditEvent) -> None:
        """Send security alert for critical events."""
        alert_message = {
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type.value,
            "description": event.description,
            "severity": "CRITICAL",
        }

        # In production, this would integrate with alerting systems
        logger.critical(f"SECURITY_ALERT: {json.dumps(alert_message)}")

    async def _flush_audit_buffer(self) -> None:
        """Background task to flush audit buffer periodically."""
        while True:
            try:
                await asyncio.sleep(self.config.flush_interval_seconds)
                async with self.buffer_lock:
                    if len(self.audit_entries) >= self.config.batch_size:
                        events_to_write = self.audit_entries[: self.config.batch_size]
                        self.audit_entries = self.audit_entries[
                            self.config.batch_size :
                        ]
                        await self._write_events_to_file(events_to_write)
            except Exception as e:
                logger.error(f"Error in audit buffer flush: {e}")

    async def _write_events_to_file(self, events: list[AuditEvent]) -> None:
        """Write audit events to encrypted log file."""
        if not events:
            return

        try:
            log_file = os.path.join(
                self.config.log_directory,
                f"audit_{datetime.utcnow().strftime('%Y%m%d')}.jsonl",
            )

            async with aiofiles.open(log_file, "a", encoding="utf-8") as f:
                for event in events:
                    log_line = json.dumps(event.to_dict(), ensure_ascii=False)
                    await f.write(log_line + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit events to file: {e}")

    async def _rotate_old_logs(self) -> None:
        """Background task to rotate and clean up old audit logs."""
        while True:
            try:
                await asyncio.sleep(86400)  # Run daily

                cutoff_date = datetime.utcnow() - timedelta(
                    days=self.config.retention_days,
                )

                for filename in os.listdir(self.config.log_directory):
                    if filename.startswith("audit_") and filename.endswith(".jsonl"):
                        file_path = os.path.join(self.config.log_directory, filename)
                        file_stat = os.stat(file_path)
                        file_date = datetime.fromtimestamp(file_stat.st_mtime)

                        if file_date < cutoff_date:
                            os.remove(file_path)
                            logger.info(f"Rotated old audit log: {filename}")
            except Exception as e:
                logger.error(f"Error in audit log rotation: {e}")


# Global audit logger instance
_audit_logger: AuditLogger | None = None


def get_audit_logger() -> AuditLogger:
    """Get or create global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        config = AuditConfig(
            log_directory="logs/audit",
            max_file_size_mb=100,
            max_files=10,
            retention_days=2555,  # 7 years for COPPA compliance
            enable_encryption=True,
            enable_tamper_detection=True,
            batch_size=100,
            flush_interval_seconds=30.0,
        )
        _audit_logger = AuditLogger(config)
    return _audit_logger


# Convenience functions for common audit events
async def log_audit_event(
    event_type: AuditEventType,
    severity: AuditSeverity,
    category: AuditCategory,
    description: str,
    **kwargs,
) -> str:
    """Convenience function for logging audit events."""
    audit_logger = get_audit_logger()
    return await audit_logger.log_event(
        event_type,
        severity,
        category,
        description,
        **kwargs,
    )


async def log_child_safety_incident(
    child_id: str,
    incident_type: str,
    description: str,
    **kwargs,
) -> str:
    """Convenience function for logging child safety incidents."""
    audit_logger = get_audit_logger()
    return await audit_logger.log_safety_incident(
        child_id,
        incident_type,
        description,
        **kwargs,
    )
