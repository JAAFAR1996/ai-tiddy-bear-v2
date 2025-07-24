# src/infrastructure/validators/security/security_validator.py

from datetime import datetime
from typing import Any, List, Optional

from src.infrastructure.logging_config import get_logger
from src.infrastructure.validators.security.detectors import ThreatDetectors
from src.infrastructure.validators.security.security_types import (
    InputValidationResult,
    SecurityThreat,
)

logger = get_logger(__name__, component="security-validator")


class SecurityValidator(ThreatDetectors):
    """
    Enterprise Security Validator for AI Teddy Bear Platform.

    - Detects classic/advanced threats (SQLi, XSS, Path Traversal, إلخ)
    - Child safety and privacy (GDPR/COPPA)
    - Integrates with audit/security log if needed
    - Designed for FastAPI/FastService (async/await)
    """

    def __init__(self):
        super().__init__()

    async def validate(
        self, data: Any, field: str = "input", context: Optional[dict] = None
    ) -> InputValidationResult:
        """
        Validate generic input for security, privacy and child safety.
        Returns InputValidationResult.
        """
        threats: List[SecurityThreat] = []
        child_safety_violations: List[str] = []
        errors: List[str] = []

        # Preprocess input to string for checks
        if isinstance(data, dict):
            value = str(data)
        elif data is None:
            return InputValidationResult(True)
        else:
            value = str(data)

        # Detect classic threats
        threats += await self.detect_sql_injection(value, field)
        threats += await self.detect_xss(value, field)
        threats += await self.detect_path_traversal(value, field)
        threats += await self.detect_command_injection(value, field)
        threats += await self.detect_ldap_injection(value, field)
        threats += await self.detect_template_injection(value, field)
        threats += await self.detect_encoding_attacks(value, field)

        # Child-safety, privacy threats
        child_safety_violations += await self.detect_inappropriate_content(value, field)
        child_safety_violations += await self.detect_pii(value, field)

        # Validate input length
        if len(value) > 100_000:
            threats.append(
                SecurityThreat(
                    threat_type="oversized_input",
                    severity="high",
                    field_name=field,
                    value=value[:128],
                    description="Input size exceeds allowed maximum",
                )
            )

        # Is valid if no critical/high threat and no child violations
        is_valid = (
            not any(t.severity in ("critical", "high") for t in threats)
            and len(child_safety_violations) == 0
        )

        # Compose result
        result = InputValidationResult(
            is_valid=is_valid,
            threats=threats,
            errors=errors,
            child_safety_violations=child_safety_violations,
            metadata={"field": field, "validated_at": datetime.utcnow()},
        )

        # Audit (optional, extend as needed)
        if threats or child_safety_violations:
            logger.warning(
                f"[SECURITY VALIDATOR] Threats: {threats}, Child Safety: {child_safety_violations} | Field: {field}"
            )
        return result

    async def validate_file_upload(
        self,
        filename: str,
        content_type: str,
        file_size: int,
        max_size: int = 10 * 1024 * 1024,
    ) -> InputValidationResult:
        """Validate file upload parameters for security."""
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

        # Path traversal in filename
        threats += await self.detect_path_traversal(filename, "filename")

        # Dangerous extensions
        forbidden_ext = [
            ".exe",
            ".bat",
            ".cmd",
            ".com",
            ".scr",
            ".vbs",
            ".js",
            ".php",
            ".asp",
            ".jsp",
        ]
        ext = "." + filename.lower().split(".")[-1] if "." in filename else ""
        if ext in forbidden_ext:
            threats.append(
                SecurityThreat(
                    "dangerous_file_type",
                    "high",
                    "filename",
                    filename,
                    f"Dangerous file extension: {ext}",
                )
            )

        # Content-type checks
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

        is_valid = not any(t.severity in ("critical", "high") for t in threats)
        return InputValidationResult(
            is_valid=is_valid,
            threats=threats,
            errors=errors,
            child_safety_violations=[],
            metadata={"filename": filename, "checked_at": datetime.utcnow()},
        )
