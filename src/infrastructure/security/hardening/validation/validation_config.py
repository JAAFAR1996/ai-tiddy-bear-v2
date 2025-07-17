"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List
"""

"""Validation Configuration and Data Models
Extracted from input_validation.py to reduce file size"""


class ValidationSeverity(str, Enum):
    """Severity levels for validation issues"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ValidationRule:
    """Configuration for input validation rules"""
    pattern: str
    message: str
    severity: ValidationSeverity
    action: str = "block"  # "block", "sanitize", "warn"


@dataclass
class InputValidationConfig:
    """Configuration for input validation"""
    # Maximum sizes
    max_json_size: int = 1024 * 1024  # 1MB
    max_string_length: int = 10000
    max_array_length: int = 1000
    max_object_depth: int = 10
    
    # Child safety patterns (more restrictive)
    child_max_string_length: int = 1000
    child_max_array_length: int = 100
    
    # Dangerous patterns to block
    dangerous_patterns: List[ValidationRule] = field(default_factory=list)
    
    # Allowed characters for child inputs
    child_safe_pattern: str = r'^[a-zA-Z0-9\s\.\,\!\?\-\'\"]*$'
    
    # Content filtering
    enable_profanity_filter: bool = True
    enable_personal_info_detection: bool = True