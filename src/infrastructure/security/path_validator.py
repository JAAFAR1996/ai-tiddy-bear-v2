"""
Path Validation Security Service
This module provides secure path validation to prevent directory traversal attacks
and ensure all file operations are restricted to authorized directories.
"""

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


@dataclass
class PathPolicy:
    """Security policy for path operations"""

    allowed_base_dirs: Set[str]
    allowed_extensions: Set[str]
    max_path_length: int = 255
    allow_symlinks: bool = False
    case_sensitive: bool = True


class PathValidator:
    """
    This service validates file paths and prevents directory traversal
    vulnerabilities while maintaining child safety compliance.
    """

    # Dangerous path patterns that indicate traversal attempts
    TRAVERSAL_PATTERNS = [
        r"\\.\\./",  # Unix-style parent directory
        r"\\.\\.\\",  # Windows-style parent directory
        r"%2e%2e",  # URL-encoded ..
        r"%2f",  # URL-encoded /
        r"%5c",  # URL-encoded \\
        r"\\.\\.%2f",  # Mixed encoding
        r"\\.\\.%5c",  # Mixed encoding
        r"%252e%252e",  # Double URL-encoded ..
        r"\x2e\x2e",  # Hex-encoded ..
        r"\\.{2,}",  # Multiple dots
    ]

    def __init__(self, policy: PathPolicy) -> None:
        self.policy = policy
        self._compiled_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.TRAVERSAL_PATTERNS
        ]
        # Normalize base directories for consistent checking
        self.normalized_base_dirs = set()
        for base_dir in policy.allowed_base_dirs:
            normalized = os.path.realpath(os.path.abspath(base_dir))
            self.normalized_base_dirs.add(normalized)
            logger.debug(f"Added normalized base directory: {normalized}")

    def validate_path(self, user_path: str, operation: str = "read") -> bool:
        """
        Validate a user-provided path for security
        Args:
            user_path: The path provided by user/API
            operation: Type of operation (read, write, execute)
        Returns:
            bool: True if path is safe, False otherwise
        """
        try:
            # Basic input validation
            if not user_path or not isinstance(user_path, str):
                logger.warning("Invalid path input: empty or non-string")
                return False
            # Check path length
            if len(user_path) > self.policy.max_path_length:
                logger.warning(
                    f"Path too long: {len(user_path)} > "
                    f"{self.policy.max_path_length}"
                )
                return False
            # Check for traversal patterns
            if self._contains_traversal_patterns(user_path):
                logger.warning(
                    f"Path contains traversal patterns: {user_path}"
                )
                return False
            # Check for null bytes (directory traversal via null byte injection)
            if "\x00" in user_path:
                logger.warning(f"Path contains null bytes: {user_path}")
                return False
            # Normalize and resolve the path
            try:
                normalized_path = os.path.realpath(os.path.abspath(user_path))
            except (OSError, ValueError) as e:
                logger.warning(f"Failed to normalize path {user_path}: {e}")
                return False
            # Check if path is within allowed base directories
            if not self._is_within_allowed_dirs(normalized_path):
                logger.warning(
                    f"Path outside allowed directories: {normalized_path}"
                )
                return False
            # Check file extension if specified
            if self.policy.allowed_extensions:
                file_ext = Path(user_path).suffix.lower()
                if file_ext not in self.policy.allowed_extensions:
                    logger.warning(f"File extension not allowed: {file_ext}")
                    return False
            # Check symlink policy
            if not self.policy.allow_symlinks and os.path.islink(user_path):
                logger.warning(f"Symlinks not allowed: {user_path}")
                return False
            return True
        except Exception as e:
            logger.error(f"Path validation error: {e}")
            return False

    def sanitize_path(self, user_path: str) -> Optional[str]:
        """
        Sanitize a user path by removing dangerous components
        Args:
            user_path: User-provided path
        Returns:
            Optional[str]: Sanitized path or None if cannot be made safe
        """
        if not user_path:
            return None
        try:
            # Remove dangerous patterns
            sanitized = user_path
            for pattern in self.TRAVERSAL_PATTERNS:
                sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)
            # Remove null bytes
            sanitized = sanitized.replace("\x00", "")
            # Normalize path separators
            sanitized = sanitized.replace("\\", "/")
            # Remove duplicate slashes
            sanitized = re.sub(r"/+", "/", sanitized)
            # Remove leading/trailing dots and slashes
            sanitized = sanitized.strip("./")
            if self.validate_path(sanitized):
                return sanitized
            return None
        except Exception as e:
            logger.error(f"Path sanitization error: {e}")
            return None

    def get_safe_path(
        self, user_path: str, base_dir: str = None
    ) -> Optional[str]:
        """
        Get a safe absolute path within the specified base directory
        Args:
            user_path: User-provided path
            base_dir: Base directory to restrict to (must be in allowed dirs)
        Returns:
            Optional[str]: Safe absolute path or None
        """
        try:
            # Use first allowed base directory if none specified
            if base_dir is None:
                if not self.normalized_base_dirs:
                    return None
                base_dir = list(self.normalized_base_dirs)[0]
            # Ensure base directory is allowed
            normalized_base = os.path.realpath(os.path.abspath(base_dir))
            if normalized_base not in self.normalized_base_dirs:
                logger.warning(f"Base directory not allowed: {base_dir}")
                return None
            # Sanitize the user path
            sanitized = self.sanitize_path(user_path)
            if not sanitized:
                return None
            # Combine with base directory
            safe_path = os.path.join(normalized_base, sanitized)
            safe_path = os.path.realpath(safe_path)
            # Final validation
            if self.validate_path(safe_path):
                return safe_path
            return None
        except Exception as e:
            logger.error(f"Safe path generation error: {e}")
            return None

    def _contains_traversal_patterns(self, path: str) -> bool:
        """Check if path contains directory traversal patterns"""
        for pattern in self._compiled_patterns:
            if pattern.search(path):
                return True
        return False

    def _is_within_allowed_dirs(self, normalized_path: str) -> bool:
        """Check if normalized path is within allowed base directories"""
        for base_dir in self.normalized_base_dirs:
            try:
                # Check if path starts with base directory
                if (
                    normalized_path.startswith(base_dir + os.sep)
                    or normalized_path == base_dir
                ):
                    return True
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(
                    f"Path validation error for base_dir '{base_dir}': {e}"
                )
                continue
            except OSError as e:
                logger.error(f"OS error during path validation: {e}")
                continue
        return False


