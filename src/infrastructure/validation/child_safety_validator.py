"""
from typing import Dict, List, Optional, Union, Any, Pattern
import logging
import re
from .types import ValidationResult, ValidationError
"""

"""Child Safety Input Validation Service
Provides COPPA - compliant validation specifically focused on child safety, including age validation, content filtering, and PII protection.
"""

from src.infrastructure.logging_config import get_logger
logger = get_logger(__name__, component="validation")

class ChildSafetyValidator:
    """
    Child safety - focused input validation service.
    Features: - COPPA - compliant age validation - Content safety filtering - PII detection and protection - Malicious content detection - Child - appropriate content validation
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize child safety validator with safety patterns."""
        config = config or {}
        # Age validation boundaries (COPPA compliance)
        self.min_child_age: int = config.get('min_child_age', 3)
        self.max_child_age: int = config.get('max_child_age', 13)
        self.coppa_age_threshold: int = config.get('coppa_age_threshold', 13)
        
        # Enhanced security configuration
        self.enable_pii_detection: bool = config.get('enable_pii_detection', True)
        self.enable_content_scoring: bool = config.get('enable_content_scoring', True)
        self.strict_mode: bool = config.get('strict_mode', True)
        self.max_validation_time_ms: int = config.get('max_validation_time_ms', 1000)
        
        # Prohibited content patterns
        self.prohibited_patterns = [
            # Personal information patterns
            r'\b\\\d{3}-\\\d{2}-\\\d{4}\b',  # SSN
            r'\b\\\d{4}[\\\s-]?\\\d{4}[\\\s-]?\\\d{4}[\\\s-]?\\\d{4}\b',  # Credit card
            r'\b\\\d{3}[\\\s-]?\\\d{3}[\\\s-]?\\\d{4}\b',  # Phone number
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\\\.[A-Z|a-z]{2,}\b',  # Email
            
            # Location information
            r'\b\\\d{1,5}\\\s+[A-Za-z0-9\\\s,]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|court|ct)\b',
            r'\b\\\d{5}(?:-\\\d{4})?\b',  # ZIP codes
            
            # Inappropriate content
            r'\b(?:password|secret|private|confidential)\b',
            r'\b(?:meet|meetup|visit|come over|address|location)\b',
        ]
        
        # Child-appropriate content patterns
        self.appropriate_patterns = [
            r'\b(?:play|fun|game|story|learn|sing|dance|draw|color)\b',
            r'\b(?:happy|excited|curious|creative|friendly|kind)\b',
            r'\b(?:family|mom|dad|parent|brother|sister|pet|friend)\b',
        ]
        
        # Compile patterns for performance
        try:
            self.compiled_prohibited: List[Pattern[str]] = [
                re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                for pattern in self.prohibited_patterns
            ]
            self.compiled_appropriate: List[Pattern[str]] = [
                re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                for pattern in self.appropriate_patterns
            ]
        except re.error as e:
            logger.error(f"Failed to compile regex patterns: {e}")
            raise ValidationError("Invalid security patterns configuration",
                                code="PATTERN_COMPILE_ERROR")
        
        # Security enhancement: pattern matching cache
        self._pattern_cache: Dict[str, bool] = {}
        self._cache_max_size: int = 1000
        
        logger.info("Child safety validator initialized with COPPA compliance")

    def validate_child_age(self, age: Union[int, str, None]) -> ValidationResult:
        """
        Validate child age for COPPA compliance.
        Args: age: Child's age as integer or string
        Returns:
            ValidationResult with COPPA requirements
        """
        if age is None:
            return ValidationResult(
                valid=False,
                errors=["Age is required for child registration"],
                metadata={"code": "AGE_REQUIRED", "coppa_applicable": True}
            )
        
        try:
            # Enhanced age validation with bounds checking
            if isinstance(age, str):
                age = age.strip()
                if not age.isdigit():
                    raise ValueError("Age must be a positive integer")
            
            age_int = int(age)
            
            # Security: Check for unrealistic age values
            if age_int < 0 or age_int > 150:
                return ValidationResult(
                    valid=False,
                    errors=[f"Age {age_int} is not realistic (must be 0-150)"],
                    metadata={"code": "AGE_UNREALISTIC", "security_issue": True},
                    security_flags=["unrealistic_age_value"]
                )
            
            if age_int < self.min_child_age:
                return ValidationResult(
                    valid=False,
                    errors=[f"Age {age_int} too young for platform (minimum: {self.min_child_age})"],
                    metadata={
                        "code": "AGE_TOO_YOUNG",
                        "coppa_applicable": True,
                        "parental_consent_required": True
                    }
                )
            
            if age_int > self.max_child_age:
                return ValidationResult(
                    valid=False,
                    errors=[f"Age {age_int} exceeds child platform limit (maximum: {self.max_child_age})"],
                    metadata={
                        "code": "AGE_TOO_OLD",
                        "coppa_applicable": False,
                        "parental_consent_required": False
                    }
                )
            
            # Check COPPA requirements
            coppa_applicable = age_int < self.coppa_age_threshold
            return ValidationResult(
                valid=True,
                sanitized_value=age_int,
                original_value=age,
                metadata={
                    "coppa_applicable": coppa_applicable,
                    "parental_consent_required": coppa_applicable,
                    "data_collection_restrictions": coppa_applicable,
                    "age_group": self._get_age_group(age_int)
                }
            )
        except (ValueError, TypeError, OverflowError) as e:
            return ValidationResult(
                valid=False,
                errors=["Invalid age format - must be a valid number"],
                metadata={
                    "code": "INVALID_AGE_FORMAT",
                    "coppa_applicable": True,
                    "parental_consent_required": True,
                    "original_error": str(e)
                },
                security_flags=["invalid_age_format"]
            )

    def validate_child_message(self, message: str, child_age: int = None) -> Dict[str, Any]:
        """
        Validate and sanitize child's message for safety.
        Args: message: Child's input message
            child_age: Optional child age for age - appropriate validation
        Returns: Dict with validation results and sanitized content
        """
        if not message or not isinstance(message, str):
            return {
                "valid": False,
                "reason": "Message cannot be empty",
                "code": "EMPTY_MESSAGE"
            }
        
        # Length validation
        if len(message) > 1000:
            return {
                "valid": False,
                "reason": "Message too long (maximum 1000 characters)",
                "code": "MESSAGE_TOO_LONG"
            }
        
        # Check for prohibited content
        pii_detected = []
        for pattern in self.compiled_prohibited:
            matches = pattern.findall(message)
            if matches:
                pii_detected.extend(matches)
        
        if pii_detected:
            return {
                "valid": False,
                "reason": "Message contains personal information that cannot be shared",
                "code": "PII_DETECTED",
                "child_friendly_message": "Remember, never share personal information like phone numbers or addresses!",
                "detected_patterns": len(pii_detected)
            }
        
        # Calculate appropriateness score
        appropriate_score = self._calculate_appropriateness_score(message)
        
        return {
            "valid": True,
            "sanitized_message": self._sanitize_message(message),
            "original_message": message,
            "appropriateness_score": appropriate_score,
            "age_appropriate": appropriate_score > 0.7,
            "code": "MESSAGE_VALID"
        }

    def _get_age_group(self, age: int) -> str:
        """Categorize age into appropriate groups."""
        if age <= 5:
            return "preschool"
        elif age <= 8:
            return "elementary"
        elif age <= 11:
            return "middle_elementary"
        else:
            return "middle_school"

    def _calculate_appropriateness_score(self, message: str) -> float:
        """Calculate how appropriate the message is for children."""
        score = 0.5  # Base score
        
        # Check for appropriate content
        for pattern in self.compiled_appropriate:
            if pattern.search(message):
                score += 0.1
        
        # Normalize score between 0 and 1
        return min(score, 1.0)

    def _sanitize_message(self, message: str) -> str:
        """Remove or mask potentially unsafe content."""
        sanitized = message
        
        # Remove any remaining PII patterns
        for pattern in self.compiled_prohibited:
            sanitized = pattern.sub("[REMOVED]", sanitized)
        
        return sanitized.strip()

# Global instance
_child_safety_validator: Optional[ChildSafetyValidator] = None

def get_child_safety_validator() -> ChildSafetyValidator:
    """Get or create global child safety validator instance."""
    global _child_safety_validator
    if _child_safety_validator is None:
        _child_safety_validator = ChildSafetyValidator()
    return _child_safety_validator