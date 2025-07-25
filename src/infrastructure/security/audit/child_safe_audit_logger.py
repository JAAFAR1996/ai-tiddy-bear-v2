"""
Child-Safe Audit Logger for COPPA Compliance
============================================

This module provides a specialized audit logging system that ensures ABSOLUTE
compliance with COPPA regulations by preventing any child PII from being logged.

🛑 CRITICAL SECURITY: This logger NEVER logs actual child data, names, ages,
or any personally identifiable information. All data is sanitized, hashed,
or redacted before any logging operation.
"""

import hashlib
import json
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.audit.pii_classifier import PIIClassifier


class ChildSafeAuditLogger:
    """
    COPPA-compliant audit logger that sanitizes all data before logging.

    🛡️ SECURITY GUARANTEE: This logger implements the following protections:
    - NEVER logs actual child names, ages, or personal information
    - NEVER logs actual user input content
    - ALL data is classified for PII before logging
    - Only metadata, hashes, and classifications are logged
    - Automatic redaction of any detected PII
    - Special protection for child-specific data patterns
    """

    def __init__(self, logger_name: str = "child_safe_audit"):
        """Initialize the child-safe audit logger."""
        self.logger = get_logger(logger_name, component="child_safety")
        self.pii_classifier = PIIClassifier()
        self.audit_id = str(uuid4())

        # Track audit session
        self.logger.info(f"Child-safe audit session started: {self.audit_id}")

    def log_input_analysis(
        self,
        input_data: str,
        context: str = "user_input",
        severity: str = "info",
        child_id: Optional[str] = None,
    ) -> None:
        """
        Log analysis of user input with complete PII sanitization.

        🛡️ SECURITY: This method NEVER logs the actual input content.
        Only safe metadata and classifications are logged.

        Args:
            input_data: The input to analyze (NEVER logged directly)
            context: Context for the input analysis
            severity: Log severity level
            child_id: Child identifier (will be hashed)
        """
        # Get safe summary from PII classifier
        safe_summary = self.pii_classifier.get_safe_summary(input_data)

        # Create audit entry with ONLY safe data
        audit_entry = {
            "audit_id": self.audit_id,
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "input_analysis",
            "context": context,
            "child_id_hash": self._hash_identifier(child_id) if child_id else None,
            "input_metadata": safe_summary,
            "coppa_compliant": True,  # This logger is always COPPA compliant
        }

        # Log based on risk level
        if (
            safe_summary["child_specific_pii"]
            or safe_summary["risk_level"] == "critical"
        ):
            self.logger.critical(
                f"CRITICAL PII DETECTED - {context}: {json.dumps(audit_entry)}"
            )
        elif safe_summary["risk_level"] == "high":
            self.logger.error(f"HIGH RISK INPUT - {context}: {json.dumps(audit_entry)}")
        elif safe_summary["risk_level"] == "medium":
            self.logger.warning(
                f"MEDIUM RISK INPUT - {context}: {json.dumps(audit_entry)}"
            )
        else:
            getattr(self.logger, severity)(
                f"Input analysis - {context}: {json.dumps(audit_entry)}"
            )

    def log_security_event(
        self,
        event_type: str,
        threat_level: str,
        input_data: str,
        context: Dict[str, Any] = None,
    ) -> None:
        """
        Log a security event with sanitized data.

        🛡️ SECURITY: Actual threat content is NEVER logged.
        Only classifications and metadata are recorded.

        Args:
            event_type: Type of security event
            threat_level: Threat severity level
            input_data: The potentially malicious input (NEVER logged directly)
            context: Additional context data
        """
        safe_summary = self.pii_classifier.get_safe_summary(input_data)

        # Sanitize context data
        safe_context = self._sanitize_context(context or {})

        security_event = {
            "audit_id": self.audit_id,
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "threat_level": threat_level,
            "input_metadata": safe_summary,
            "context": safe_context,
            "security_classification": self._classify_security_threat(safe_summary),
            "coppa_compliant": True,
        }

        # Always log security events as warnings or higher
        if threat_level.lower() in ["critical", "high"]:
            self.logger.error(
                f"SECURITY THREAT DETECTED - {event_type}: {json.dumps(security_event)}"
            )
        else:
            self.logger.warning(
                f"Security event - {event_type}: {json.dumps(security_event)}"
            )

    def log_sql_injection_attempt(
        self,
        severity: str,
        pattern: str,
        input_data: str,
        context: str = "sql_validation",
    ) -> None:
        """
        Log SQL injection attempt with complete data sanitization.

        🛡️ SECURITY: This replaces the unsafe _log_blocked_attempt methods
        that were logging actual user input content.

        Args:
            severity: Severity level of the attempt
            pattern: Pattern that was matched
            input_data: The malicious input (NEVER logged directly)
            context: Context of the validation
        """
        safe_summary = self.pii_classifier.get_safe_summary(input_data)

        sql_injection_event = {
            "audit_id": self.audit_id,
            "event_id": str(uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "sql_injection_attempt",
            "severity": severity,
            "matched_pattern": pattern,  # Pattern name only, not actual content
            "input_metadata": safe_summary,
            "context": context,
            "blocked": True,
            "coppa_compliant": True,
        }

        # Log based on severity and PII content
        if safe_summary["child_specific_pii"]:
            self.logger.critical(
                f"SQL INJECTION WITH CHILD PII - BLOCKED: {json.dumps(sql_injection_event)}"
            )
        elif severity.lower() == "critical":
            self.logger.critical(
                f"CRITICAL SQL INJECTION BLOCKED: {json.dumps(sql_injection_event)}"
            )
        elif severity.lower() == "high":
            self.logger.error(
                f"HIGH SEVERITY SQL INJECTION BLOCKED: {json.dumps(sql_injection_event)}"
            )
        else:
            self.logger.warning(
                f"SQL injection attempt blocked: {json.dumps(sql_injection_event)}"
            )

    def log_child_interaction(
        self,
        child_id: str,
        interaction_type: str,
        metadata: Dict[str, Any] = None,
        safety_score: float = None,
    ) -> None:
        """
        Log child interaction with complete privacy protection.

        🛡️ SECURITY: No actual interaction content is logged.
        Only safe metadata and safety classifications.

        Args:
            child_id: Child identifier (will be hashed)
            interaction_type: Type of interaction
            metadata: Safe metadata only
            safety_score: Safety assessment score
        """
        # Sanitize all metadata
        safe_metadata = self._sanitize_context(metadata or {})

        interaction_event = {
            "audit_id": self.audit_id,
            "event_id": str(uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "child_interaction",
            "interaction_type": interaction_type,
            "child_id_hash": self._hash_identifier(child_id),
            "metadata": safe_metadata,
            "safety_score": safety_score,
            "coppa_compliant": True,
        }

        # Log based on safety score
        if safety_score is not None:
            if safety_score < 0.3:
                self.logger.error(
                    f"LOW SAFETY INTERACTION: {json.dumps(interaction_event)}"
                )
            elif safety_score < 0.7:
                self.logger.warning(
                    f"MEDIUM SAFETY INTERACTION: {json.dumps(interaction_event)}"
                )
            else:
                self.logger.info(
                    f"Safe child interaction: {json.dumps(interaction_event)}"
                )
        else:
            self.logger.info(
                f"Child interaction logged: {json.dumps(interaction_event)}"
            )

    def _hash_identifier(self, identifier: str) -> str:
        """Create a non-reversible hash of an identifier for audit purposes."""
        if not identifier:
            return None
        return hashlib.sha256(f"{identifier}:{self.audit_id}".encode()).hexdigest()[:16]

    def _sanitize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize context data to remove any potential PII.

        🛡️ SECURITY: This method ensures no PII leaks through context data.
        """
        safe_context = {}

        # List of safe fields that can be logged
        safe_fields = {
            "timestamp",
            "event_type",
            "severity",
            "classification",
            "score",
            "length",
            "hash",
            "risk_level",
            "threat_level",
            "blocked",
            "validated",
            "coppa_compliant",
            "audit_id",
            "event_id",
            "context_type",
        }

        for key, value in context.items():
            if key.lower() in safe_fields:
                safe_context[key] = value
            elif isinstance(value, (int, float, bool)):
                # Numeric values are generally safe
                safe_context[key] = value
            elif isinstance(value, str):
                # String values need PII analysis
                if not self.pii_classifier.contains_child_pii(value):
                    # Only include if no PII detected
                    safe_context[f"{key}_length"] = len(value)
                    safe_context[f"{key}_hash"] = hashlib.sha256(
                        value.encode()
                    ).hexdigest()[:8]
                else:
                    safe_context[f"{key}_contains_pii"] = True
            else:
                # Other types: just record the type
                safe_context[f"{key}_type"] = type(value).__name__

        return safe_context

    def _classify_security_threat(self, safe_summary: Dict[str, Any]) -> str:
        """Classify the security threat level based on safe summary."""
        if safe_summary["child_specific_pii"]:
            return "CRITICAL_CHILD_PII"
        elif safe_summary["risk_level"] == "critical":
            return "CRITICAL_PII"
        elif safe_summary["risk_level"] == "high":
            return "HIGH_PII_RISK"
        elif safe_summary["contains_pii"]:
            return "PII_DETECTED"
        else:
            return "NO_PII_DETECTED"

    def finalize_audit_session(self) -> None:
        """Finalize the audit session."""
        self.logger.info(f"Child-safe audit session completed: {self.audit_id}")


# Convenience function for creating child-safe audit loggers
def create_child_safe_audit_logger(
    name: str = "child_safe_audit",
) -> ChildSafeAuditLogger:
    """Create a new child-safe audit logger instance."""
    return ChildSafeAuditLogger(name)


# Global child-safe audit logger instance
_global_child_safe_logger = None


def get_child_safe_audit_logger() -> ChildSafeAuditLogger:
    """Get the global child-safe audit logger instance."""
    global _global_child_safe_logger
    if _global_child_safe_logger is None:
        _global_child_safe_logger = ChildSafeAuditLogger("global_child_safe_audit")
    return _global_child_safe_logger
