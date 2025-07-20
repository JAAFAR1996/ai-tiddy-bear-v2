from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.audit.audit_logger import (
    AuditCategory,
    AuditContext,
    AuditEventType,
    AuditSeverity,
    get_audit_logger,
)

logger = get_logger(__name__, component="security")


@dataclass
class AuditableOperation:
    """Represents an operation that should be audited."""

    operation_type: str
    user_id: str | None
    child_id: str | None
    resource_id: str | None
    ip_address: str | None
    details: dict[str, Any] | None = None


class ComprehensiveAuditIntegration:
    """Comprehensive audit integration service that ensures all critical operations are logged.
    This service fixes audit trail gaps by providing centralized methods for logging:
    - Authentication events(login, logout, failures)
    - Authorization events(access granted / denied, permission changes)
    - Child data operations(creation, modification, deletion, access)
    - COPPA compliance events(consent, age verification, data retention)
    - Security events(threats, policy violations, configuration changes)
    """

    def __init__(self):
        self.audit_logger = get_audit_logger()

    async def log_authentication_event(
        self,
        event_type: str,
        user_email: str,
        success: bool,
        ip_address: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> str:
        """Log authentication events with comprehensive details."""
        sanitized_email = self._sanitize_email(user_email)

        event_mapping = {
            "login": (
                AuditEventType.LOGIN_SUCCESS
                if success
                else AuditEventType.LOGIN_FAILURE
            ),
            "logout": AuditEventType.LOGOUT,
            "password_change": AuditEventType.PASSWORD_CHANGE,
            "account_locked": AuditEventType.ACCOUNT_LOCKED,
        }

        audit_event_type = event_mapping.get(event_type, AuditEventType.LOGIN_FAILURE)
        severity = AuditSeverity.INFO if success else AuditSeverity.WARNING

        if event_type == "account_locked":
            severity = AuditSeverity.ERROR

        context = AuditContext(user_id=sanitized_email, ip_address=ip_address)

        audit_details = {
            "user_email": sanitized_email,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
            **(details or {}),
        }

        return await self.audit_logger.log_event(
            event_type=audit_event_type,
            severity=severity,
            category=AuditCategory.AUTHENTICATION,
            description=f"Authentication {event_type}: {sanitized_email} ({'success' if success else 'failed'})",
            context=context,
            details=audit_details,
        )

    async def log_authorization_event(
        self,
        user_id: str,
        resource: str,
        action: str,
        granted: bool,
        child_id: str | None = None,
        ip_address: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> str:
        """Log authorization events (access control decisions)."""
        event_type = (
            AuditEventType.ACCESS_GRANTED if granted else AuditEventType.ACCESS_DENIED
        )
        severity = AuditSeverity.INFO if granted else AuditSeverity.WARNING

        context = AuditContext(
            user_id=user_id, child_id=child_id, ip_address=ip_address
        )

        audit_details = {
            "resource": resource,
            "action": action,
            "granted": granted,
            "timestamp": datetime.utcnow().isoformat(),
            **(details or {}),
        }

        return await self.audit_logger.log_event(
            event_type=event_type,
            severity=severity,
            category=AuditCategory.AUTHORIZATION,
            description=f"Access {action} on {resource}: {'granted' if granted else 'denied'} for user {user_id}",
            context=context,
            details=audit_details,
        )

    async def log_child_data_operation(
        self,
        operation: str,
        child_id: str,
        user_id: str,
        data_type: str,
        ip_address: str | None = None,
        details: dict[str, Any] | None = None,
        operation_id: str | None = None,
        success: bool | None = None,
    ) -> str:
        """Log child data operations for COPPA compliance."""
        sanitized_child_id = self._sanitize_child_id(child_id)

        operation_mapping = {
            "create": AuditEventType.DATA_MODIFICATION,
            "read": AuditEventType.DATA_ACCESS,
            "update": AuditEventType.DATA_MODIFICATION,
            "delete": AuditEventType.DATA_DELETION,
        }
        if operation not in operation_mapping:
            raise ValueError(f"Unknown operation: {operation}")
        event_type = operation_mapping[operation]

        sensitive_types = {"medical", "voice", "personal"}
        severity = AuditSeverity.INFO
        if operation == "delete" and data_type in sensitive_types:
            severity = AuditSeverity.CRITICAL
        elif operation == "delete" or data_type in sensitive_types:
            severity = AuditSeverity.WARNING

        context = AuditContext(
            user_id=user_id, child_id=sanitized_child_id, ip_address=ip_address
        )

        core_audit_fields = {
            "operation": operation,
            "data_type": data_type,
            "child_id": sanitized_child_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if operation_id:
            core_audit_fields["operation_id"] = operation_id
        if success is not None:
            core_audit_fields["success"] = success

        safe_details = {
            k: v for k, v in (details or {}).items() if k not in core_audit_fields
        }
        audit_details = {**core_audit_fields, **safe_details}

        return await self.audit_logger.log_event(
            event_type=event_type,
            severity=severity,
            category=AuditCategory.DATA_PROTECTION,
            description=f"Child data {operation}: {data_type} for child {sanitized_child_id} by user {user_id}",
            context=context,
            details=audit_details,
        )

    async def log_coppa_compliance_event(
        self,
        event_type: str,
        child_id: str,
        parent_id: str | None,
        description: str,
        details: dict[str, Any] | None = None,
    ) -> str:
        from ..config.coppa_config import requires_coppa_audit_logging

        if not requires_coppa_audit_logging():
            return f"coppa_disabled_{event_type}_{int(datetime.utcnow().timestamp())}"

        sanitized_child_id = self._sanitize_child_id(child_id)

        coppa_event_mapping = {
            "consent_requested": AuditEventType.PARENTAL_CONSENT_REQUEST,
            "consent_granted": AuditEventType.PARENTAL_CONSENT_GRANTED,
            "consent_revoked": AuditEventType.PARENTAL_CONSENT_REVOKED,
            "data_retention_triggered": AuditEventType.DATA_RETENTION_TRIGGERED,
            "data_deleted": AuditEventType.CHILD_DATA_DELETED,
        }

        audit_event_type = coppa_event_mapping.get(
            event_type, AuditEventType.PARENTAL_CONSENT_REQUEST
        )

        context = AuditContext(user_id=parent_id, child_id=sanitized_child_id)

        audit_details = {
            "event_type": event_type,
            "child_id": sanitized_child_id,
            "parent_id": parent_id,
            "timestamp": datetime.utcnow().isoformat(),
            **(details or {}),
        }

        return await self.audit_logger.log_event(
            event_type=audit_event_type,
            severity=AuditSeverity.INFO,
            category=AuditCategory.COPPA_COMPLIANCE,
            description=description,
            context=context,
            details=audit_details,
        )

    async def log_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        user_id: str | None = None,
        ip_address: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> str:
        severity_mapping = {
            "debug": AuditSeverity.DEBUG,
            "info": AuditSeverity.INFO,
            "warning": AuditSeverity.WARNING,
            "error": AuditSeverity.ERROR,
            "critical": AuditSeverity.CRITICAL,
        }

        audit_severity = severity_mapping.get(severity.lower(), AuditSeverity.INFO)

        context = AuditContext(user_id=user_id, ip_address=ip_address)

        audit_details = {
            "event_type": event_type,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
            **(details or {}),
        }

        return await self.audit_logger.log_event(
            event_type=AuditEventType.SECURITY_ALERT,
            severity=audit_severity,
            category=AuditCategory.SYSTEM_SECURITY,
            description=description,
            context=context,
            details=audit_details,
        )

    async def log_system_event(
        self,
        event_type: str,
        description: str,
        details: dict[str, Any] | None = None,
    ) -> str:
        system_event_mapping = {
            "startup": AuditEventType.SYSTEM_STARTUP,
            "shutdown": AuditEventType.SYSTEM_SHUTDOWN,
            "config_change": AuditEventType.CONFIGURATION_CHANGE,
        }

        audit_event_type = system_event_mapping.get(
            event_type, AuditEventType.SYSTEM_STARTUP
        )

        audit_details = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            **(details or {}),
        }

        return await self.audit_logger.log_event(
            event_type=audit_event_type,
            severity=AuditSeverity.INFO,
            category=AuditCategory.SYSTEM_SECURITY,
            description=description,
            details=audit_details,
        )

    def _sanitize_email(self, email: str) -> str:
        try:
            parts = email.split("@")
            if len(parts) == 2:
                return f"{parts[0][:2]}***@{parts[1]}"
            return "***@***"
        except (AttributeError, IndexError, TypeError):
            return "***@***"

    def _sanitize_child_id(self, child_id: str) -> str:
        try:
            if len(child_id) > 8:
                return f"{child_id[:4]}***{child_id[-4:]}"
            return f"{child_id[:2]}***"
        except (AttributeError, TypeError):
            return "***"


# Global audit integration instance
_audit_integration: ComprehensiveAuditIntegration | None = None


def get_audit_integration() -> ComprehensiveAuditIntegration:
    global _audit_integration
    if _audit_integration is None:
        _audit_integration = ComprehensiveAuditIntegration()
    return _audit_integration


async def audit_authentication(
    event_type: str, user_email: str, success: bool, **kwargs
) -> str:
    integration = get_audit_integration()
    return await integration.log_authentication_event(
        event_type, user_email, success, **kwargs
    )


async def audit_authorization(
    user_id: str, resource: str, action: str, granted: bool, **kwargs
) -> str:
    integration = get_audit_integration()
    return await integration.log_authorization_event(
        user_id, resource, action, granted, **kwargs
    )


async def audit_child_data_operation(
    operation: str, child_id: str, user_id: str, data_type: str, **kwargs
) -> str:
    integration = get_audit_integration()
    return await integration.log_child_data_operation(
        operation, child_id, user_id, data_type, **kwargs
    )


async def audit_coppa_event(
    event_type: str,
    child_id: str,
    parent_id: str | None,
    description: str,
    **kwargs,
) -> str:
    integration = get_audit_integration()
    return await integration.log_coppa_compliance_event(
        event_type, child_id, parent_id, description, **kwargs
    )


async def audit_security_event(
    event_type: str, severity: str, description: str, **kwargs
) -> str:
    integration = get_audit_integration()
    return await integration.log_security_event(
        event_type, severity, description, **kwargs
    )
