"""Validation Configuration and Data Models
Extracted from input_validation.py to reduce file size
"""

from dataclasses import dataclass, field
from enum import Enum
from .validation_rules import get_default_validation_rules




class ValidationSeverity(Enum):
    """Validation severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ValidationRule:
    """Validation rule definition."""
    pattern: str
    severity: ValidationSeverity
    action: str = "warn"


@dataclass
class InputValidationConfig:
    """Configuration for input validation."""
    dangerous_patterns: list[ValidationRule] = None
    enable_profanity_filter: bool = True
    child_max_string_length: int = 100
    max_string_length: int = 1000
    child_safe_pattern: str = r"^[a-zA-Z0-9\s\.\,\!\?\-\'\"]*$"
    max_object_depth: int = 10
    max_array_length: int = 100
    child_max_array_length: int = 50
    
    def __post_init__(self):
        """Initialize default patterns if none provided."""
        if self.dangerous_patterns is None:
            self.dangerous_patterns = get_default_validation_rules()