class SecureFileOperations:
    """
    Provides safe file operations that automatically validate paths
    before performing file system operations.
    """

    def __init__(self, validator: PathValidator) -> None:
        self.validator = validator

    def safe_open(self, user_path: str, mode: str = "r", **kwargs):
        """
        Safely open a file after path validation
        Args:
            user_path: User-provided file path
            mode: File open mode
            **kwargs: Additional arguments for open()
        Returns:
            File object or raises SecurityError
        """
        if not self.validator.validate_path(
            user_path, "read" if "r" in mode else "write"
        ):
            raise SecurityError(f"Path validation failed: {user_path}")
        safe_path = self.validator.get_safe_path(user_path)
        if not safe_path:
            raise SecurityError(f"Cannot create safe path: {user_path}")
        try:
            return open(safe_path, mode, **kwargs)
        except Exception as e:
            logger.error(f"File operation error: {e}")
            raise

    def safe_exists(self, user_path: str) -> bool:
        """Safely check if file exists"""
        if not self.validator.validate_path(user_path, "read"):
            return False
        safe_path = self.validator.get_safe_path(user_path)
        if not safe_path:
            return False
        return os.path.exists(safe_path)

    def safe_remove(self, user_path: str) -> bool:
        """Safely remove a file"""
        if not self.validator.validate_path(user_path, "write"):
            return False
        safe_path = self.validator.get_safe_path(user_path)
        if not safe_path:
            return False
        try:
            os.remove(safe_path)
            return True
        except Exception as e:
            logger.error(f"File removal error: {e}")
            return False

    def safe_listdir(self, user_path: str) -> List[str]:
        """Safely list directory contents"""
        if not self.validator.validate_path(user_path, "read"):
            return []
        safe_path = self.validator.get_safe_path(user_path)
        if not safe_path:
            return []
        try:
            return os.listdir(safe_path)
        except Exception as e:
            logger.error(f"Directory listing error: {e}")
            return []


class SecurityError(Exception):
    """Custom exception for security-related path errors"""


def create_child_safe_validator() -> PathValidator:
    """
    Create a path validator with child-safe default policies
    Returns:
        PathValidator: Configured for child safety compliance
    """
    # Define safe base directories for child data
    safe_dirs = {
        "/tmp/teddy_temp",  # Temporary files
        "./data/children",  # Child data (relative to app)
        "./logs",  # Log files
        "./exports",  # Data exports for parents
    }
    # Allow only safe file extensions
    safe_extensions = {
        ".txt",
        ".json",
        ".csv",
        ".log",
        ".wav",
        ".mp3",
        ".png",
        ".jpg",
        ".jpeg",
    }
    policy = PathPolicy(
        allowed_base_dirs=safe_dirs,
        allowed_extensions=safe_extensions,
        max_path_length=255,
        allow_symlinks=False,  # No symlinks for security
        case_sensitive=True,
    )
    return PathValidator(policy)


def create_secure_file_operations() -> SecureFileOperations:
    """
    Create secure file operations with child-safe validation
    Returns:
        SecureFileOperations: Ready for safe file operations
    """
    validator = create_child_safe_validator()
    return SecureFileOperations(validator)


# Global instances for easy access
_default_validator: Optional[PathValidator] = None
_default_file_ops: Optional[SecureFileOperations] = None


def get_path_validator() -> PathValidator:
    """Get global path validator instance"""
    global _default_validator
    if _default_validator is None:
        _default_validator = create_child_safe_validator()
    return _default_validator


def get_secure_file_operations() -> SecureFileOperations:
    """Get global secure file operations instance"""
    global _default_file_ops
    if _default_file_ops is None:
        _default_file_ops = create_secure_file_operations()
    return _default_file_ops


def validate_path(user_path: str) -> bool:
    """Convenience function for path validation"""
    return get_path_validator().validate_path(user_path)


def safe_open(user_path: str, mode: str = "r", **kwargs):
    """Convenience function for safe file opening"""
    return get_secure_file_operations().safe_open(user_path, mode, **kwargs)