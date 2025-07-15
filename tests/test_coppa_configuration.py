"""
Test COPPA Configuration Functionality

Tests that COPPA compliance can be enabled/disabled and that
all conditional logic responds appropriately.
"""

import pytest
import os
from unittest.mock import patch

from src.infrastructure.config.coppa_config import (
    get_coppa_config, 
    is_coppa_enabled,
    requires_parental_consent,
    get_data_retention_days,
    should_show_coppa_notices
)
from src.infrastructure.security.coppa_validator import (
    validate_child_age,
    is_coppa_subject,
    COPPAComplianceLevel
)


class TestCOPPAConfiguration:
    """Test COPPA configuration functionality"""
    
    def setup_method(self):
        """Reset COPPA config before each test"""
        get_coppa_config().reset()
    
    def test_coppa_enabled_mode(self):
        """Test behavior when COPPA is enabled"""
        # Force enable COPPA
        get_coppa_config().force_enable()
        
        # Verify configuration
        assert is_coppa_enabled() == True
        assert should_show_coppa_notices() == True
        
        # Test age-based functions
        assert requires_parental_consent(10) == True  # Under 13
        assert requires_parental_consent(15) == False  # Over 13
        assert is_coppa_subject(8) == True
        assert is_coppa_subject(14) == False
        
        # Test data retention
        assert get_data_retention_days(10) == 90  # COPPA limit
        assert get_data_retention_days(15) == 365  # Older child
    
    def test_coppa_disabled_mode(self):
        """Test behavior when COPPA is disabled"""
        # Force disable COPPA
        get_coppa_config().force_disable()
        
        # Verify configuration
        assert is_coppa_enabled() == False
        assert should_show_coppa_notices() == False
        
        # Test age-based functions - should all return permissive values
        assert requires_parental_consent(10) == False  # No consent required
        assert requires_parental_consent(5) == False   # Even young children
        assert is_coppa_subject(8) == False           # Never COPPA subject
        assert is_coppa_subject(5) == False           # Never COPPA subject
        
        # Test data retention - should be extended
        assert get_data_retention_days(10) == 730  # 2 years
        assert get_data_retention_days(15) == 730  # 2 years
    
    def test_coppa_validator_enabled(self):
        """Test COPPA validator when compliance is enabled"""
        get_coppa_config().force_enable()
        
        # Test strict validation
        result = validate_child_age(10)
        assert result.is_coppa_subject == True
        assert result.parental_consent_required == True
        assert result.data_retention_days == 90
        assert result.compliance_level == COPPAComplianceLevel.UNDER_COPPA
        
        # Test special protections
        assert result.special_protections["enhanced_content_filtering"] == True
        assert result.special_protections["restricted_data_sharing"] == True
        assert result.special_protections["audit_trail_required"] == True
    
    def test_coppa_validator_disabled(self):
        """Test COPPA validator when compliance is disabled"""
        get_coppa_config().force_disable()
        
        # Test relaxed validation
        result = validate_child_age(10)
        assert result.is_coppa_subject == False  # Never subject when disabled
        assert result.parental_consent_required == False
        assert result.data_retention_days == 730  # Extended retention
        assert result.compliance_level == COPPAComplianceLevel.GENERAL_PROTECTION
        
        # Test special protections - mostly disabled
        assert result.special_protections["enhanced_content_filtering"] == True  # Still filter for safety
        assert result.special_protections["restricted_data_sharing"] == False
        assert result.special_protections["audit_trail_required"] == False
        
        # Should allow wider age range when disabled
        result_young = validate_child_age(5)
        assert result_young.is_coppa_subject == False
        
        result_old = validate_child_age(16)  # Older than typical COPPA range
        assert result_old.is_coppa_subject == False
    
    def test_environment_based_defaults(self):
        """Test that defaults are set based on environment"""
        # Reset to use environment defaults
        get_coppa_config().reset()
        
        # Mock production environment
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            get_coppa_config().reset()
            # Should enable COPPA in production (if no explicit override)
        
        # Mock development environment  
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            get_coppa_config().reset()
            # Should disable COPPA in development (if no explicit override)
    
    def test_explicit_environment_variable(self):
        """Test explicit ENABLE_COPPA_COMPLIANCE environment variable"""
        # Test explicit enable
        with patch.dict(os.environ, {"ENABLE_COPPA_COMPLIANCE": "true"}):
            get_coppa_config().reset()
            assert is_coppa_enabled() == True
        
        # Test explicit disable
        with patch.dict(os.environ, {"ENABLE_COPPA_COMPLIANCE": "false"}):
            get_coppa_config().reset()
            assert is_coppa_enabled() == False


