"""Centralized COPPA Age Validation Service
This module provides a single source of truth for all COPPA-related age validation
and compliance checks to ensure consistent application of child protection laws.

IMPORTANT: All COPPA functionality is conditional based on ENABLE_COPPA_COMPLIANCE setting.
When disabled, COPPA validations are bypassed for development/testing."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional
import logging

from ..config.coppa_config import is_coppa_enabled, get_coppa_config
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")

class COPPAComplianceLevel(Enum):
    """COPPA compliance levels based on age"""
    UNDER_COPPA = "under_coppa"  # Under 13 - Full COPPA protection required
    COPPA_TRANSITION = "coppa_transition"  # 13-15 - Enhanced protection recommended
    GENERAL_PROTECTION = "general_protection"  # 16+ - Standard protection

@dataclass
class COPPAValidationResult:
    """Result of COPPA age validation"""
    is_coppa_subject: bool
    compliance_level: COPPAComplianceLevel
    parental_consent_required: bool
    data_retention_days: int
    special_protections: Dict[str, bool]
    age_verified: bool

class COPPAValidator:
    """
    Centralized COPPA age validation and compliance service.
    This class provides the authoritative source for all age-related
    COPPA compliance decisions throughout the application.
    """
    
    # COPPA Constants - DO NOT MODIFY WITHOUT LEGAL REVIEW
    COPPA_AGE_LIMIT = 13
    MIN_CHILD_AGE = 3  # Minimum age for platform use
    MAX_CHILD_AGE = 13  # Maximum age for child accounts
    
    # Data retention periods (days)
    COPPA_RETENTION_DAYS = 90  # Maximum COPPA retention
    TRANSITION_RETENTION_DAYS = 365  # For 13-15 age group
    
    def __init__(self):
        self._validation_cache = {}
    
    def validate_age_compliance(self, age: int, strict_validation: bool = True) -> COPPAValidationResult:
        """
        Perform comprehensive COPPA age validation.
        COPPA CONDITIONAL: When COPPA compliance is disabled, validation is relaxed
        to allow development/testing without COPPA restrictions.
        
        Args:
            age: Child's age in years
            strict_validation: Whether to apply strict validation rules
            
        Returns:
            COPPAValidationResult with all compliance requirements
            
        Raises:
            ValueError: If age is invalid or out of acceptable range
        """
        if not isinstance(age, int):
            raise ValueError(f"Age must be an integer, got {type(age)}")
        
        # COPPA CONDITIONAL: Check if COPPA compliance is enabled
        coppa_enabled = is_coppa_enabled()
        if not coppa_enabled:
            # COPPA disabled - relaxed validation for development
            logger.debug(f"COPPA compliance disabled - relaxed age validation for age {age}")
            
            # Still validate basic age range for system functionality
            if age < 1 or age > 18:
                raise ValueError(f"Age {age} is outside acceptable range (1-18)")
            
            # Return permissive result when COPPA disabled
            return COPPAValidationResult(
                is_coppa_subject=False,  # Never subject to COPPA when disabled
                compliance_level=COPPAComplianceLevel.GENERAL_PROTECTION,
                parental_consent_required=False,  # No consent required when disabled
                data_retention_days=365 * 2,  # Longer retention when COPPA disabled
                special_protections={
                    "enhanced_content_filtering": True,  # Still filter content for safety
                    "restricted_data_sharing": False,    # No COPPA restrictions
                    "parental_oversight_required": False, # No COPPA oversight
                    "anonymized_analytics_only": False,  # Regular analytics allowed
                    "encrypted_storage_required": True,  # Still encrypt for security
                    "audit_trail_required": False,      # No COPPA audit trails
                },
                age_verified=True
            )
        
        # COPPA enabled - strict validation
        if age < self.MIN_CHILD_AGE:
            raise ValueError(f"Age {age} is below minimum allowed age of {self.MIN_CHILD_AGE}")
        
        if strict_validation and age > self.MAX_CHILD_AGE:
            raise ValueError(f"Age {age} exceeds maximum child age of {self.MAX_CHILD_AGE}")
        
        # Determine COPPA status (only when COPPA enabled)
        is_coppa_subject = age < self.COPPA_AGE_LIMIT
        
        # Determine compliance level
        if age < self.COPPA_AGE_LIMIT:
            compliance_level = COPPAComplianceLevel.UNDER_COPPA
            retention_days = self.COPPA_RETENTION_DAYS
        elif age <= 15:
            compliance_level = COPPAComplianceLevel.COPPA_TRANSITION
            retention_days = self.TRANSITION_RETENTION_DAYS
        else:
            compliance_level = COPPAComplianceLevel.GENERAL_PROTECTION
            retention_days = self.TRANSITION_RETENTION_DAYS
        
        # Determine special protections
        special_protections = {
            "enhanced_content_filtering": age < 16,
            "restricted_data_sharing": is_coppa_subject,
            "parental_oversight_required": is_coppa_subject,
            "anonymized_analytics_only": is_coppa_subject,
            "encrypted_storage_required": True,  # Always required for children
            "audit_trail_required": True,  # Always required
        }
        
        result = COPPAValidationResult(
            is_coppa_subject=is_coppa_subject,
            compliance_level=compliance_level,
            parental_consent_required=is_coppa_subject,
            data_retention_days=retention_days,
            special_protections=special_protections,
            age_verified=True
        )
        
        # Log validation (without PII)
        logger.info(f"COPPA validation completed: age_group={compliance_level.value}, "
                   f"consent_required={is_coppa_subject}, retention_days={retention_days}")
        
        return result
    
    def is_coppa_subject(self, age: int) -> bool:
        """
        Quick check if age falls under COPPA protection.
        Args:
            age: Child's age in years
        Returns:
            True if child is under COPPA protection (< 13)
        """
        try:
            result = self.validate_age_compliance(age, strict_validation=False)
            return result.is_coppa_subject
        except ValueError:
            # If age validation fails, err on the side of caution
            logger.warning(f"Invalid age for COPPA check: {age}, assuming COPPA subject")
            return True
    
    def get_data_retention_period(self, age: int) -> int:
        """
        Get appropriate data retention period based on age.
        Args:
            age: Child's age in years
        Returns:
            Number of days data should be retained
        """
        try:
            result = self.validate_age_compliance(age, strict_validation=False)
            return result.data_retention_days
        except ValueError:
            # If age validation fails, use most restrictive retention
            logger.warning(f"Invalid age for retention check: {age}, using COPPA retention")
            return self.COPPA_RETENTION_DAYS
    
    def requires_parental_consent(self, age: int) -> bool:
        """
        Check if parental consent is required for this age.
        Args:
            age: Child's age in years
        Returns:
            True if parental consent is required
        """
        return self.is_coppa_subject(age)
    
    def get_content_filtering_level(self, age: int) -> str:
        """
        Get appropriate content filtering level based on age.
        Args:
            age: Child's age in years
        Returns:
            Content filtering level string
        """
        try:
            result = self.validate_age_compliance(age, strict_validation=False)
            if result.compliance_level == COPPAComplianceLevel.UNDER_COPPA:
                return "strict"
            elif result.compliance_level == COPPAComplianceLevel.COPPA_TRANSITION:
                return "moderate"
            else:
                return "standard"
        except ValueError:
            # If age validation fails, use strictest filtering
            return "strict"
    
    def validate_age_range(self, age: int, min_age: Optional[int] = None,
                          max_age: Optional[int] = None) -> bool:
        """
        Validate age is within specified range with COPPA compliance.
        Args:
            age: Child's age to validate
            min_age: Minimum allowed age (default: MIN_CHILD_AGE)
            max_age: Maximum allowed age (default: MAX_CHILD_AGE)
        Returns:
            True if age is valid and compliant
        """
        min_age = min_age or self.MIN_CHILD_AGE
        max_age = max_age or self.MAX_CHILD_AGE
        
        if not isinstance(age, int):
            return False
        
        if age < min_age or age > max_age:
            return False
        
        try:
            self.validate_age_compliance(age)
            return True
        except ValueError:
            return False

# Global instance for consistent validation
coppa_validator = COPPAValidator()

# Convenience functions for backward compatibility - ALL COPPA CONDITIONAL
def is_coppa_subject(age: int) -> bool:
    """
    Check if age is subject to COPPA (< 13 years old)
    COPPA CONDITIONAL: Always returns False when COPPA compliance is disabled
    """
    if not is_coppa_enabled():
        return False  # Never subject to COPPA when disabled
    
    return coppa_validator.is_coppa_subject(age)

def requires_parental_consent(age: int) -> bool:
    """
    Check if parental consent is required for this age
    COPPA CONDITIONAL: Always returns False when COPPA compliance is disabled
    """
    if not is_coppa_enabled():
        return False  # No consent required when COPPA disabled
    
    return coppa_validator.requires_parental_consent(age)

def get_data_retention_days(age: int) -> int:
    """
    Get data retention period in days for this age
    COPPA CONDITIONAL: Returns longer retention when COPPA compliance is disabled
    """
    return coppa_validator.get_data_retention_period(age)

def validate_child_age(age: int) -> COPPAValidationResult:
    """
    Validate child age with full COPPA compliance check
    COPPA CONDITIONAL: Returns relaxed validation when COPPA compliance is disabled
    """
    return coppa_validator.validate_age_compliance(age)