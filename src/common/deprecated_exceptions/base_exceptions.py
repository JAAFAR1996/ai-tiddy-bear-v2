"""Base exceptions for AI Teddy Bear system.
Central location for all base exception classes.
"""

from enum import Enum
from typing import Any, Dict, Optional


class ErrorCategory(Enum):
    """Categories for error classification."""

    DOMAIN = "domain"
    APPLICATION = "application"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"
    VALIDATION = "validation"


class AITeddyBaseError(Exception):
    """Base exception for all AI Teddy Bear errors."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        details: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
    ):
        self.message = message
        self.category = category
        self.details = details or {}
        self.error_code = error_code
        super().__init__(self.message)
