"""Main input validation service implementation."""

import json
from typing import Any

from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.audit.comprehensive_audit_integration import (
    get_audit_integration,
)
from src.infrastructure.validators.security.security_types import (
    InputValidationResult,
    SecurityThreat,
)

from .security_validator import ThreatDetectors

logger = get_logger(__name__, component="security")


class ComprehensiveInputValidator(ThreatDetectors):
    """Comprehensive input validator with security threat detection and child safety.

    Features:
    - SQL injection detection
    - XSS attack prevention
    - Path traversal detection
    - LDAP injection detection
    - Command injection detection
    - Child-inappropriate content detection
    - PII detection and sanitization
    - File upload validation
    - Request size limits
    """

    def __init__(self):
        super().__init__()
        self.audit_integration = get_audit_integration()

    async def validate_input(
        self,
        data: Any,
        field_name: str = "input",
        context: dict[str, Any] | None = None,
    ) -> InputValidationResult:
        """Validate input data for security threats and child safety.

        Args:
            data: Input data to validate
            field_name: Name of the field being validated
            context: Additional context (user info, endpoint, etc.)

        Returns:
            InputValidationResult with validation results
        """
        threats = []
        errors = []
        child_safety_violations = []

        try:
            # Convert data to string for pattern matching
            if isinstance(data, dict):
                text_data = json.dumps(data)
            elif isinstance(data, (list, int, float, bool)):
                text_data = str(data)
            elif data is None:
                return InputValidationResult(True)
            else:
                text_data = str(data)

            # Check for security threats
            threats.extend(await self.detect_sql_injection(text_data, field_name))
            threats.extend(await self.detect_xss(text_data, field_name))
            threats.extend(await self.detect_path_traversal(text_data, field_name))
            threats.extend(await self.detect_command_injection(text_data, field_name))
            threats.extend(await self.detect_ldap_injection(text_data, field_name))
            threats.extend(await self.detect_template_injection(text_data, field_name))

            # Check for child safety issues
            child_safety_violations.extend(
                await self.detect_inappropriate_content(text_data, field_name),
            )
            child_safety_violations.extend(await self.detect_pii(text_data, field_name))

            # Validate input size
            if len(text_data) > 100000:  # 100KB limit
                threats.append(
                    SecurityThreat(
                        "oversized_input",
                        "high",
                        field_name,
                        text_data[:100],
                        "Input exceeds maximum size limit",
                    ),
                )

            # Check for encoding attacks
            threats.extend(await self.detect_encoding_attacks(text_data, field_name))

            # Additional context-based validation
            if context:
                threats.extend(
                    await self._validate_context_specific(
                        text_data, field_name, context
                    )
                )

            # Determine if input is valid
            critical_threats = [t for t in threats if t.severity == "critical"]
            high_threats = [t for t in threats if t.severity == "high"]
            is_valid = (
                len(critical_threats) == 0
                and len(high_threats) == 0
                and len(child_safety_violations) == 0
            )

            # Log validation results for audit
            if threats or child_safety_violations:
                await self._log_validation_results(
                    field_name, threats, child_safety_violations, context
                )

            return InputValidationResult(
                is_valid=is_valid,
                threats=threats,
                errors=errors,
                child_safety_violations=child_safety_violations,
            )
        except Exception as e:
            logger.error(f"Input validation error for {field_name}: {e}")
            errors.append(f"Validation failed: {e!s}")
            return InputValidationResult(
                False,
                threats,
                errors,
                child_safety_violations,
            )

    async def _validate_context_specific(
        self, text_data: str, field_name: str, context: dict[str, Any]
    ) -> list[SecurityThreat]:
        """Perform context-specific validation."""
        threats = []

        # Child endpoint validation
        if context.get("is_child_endpoint", False):
            # More strict validation for child endpoints
            if len(text_data) > 1000:  # Smaller limit for children
                threats.append(
                    SecurityThreat(
                        "child_input_too_long",
                        "medium",
                        field_name,
                        text_data[:50],
                        "Input too long for child endpoint",
                    )
                )

        # Auth endpoint validation
        if context.get("is_auth_endpoint", False):
            # Check for common auth bypass attempts
            auth_bypass_patterns = ["admin", "root", "test", "guest"]
            for pattern in auth_bypass_patterns:
                if pattern in text_data.lower():
                    threats.append(
                        SecurityThreat(
                            "auth_bypass_attempt",
                            "high",
                            field_name,
                            pattern,
                            f"Potential auth bypass attempt: {pattern}",
                        )
                    )

        return threats

    async def _log_validation_results(
        self,
        field_name: str,
        threats: list[SecurityThreat],
        child_safety_violations: list[str],
        context: dict[str, Any] | None,
    ) -> None:
        """Log validation results for audit purposes."""
        try:
            if threats:
                threat_summary = {
                    "field": field_name,
                    "threat_count": len(threats),
                    "threat_types": [t.threat_type for t in threats],
                    "max_severity": max(t.severity for t in threats),
                }

                await self.audit_integration.log_security_event(
                    event_type="input_validation_threats",
                    severity="warning",
                    description=f"Security threats detected in field {field_name}",
                    details=threat_summary,
                )

            if child_safety_violations:
                await self.audit_integration.log_security_event(
                    event_type="child_safety_violations",
                    severity="high",
                    description=f"Child safety violations in field {field_name}",
                    details={
                        "field": field_name,
                        "violation_count": len(child_safety_violations),
                        "violations": child_safety_violations[:5],  # Log first 5
                    },
                )
        except Exception as e:
            logger.error(f"Failed to log validation results: {e}")

    async def validate_file_upload(
        self,
        filename: str,
        content_type: str,
        file_size: int,
        max_size: int = 10 * 1024 * 1024,  # 10MB default
    ) -> InputValidationResult:
        """Validate file upload parameters."""
        threats = []
        errors = []

        # Check file size
        if file_size > max_size:
            threats.append(
                SecurityThreat(
                    "file_too_large",
                    "medium",
                    "file_size",
                    str(file_size),
                    f"File size {file_size} exceeds limit {max_size}",
                )
            )

        # Check filename for path traversal
        filename_threats = await self.detect_path_traversal(filename, "filename")
        threats.extend(filename_threats)

        # Check for dangerous file extensions
        dangerous_extensions = [
            ".exe",
            ".bat",
            ".cmd",
            ".com",
            ".pif",
            ".scr",
            ".vbs",
            ".js",
            ".jar",
            ".php",
            ".asp",
            ".jsp",
        ]

        file_ext = filename.lower().split(".")[-1] if "." in filename else ""
        if f".{file_ext}" in dangerous_extensions:
            threats.append(
                SecurityThreat(
                    "dangerous_file_type",
                    "high",
                    "filename",
                    filename,
                    f"Dangerous file extension: .{file_ext}",
                )
            )

        # Validate content type
        allowed_types = [
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
            "audio/mpeg",
            "audio/wav",
            "audio/ogg",
            "text/plain",
            "application/pdf",
        ]

        if content_type not in allowed_types:
            threats.append(
                SecurityThreat(
                    "invalid_content_type",
                    "medium",
                    "content_type",
                    content_type,
                    f"Content type not allowed: {content_type}",
                )
            )

        is_valid = len([t for t in threats if t.severity in ["critical", "high"]]) == 0

        return InputValidationResult(
            is_valid=is_valid,
            threats=threats,
            errors=errors,
            child_safety_violations=[],
        )


