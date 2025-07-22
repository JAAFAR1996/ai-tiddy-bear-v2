"""Path security validator with comprehensive security checks.

This module provides path validation functionality to prevent path traversal attacks,
ensure safe file operations, and maintain child-safe environments. It includes
specialized validators for different security contexts and file operation policies.
"""

import os
import re
from enum import Enum
from pathlib import Path
from typing import Optional, Set


class SecurityError(Exception):
    """Security validation error."""
    pass


class PathPolicy(Enum):
    """Path validation policies for different security contexts."""
    STRICT = "strict"  # Very restrictive, for child environments
    STANDARD = "standard"  # Normal web application security
    PERMISSIVE = "permissive"  # More relaxed for admin operations


class PathValidator:
    """Comprehensive path validator with configurable security policies."""

    def __init__(self, policy: PathPolicy = PathPolicy.STANDARD):
        self.policy = policy
        self.allowed_extensions: Set[str] = {
            '.txt', '.json', '.csv', '.log', '.md', '.yml', '.yaml'
        }
        self.restricted_paths: Set[str] = {
            '/etc/', '/proc/', '/sys/', '/dev/', '/root/', '/home/',
            'C:\\Windows\\', 'C:\\Program Files\\', 'C:\\Users\\',
            '.env', '.git', '__pycache__', 'node_modules'
        }

    def validate(self, path: str) -> bool:
        """Basic validation for backward compatibility."""
        return self.validate_path(path, "read")

    def validate_path(self, path: str, operation: str = "read") -> bool:
        """Validate path for security issues based on operation type.

        Args:
            path: The file path to validate
            operation: Type of operation ('read', 'write', 'execute')

        Returns:
            True if path is safe, False if potentially dangerous

        Raises:
            SecurityError: If path is definitely malicious
        """
        if not path or not isinstance(path, str):
            return False

        try:
            # Normalize the path to resolve any relative components
            normalized = os.path.normpath(path)
            resolved = os.path.abspath(normalized)

            # Check for path traversal attempts
            if self._detect_path_traversal(path, normalized):
                if self.policy == PathPolicy.STRICT:
                    raise SecurityError("Path traversal detected")
                return False

            # Check for restricted paths
            if self._check_restricted_paths(resolved):
                if self.policy == PathPolicy.STRICT:
                    raise SecurityError("Access to restricted path")
                return False

            # Check file extension if applicable
            if os.path.splitext(path)[1] and not self._validate_extension(path):
                if self.policy == PathPolicy.STRICT:
                    raise SecurityError("Unsafe file extension")
                return False

            # Additional checks for write operations
            if operation in ("write", "execute"):
                return self._validate_write_operation(resolved)

            return True

        except Exception as e:
            if self.policy == PathPolicy.STRICT:
                raise SecurityError(f"Path validation failed: {e}")
            return False

    def _detect_path_traversal(self, original: str, normalized: str) -> bool:
        """Detect various path traversal patterns."""
        traversal_patterns = [
            '../', '..\\', '..%2f', '..%5c',
            '%2e%2e%2f', '%2e%2e%5c',
            '..../', '....\\',
            '.%2e/', '.%2e\\',
        ]

        original_lower = original.lower()
        normalized_lower = normalized.lower()

        # Check for direct traversal patterns
        for pattern in traversal_patterns:
            if pattern in original_lower:
                return True

        # Check if normalized path goes outside intended directory
        if '..' in normalized or normalized.startswith('/'):
            return True

        # Check for encoded traversal attempts
        if '%' in original:
            try:
                from urllib.parse import unquote
                decoded = unquote(original)
                if any(pattern in decoded.lower() for pattern in traversal_patterns):
                    return True
            except Exception:
                return True  # Suspicious encoding

        return False

    def _check_restricted_paths(self, path: str) -> bool:
        """Check if path accesses restricted system areas."""
        path_lower = path.lower()

        # Check against restricted path patterns
        for restricted in self.restricted_paths:
            if restricted.lower() in path_lower:
                return True

        # Additional system-specific checks
        if os.name == 'nt':  # Windows
            if any(sys_path in path_lower for sys_path in [
                'c:\\windows\\system32', 'c:\\boot\\', 'c:\\$recycle.bin'
            ]):
                return True
        else:  # Unix-like
            if any(sys_path in path_lower for sys_path in [
                '/boot/', '/lib/', '/sbin/', '/bin/sudo'
            ]):
                return True

        return False

    def _validate_extension(self, path: str) -> bool:
        """Validate file extension is safe."""
        _, ext = os.path.splitext(path)

        if not ext:
            return True  # No extension is generally safe

        # Dangerous extensions that should never be allowed
        dangerous_extensions = {
            '.exe', '.bat', '.cmd', '.com', '.scr', '.pif',
            '.sh', '.bash', '.zsh', '.ps1', '.vbs', '.js',
            '.jar', '.msi', '.deb', '.rpm', '.dmg'
        }

        if ext.lower() in dangerous_extensions:
            return False

        # For strict policy, only allow explicitly safe extensions
        if self.policy == PathPolicy.STRICT:
            return ext.lower() in self.allowed_extensions

        return True

    def _validate_write_operation(self, path: str) -> bool:
        """Additional validation for write operations."""
        # Check if path is in a writable area
        try:
            parent_dir = os.path.dirname(path)
            if not os.path.exists(parent_dir):
                return False
            if not os.access(parent_dir, os.W_OK):
                return False
        except (OSError, TypeError):
            return False

        return True


class SecureFileOperations:
    """Wrapper for secure file operations with path validation."""

    def __init__(self, validator: PathValidator):
        self.validator = validator

    def safe_open(self, path: str, mode: str = 'r', **kwargs):
        """Safely open a file with path validation."""
        operation = "write" if any(m in mode for m in ['w', 'a', '+']) else "read"

        if not self.validator.validate_path(path, operation):
            raise SecurityError(f"Unsafe path operation: {path}")

        return open(path, mode, **kwargs)


def create_child_safe_validator() -> PathValidator:
    """Create a path validator with strict child-safe policies."""
    validator = PathValidator(PathPolicy.STRICT)

    # Even more restrictive settings for child safety
    validator.allowed_extensions = {'.txt', '.json', '.md'}
    validator.restricted_paths.update({
        'config/', 'secrets/', 'admin/', '.ssh/', 'credentials',
        'password', 'token', 'key', 'cert', 'private'
    })

    return validator


def get_path_validator(child_safe: bool = False) -> PathValidator:
    """Factory function to get appropriate path validator.

    Args:
        child_safe: If True, returns validator with child-safe strict policies

    Returns:
        Configured PathValidator instance
    """
    if child_safe:
        return create_child_safe_validator()
    return PathValidator(PathPolicy.STANDARD)


def validate_path(path: str, operation: str = "read") -> bool:
    """Convenience function for quick path validation."""
    validator = get_path_validator()
    return validator.validate_path(path, operation)


def safe_open(path: str, mode: str = 'r', **kwargs):
    """Convenience function for safe file opening."""
    validator = get_path_validator()
    operations = SecureFileOperations(validator)
    return operations.safe_open(path, mode, **kwargs)
