"""from pathlib import Path
from typing import Dict, List, Optional, Any, Pattern
import logging
import re
import urllib.parse.
"""

"""General Input Validator
General purpose input validation service for common data types and security checks.
Provides email, URL, file validation with XSS and SQL injection prevention.
"""

try:
    from email_validator import EmailNotValidError, validate_email

    EMAIL_VALIDATOR_AVAILABLE = True
except ImportError:
    EMAIL_VALIDATOR_AVAILABLE = False

from src.infrastructure.logging_config import get_logger

from .validation_types import ValidationResult

logger = get_logger(__name__, component="validation")


class GeneralInputValidator:
    """General purpose input validation service.
    Features: - Email validation - URL validation - File type validation - Size limit validation - XSS prevention - SQL injection prevention.
    """

    def __init__(self) -> None:
        """Initialize general input validator."""
        # Allowed file types for uploads
        self.allowed_image_types = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        self.allowed_audio_types = {".mp3", ".wav", ".ogg", ".m4a"}
        self.allowed_document_types = {".pdf", ".txt", ".doc", ".docx"}

        # Size limits (in bytes)
        self.max_image_size = 5 * 1024 * 1024  # 5MB
        self.max_audio_size = 10 * 1024 * 1024  # 10MB
        self.max_document_size = 2 * 1024 * 1024  # 2MB

        # XSS patterns to detect
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"onload\\s*=",
            r"onerror\\s*=",
            r"onclick\\s*=",
            r"onmouseover\\s*=",
        ]

        # SQL injection patterns
        self.sql_patterns = [
            r"\bunion\\s+select\b",
            r"\bselect\\s+.*\bfrom\b",
            r"\binsert\\s+into\b",
            r"\bdelete\\s+from\b",
            r"\bdrop\\s+table\b",
            r"[\'\"];.*--",
            r"\bor\\s+1\\s*=\\s*1\b",
        ]

        # Compile patterns
        self.compiled_xss = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.xss_patterns
        ]
        self.compiled_sql = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.sql_patterns
        ]

        logger.info("General input validator initialized")

    def validate_email(self, email: str, required: bool = True) -> ValidationResult:
        """Validate email address format and deliverability.
        Args: email: Email address to validate
            required: Whether email is required
        Returns: ValidationResult with validation results.
        """
        if not email:
            if required:
                return ValidationResult(
                    valid=False,
                    errors=["Email address is required"],
                    metadata={"code": "EMAIL_REQUIRED"},
                )
            return ValidationResult(valid=True, sanitized_value=None)

        if not EMAIL_VALIDATOR_AVAILABLE:
            # Fallback to basic regex validation
            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, email):
                return ValidationResult(
                    valid=False,
                    errors=["Invalid email format"],
                    metadata={"code": "INVALID_EMAIL_FORMAT"},
                )
            return ValidationResult(
                valid=True,
                original_value=email,
                sanitized_value=email.lower().strip(),
            )

        try:
            # Use email-validator library for comprehensive validation
            validation = validate_email(email)
            normalized_email = validation.email
            return ValidationResult(
                valid=True,
                original_value=email,
                sanitized_value=normalized_email,
            )
        except EmailNotValidError as e:
            return ValidationResult(
                valid=False,
                errors=[str(e)],
                metadata={"code": "INVALID_EMAIL_FORMAT"},
            )

    def validate_url(
        self,
        url: str,
        allowed_schemes: List[str] = None,
    ) -> ValidationResult:
        """Validate URL format and security.
        Args: url: URL to validate
            allowed_schemes: List of allowed URL schemes(default: ['http', 'https'])
        Returns: ValidationResult with validation results.
        """
        if not url:
            return ValidationResult(
                valid=False,
                errors=["URL cannot be empty"],
                metadata={"code": "EMPTY_URL"},
            )

        allowed_schemes = allowed_schemes or ["http", "https"]

        try:
            parsed_url = urllib.parse.urlparse(url)

            # Check scheme
            if parsed_url.scheme not in allowed_schemes:
                return ValidationResult(
                    valid=False,
                    errors=[f"URL scheme '{parsed_url.scheme}' not allowed"],
                    metadata={
                        "code": "INVALID_URL_SCHEME",
                        "allowed_schemes": allowed_schemes,
                    },
                )

            # Check that hostname exists
            if not parsed_url.netloc:
                return ValidationResult(
                    valid=False,
                    errors=["URL must include a hostname"],
                    metadata={"code": "MISSING_HOSTNAME"},
                )

            # Security check for local/private addresses
            if self._is_local_address(parsed_url.netloc):
                return ValidationResult(
                    valid=False,
                    errors=["Local and private addresses are not allowed"],
                    metadata={"code": "LOCAL_ADDRESS_BLOCKED"},
                    security_flags=["local_address_attempted"],
                )

            return ValidationResult(
                valid=True,
                original_value=url,
                sanitized_value=parsed_url.geturl(),
            )
        except Exception as e:
            return ValidationResult(
                valid=False,
                errors=["Invalid URL format"],
                metadata={"code": "INVALID_URL_FORMAT", "error": str(e)},
            )

    def validate_file_upload(
        self,
        filename: str,
        file_size: int,
        file_content: bytes | None = None,
    ) -> ValidationResult:
        """Validate file upload for security and constraints.
        Args: filename: Name of the uploaded file
            file_size: Size of file in bytes
            file_content: Optional file content for deep validation
        Returns: ValidationResult with validation results.
        """
        if not filename:
            return ValidationResult(
                valid=False,
                errors=["Filename cannot be empty"],
                metadata={"code": "EMPTY_FILENAME"},
            )

        # Check file extension
        file_path = Path(filename)
        file_ext = file_path.suffix.lower()

        # Determine file category and limits
        if file_ext in self.allowed_image_types:
            max_size = self.max_image_size
            file_category = "image"
        elif file_ext in self.allowed_audio_types:
            max_size = self.max_audio_size
            file_category = "audio"
        elif file_ext in self.allowed_document_types:
            max_size = self.max_document_size
            file_category = "document"
        else:
            return ValidationResult(
                valid=False,
                errors=[f"File type '{file_ext}' is not allowed"],
                metadata={"code": "INVALID_FILE_TYPE", "extension": file_ext},
            )

        # Check file size
        if file_size > max_size:
            return ValidationResult(
                valid=False,
                errors=[
                    f"File size {file_size} bytes exceeds maximum {max_size} bytes",
                ],
                metadata={
                    "code": "FILE_TOO_LARGE",
                    "size": file_size,
                    "max_size": max_size,
                },
            )

        # Security check: validate filename
        safe_filename = self._sanitize_filename(filename)

        return ValidationResult(
            valid=True,
            original_value=filename,
            sanitized_value=safe_filename,
            metadata={"file_category": file_category, "file_size": file_size},
        )

    def validate_text_input(
        self,
        text: str,
        max_length: int = 1000,
    ) -> ValidationResult:
        """Validate text input for security issues.
        Args: text: Text input to validate
            max_length: Maximum allowed length
        Returns: ValidationResult with validation results.
        """
        if not text:
            return ValidationResult(
                valid=False,
                errors=["Text input cannot be empty"],
                metadata={"code": "EMPTY_TEXT"},
            )

        # Length check
        if len(text) > max_length:
            return ValidationResult(
                valid=False,
                errors=[
                    f"Text length {len(text)} exceeds maximum {max_length} characters",
                ],
                metadata={
                    "code": "TEXT_TOO_LONG",
                    "length": len(text),
                    "max_length": max_length,
                },
            )

        # XSS detection
        xss_detected = any(pattern.search(text) for pattern in self.compiled_xss)
        if xss_detected:
            return ValidationResult(
                valid=False,
                errors=["Text contains potentially malicious content"],
                metadata={"code": "XSS_DETECTED"},
                security_flags=["xss_attempt"],
            )

        # SQL injection detection
        sql_detected = any(pattern.search(text) for pattern in self.compiled_sql)
        if sql_detected:
            return ValidationResult(
                valid=False,
                errors=["Text contains potentially malicious SQL patterns"],
                metadata={"code": "SQL_INJECTION_DETECTED"},
                security_flags=["sql_injection_attempt"],
            )

        # Sanitize text
        sanitized_text = self._sanitize_text(text)

        return ValidationResult(
            valid=True,
            original_value=text,
            sanitized_value=sanitized_text,
        )

    def _is_local_address(self, hostname: str) -> bool:
        """Check if hostname refers to local / private address."""
        local_patterns = [
            r"^localhost$",
            r"^127\\.",
            r"^192\\.168\\.",
            r"^10\\.",
            r"^172\\.(1[6-9]|2[0-9]|3[01])\\.",
            r"^::1$",
            r"^fe80:",
        ]

        for pattern in local_patterns:
            if re.match(pattern, hostname, re.IGNORECASE):
                return True

        return False

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe storage."""
        # Remove path traversal attempts
        safe_name = filename.replace("..", "").replace("/", "").replace("\\", "")

        # Remove potentially dangerous characters
        safe_name = re.sub(r'[<>:"|?*]', "", safe_name)

        # Ensure reasonable length
        if len(safe_name) > 255:
            name_part, ext_part = (
                safe_name.rsplit(".", 1) if "." in safe_name else (safe_name, "")
            )
            safe_name = name_part[:250] + ("." + ext_part if ext_part else "")

        return safe_name

    def _sanitize_text(self, text: str) -> str:
        """Sanitize text input for safe storage and display."""
        # Remove null bytes
        sanitized = text.replace("\x00", "")

        # Normalize whitespace
        sanitized = re.sub(r"\\s+", " ", sanitized).strip()

        # Remove control characters except common ones (tab, newline)
        sanitized = "".join(
            char for char in sanitized if ord(char) >= 32 or char in "\t\n\r"
        )

        return sanitized


# Factory function
def get_general_input_validator() -> GeneralInputValidator:
    """Create general input validator instance."""
    return GeneralInputValidator()