# Global validator instance for direct use
_global_validator: ComprehensiveInputValidator | None = None


def get_input_validator() -> ComprehensiveInputValidator:
    """Get global input validator instance."""
    global _global_validator
    if _global_validator is None:
        _global_validator = ComprehensiveInputValidator()
    return _global_validator


# Convenience functions for manual validation
async def validate_user_input(
    data: Any,
    field_name: str = "input",
    require_child_safe: bool = False,
) -> InputValidationResult:
    """Validate user input manually."""
    validator = get_input_validator()
    result = await validator.validate_input(data, field_name)
    if require_child_safe and result.child_safety_violations:
        result.is_valid = False
    return result


async def validate_child_message(message: str) -> InputValidationResult:
    """Validate message content for child safety."""
    context = {"is_child_endpoint": True}
    validator = get_input_validator()
    result = await validator.validate_input(message, "message", context)

    # For child messages, any safety violation makes it invalid
    if result.child_safety_violations:
        result.is_valid = False

    return result


async def validate_parent_input(
    data: Any, field_name: str = "input"
) -> InputValidationResult:
    """Validate parent/guardian input with standard security checks."""
    return await validate_user_input(data, field_name, require_child_safe=False)


async def validate_admin_input(
    data: Any, field_name: str = "input"
) -> InputValidationResult:
    """Validate admin input with enhanced security checks."""
    context = {"is_admin_endpoint": True, "strict_mode": True}
    validator = get_input_validator()
    return await validator.validate_input(data, field_name, context)


# Quick validation helpers
async def is_safe_for_children(text: str) -> bool:
    """Quick check if text is safe for children."""
    result = await validate_child_message(text)
    return result.is_valid


async def has_security_threats(text: str) -> bool:
    """Quick check if text contains security threats."""
    result = await validate_user_input(text)
    return len(result.threats) > 0


async def get_threat_summary(text: str) -> dict:
    """Get summary of threats in text."""
    result = await validate_user_input(text)
    return {
        "has_threats": len(result.threats) > 0,
        "threat_count": len(result.threats),
        "threat_types": [t.threat_type for t in result.threats],
        "max_severity": (
            max([t.severity for t in result.threats]) if result.threats else "none"
        ),
        "child_safety_violations": len(result.child_safety_violations),
        "is_valid": result.is_valid,
    }


InputValidator = ComprehensiveInputValidator