class TestCOPPAConditionalFunctions:
    """Test that COPPA conditional functions work correctly"""
    
    def setup_method(self):
        """Reset COPPA config before each test"""
        get_coppa_config().reset()
    
    def test_conditional_import_pattern(self):
        """Test the conditional import pattern used throughout codebase"""
        # Enable COPPA
        get_coppa_config().force_enable()
        
        # Import and test
        from src.infrastructure.config.coppa_config import requires_parental_consent
        assert requires_parental_consent(10) == True
        
        # Disable COPPA
        get_coppa_config().force_disable()
        assert requires_parental_consent(10) == False
    
    def test_age_validation_edge_cases(self):
        """Test edge cases in age validation"""
        # Test with COPPA enabled
        get_coppa_config().force_enable()
        
        # Edge case: exactly 13 years old
        assert requires_parental_consent(13) == False  # 13 is not under 13
        assert is_coppa_subject(13) == False
        
        # Edge case: very young child
        assert requires_parental_consent(3) == True
        assert is_coppa_subject(3) == True
        
        # Test with COPPA disabled
        get_coppa_config().force_disable()
        
        # All ages should be permissive when disabled
        assert requires_parental_consent(3) == False
        assert requires_parental_consent(13) == False
        assert is_coppa_subject(3) == False
        assert is_coppa_subject(13) == False
    
    def test_data_retention_calculation(self):
        """Test data retention calculation in both modes"""
        # COPPA enabled - strict retention
        get_coppa_config().force_enable()
        
        assert get_data_retention_days(8) == 90   # Under 13
        assert get_data_retention_days(13) == 365 # 13 and over
        assert get_data_retention_days(15) == 365 # Older teens
        
        # COPPA disabled - extended retention
        get_coppa_config().force_disable()
        
        assert get_data_retention_days(8) == 730  # All ages get extended retention
        assert get_data_retention_days(13) == 730
        assert get_data_retention_days(15) == 730


class TestCOPPAIntegration:
    """Test integration between COPPA components"""
    
    def setup_method(self):
        """Reset COPPA config before each test"""
        get_coppa_config().reset()
    
    def test_compliance_workflow_enabled(self):
        """Test full compliance workflow when COPPA is enabled"""
        get_coppa_config().force_enable()
        
        # Simulate child creation workflow
        child_age = 10
        
        # Step 1: Check if consent required
        consent_required = requires_parental_consent(child_age)
        assert consent_required == True
        
        # Step 2: Validate age compliance
        validation_result = validate_child_age(child_age)
        assert validation_result.parental_consent_required == True
        assert validation_result.is_coppa_subject == True
        
        # Step 3: Check data retention
        retention_days = get_data_retention_days(child_age)
        assert retention_days == 90
        
        # Step 4: Check if notices should be shown
        show_notices = should_show_coppa_notices()
        assert show_notices == True
    
    def test_compliance_workflow_disabled(self):
        """Test workflow when COPPA is disabled - should be streamlined"""
        get_coppa_config().force_disable()
        
        # Simulate same workflow
        child_age = 10
        
        # Step 1: Check if consent required - should be false
        consent_required = requires_parental_consent(child_age)
        assert consent_required == False
        
        # Step 2: Validate age compliance - should be permissive
        validation_result = validate_child_age(child_age)
        assert validation_result.parental_consent_required == False
        assert validation_result.is_coppa_subject == False
        
        # Step 3: Check data retention - should be extended
        retention_days = get_data_retention_days(child_age)
        assert retention_days == 730
        
        # Step 4: Check if notices should be shown - should be false
        show_notices = should_show_coppa_notices()
        assert show_notices == False


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])