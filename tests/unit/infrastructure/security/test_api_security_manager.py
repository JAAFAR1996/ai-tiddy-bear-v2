"""
Tests for API Security Manager
Testing API-level security including rate limiting and input sanitization.
"""

import pytest
from unittest.mock import patch, Mock
import time
import html

from src.infrastructure.security.api_security_manager import APISecurityManager


class TestAPISecurityManager:
    """Test the API Security Manager."""
    
    @pytest.fixture
    def security_manager(self):
        """Create an API security manager instance."""
        return APISecurityManager()
    
    def test_initialization(self, security_manager):
        """Test security manager initialization."""
        assert isinstance(security_manager, APISecurityManager)
        assert hasattr(security_manager, 'rate_limit_storage')
        assert hasattr(security_manager, 'rate_limit_window')
        assert hasattr(security_manager, 'rate_limit_max_requests')
        assert hasattr(security_manager, 'blocked_ips')
        assert hasattr(security_manager, 'max_input_length')
        
        assert isinstance(security_manager.rate_limit_storage, dict)
        assert isinstance(security_manager.blocked_ips, set)
        assert security_manager.rate_limit_window == 60
        assert security_manager.rate_limit_max_requests == 100
        assert security_manager.max_input_length == 1000
        
        assert len(security_manager.rate_limit_storage) == 0
        assert len(security_manager.blocked_ips) == 0
    
    def test_check_rate_limit_first_request(self, security_manager):
        """Test rate limiting for first request from IP."""
        ip_address = "192.168.1.100"
        
        result = security_manager.check_rate_limit(ip_address)
        
        assert result is True
        assert ip_address in security_manager.rate_limit_storage
        assert len(security_manager.rate_limit_storage[ip_address]) == 1
    
    def test_check_rate_limit_within_limits(self, security_manager):
        """Test rate limiting within acceptable limits."""
        ip_address = "192.168.1.101"
        
        # Make 50 requests (well within limit of 100)
        for _ in range(50):
            result = security_manager.check_rate_limit(ip_address)
            assert result is True
        
        assert len(security_manager.rate_limit_storage[ip_address]) == 50
    
    def test_check_rate_limit_exceeds_limit(self, security_manager):
        """Test rate limiting when exceeding limits."""
        ip_address = "192.168.1.102"
        
        # Make exactly max_requests (should all pass)
        for _ in range(security_manager.rate_limit_max_requests):
            result = security_manager.check_rate_limit(ip_address)
            assert result is True
        
        # Next request should be rate limited
        result = security_manager.check_rate_limit(ip_address)
        assert result is False
    
    def test_check_rate_limit_window_expiry(self, security_manager):
        """Test that rate limit window properly expires old requests."""
        ip_address = "192.168.1.103"
        
        with patch('time.time') as mock_time:
            # Start at time 0
            mock_time.return_value = 0
            
            # Make max requests
            for _ in range(security_manager.rate_limit_max_requests):
                security_manager.check_rate_limit(ip_address)
            
            # Should be rate limited
            assert security_manager.check_rate_limit(ip_address) is False
            
            # Advance time beyond window
            mock_time.return_value = security_manager.rate_limit_window + 1
            
            # Should be allowed again
            assert security_manager.check_rate_limit(ip_address) is True
    
    def test_check_rate_limit_blocked_ip(self, security_manager):
        """Test rate limiting for blocked IP addresses."""
        ip_address = "192.168.1.104"
        
        # Block the IP
        security_manager.block_ip(ip_address)
        
        # Should be blocked regardless of rate limit
        result = security_manager.check_rate_limit(ip_address)
        assert result is False
    
    def test_check_rate_limit_error_handling(self, security_manager):
        """Test rate limiting error handling."""
        ip_address = "192.168.1.105"
        
        # Mock an error in time.time()
        with patch('time.time', side_effect=Exception("Time error")):
            # Should fail open (allow request) on error
            result = security_manager.check_rate_limit(ip_address)
            assert result is True
    
    def test_block_ip_success(self, security_manager):
        """Test successful IP blocking."""
        ip_address = "192.168.1.106"
        
        assert ip_address not in security_manager.blocked_ips
        
        security_manager.block_ip(ip_address)
        
        assert ip_address in security_manager.blocked_ips
    
    def test_unblock_ip_success(self, security_manager):
        """Test successful IP unblocking."""
        ip_address = "192.168.1.107"
        
        # Block first
        security_manager.block_ip(ip_address)
        assert ip_address in security_manager.blocked_ips
        
        # Then unblock
        security_manager.unblock_ip(ip_address)
        assert ip_address not in security_manager.blocked_ips
    
    def test_unblock_ip_not_blocked(self, security_manager):
        """Test unblocking IP that wasn't blocked."""
        ip_address = "192.168.1.108"
        
        # Should not raise error
        security_manager.unblock_ip(ip_address)
        assert ip_address not in security_manager.blocked_ips
    
    def test_sanitize_input_basic(self, security_manager):
        """Test basic input sanitization."""
        test_input = "Hello, world!"
        result = security_manager.sanitize_input(test_input)
        
        assert result == "Hello, world!"
    
    def test_sanitize_input_empty_string(self, security_manager):
        """Test sanitization of empty string."""
        result = security_manager.sanitize_input("")
        assert result == ""
        
        result = security_manager.sanitize_input(None)
        assert result == ""
    
    def test_sanitize_input_html_escape(self, security_manager):
        """Test HTML escaping in sanitization."""
        test_input = "<script>alert('xss')</script>"
        result = security_manager.sanitize_input(test_input)
        
        # Should escape HTML tags
        assert "&lt;" in result
        assert "&gt;" in result
        assert "<script>" not in result
    
    def test_sanitize_input_length_limit(self, security_manager):
        """Test input length limiting."""
        # Create input longer than max_input_length
        long_input = "a" * (security_manager.max_input_length + 100)
        result = security_manager.sanitize_input(long_input)
        
        assert len(result) <= security_manager.max_input_length
    
    def test_sanitize_input_null_bytes(self, security_manager):
        """Test removal of null bytes."""
        test_input = "Hello\x00World"
        result = security_manager.sanitize_input(test_input)
        
        assert "\x00" not in result
        assert result == "HelloWorld"
    
    def test_sanitize_input_control_characters(self, security_manager):
        """Test removal of control characters."""
        test_input = "Hello\x01\x02World\n\tTest"
        result = security_manager.sanitize_input(test_input)
        
        # Should remove control characters but keep newline and tab
        assert "\x01" not in result
        assert "\x02" not in result
        assert "\n" in result
        assert "\t" in result
    
    def test_sanitize_input_sql_injection_patterns(self, security_manager):
        """Test removal of SQL injection patterns."""
        sql_injections = [
            "'; DROP TABLE users; --",
            "UNION SELECT * FROM passwords",
            "INSERT INTO admin VALUES",
            "UPDATE users SET password",
            "DELETE FROM accounts",
            "CREATE TABLE malicious",
            "ALTER TABLE users",
            "EXEC xp_cmdshell",
            "/* comment */ SELECT",
            "sp_executesql"
        ]
        
        for injection in sql_injections:
            result = security_manager.sanitize_input(injection)
            
            # SQL keywords should be removed or modified
            assert "DROP TABLE" not in result.upper()
            assert "UNION SELECT" not in result.upper()
            assert "INSERT INTO" not in result.upper()
            assert "UPDATE" not in result or "SET" not in result.upper()
            assert "DELETE FROM" not in result.upper()
    
    def test_sanitize_input_xss_patterns(self, security_manager):
        """Test removal of XSS patterns."""
        xss_attempts = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "vbscript:msgbox('xss')",
            "<img onload='alert(1)'>",
            "<div onerror='alert(1)'>",
            "<span onclick='malicious()'>",
        ]
        
        for xss in xss_attempts:
            result = security_manager.sanitize_input(xss)
            
            # XSS patterns should be removed
            assert "javascript:" not in result.lower()
            assert "vbscript:" not in result.lower()
            assert "onload=" not in result.lower()
            assert "onerror=" not in result.lower()
            assert "onclick=" not in result.lower()
            assert "<script>" not in result.lower()
    
    def test_sanitize_input_error_handling(self, security_manager):
        """Test sanitization error handling."""
        # Mock an error in the sanitization process
        with patch('html.escape', side_effect=Exception("Escape error")):
            result = security_manager.sanitize_input("test input")
            
            # Should return empty string on error
            assert result == ""
    
    def test_validate_child_input_safe_content(self, security_manager):
        """Test child input validation with safe content."""
        safe_inputs = [
            "Hello, I want to play a game!",
            "Can you tell me a story about dinosaurs?",
            "What is 2 + 2?",
            "I like ice cream and cookies",
            "My favorite color is blue"
        ]
        
        for safe_input in safe_inputs:
            result = security_manager.validate_child_input(safe_input)
            
            assert result["is_safe"] is True
            assert result["sanitized_input"] == safe_input
            assert len(result["blocked_content"]) == 0
    
    def test_validate_child_input_sensitive_information(self, security_manager):
        """Test child input validation with sensitive information."""
        sensitive_inputs = [
            "My password is secret123",
            "Dad's credit card number is 1234 5678 9012 3456",
            "My SSN is 123-45-6789",
            "Our social security number is 987654321",
            "Email me at child@example.com",
            "Call me at 555-123-4567"
        ]
        
        for sensitive_input in sensitive_inputs:
            result = security_manager.validate_child_input(sensitive_input)
            
            assert result["is_safe"] is False
            assert len(result["blocked_content"]) > 0
            assert "sensitive information" in result["blocked_content"][0].lower()
    
    def test_validate_child_input_excessive_caps(self, security_manager):
        """Test detection of excessive capital letters."""
        caps_input = "I AM SHOUTING VERY LOUDLY!!!"
        result = security_manager.validate_child_input(caps_input)
        
        # Should be safe but have warning
        assert result["is_safe"] is True
        assert len(result["warnings"]) > 0
        assert "capital letters" in result["warnings"][0].lower()
    
    def test_validate_child_input_repetitive_content(self, security_manager):
        """Test detection of repetitive content."""
        repetitive_input = "aaaaaaaaaaaaaaaaaaaaaaaaa"
        result = security_manager.validate_child_input(repetitive_input)
        
        # Should be safe but have warning
        assert result["is_safe"] is True
        assert len(result["warnings"]) > 0
        assert "repetitive" in result["warnings"][0].lower()
    
    def test_validate_child_input_empty_content(self, security_manager):
        """Test validation of empty content."""
        result = security_manager.validate_child_input("")
        
        assert result["is_safe"] is True
        assert result["sanitized_input"] == ""
        assert len(result["blocked_content"]) == 0
        assert len(result["warnings"]) == 0
    
    def test_validate_child_input_error_handling(self, security_manager):
        """Test child input validation error handling."""
        # Mock an error in the validation process
        with patch.object(security_manager, 'sanitize_input', side_effect=Exception("Validation error")):
            result = security_manager.validate_child_input("test input")
            
            assert result["is_safe"] is False
            assert len(result["blocked_content"]) > 0
            assert "validation error" in result["blocked_content"][0].lower()
    
    def test_multiple_ip_rate_limiting(self, security_manager):
        """Test rate limiting with multiple IP addresses."""
        ip_addresses = ["192.168.1.1", "192.168.1.2", "192.168.1.3"]
        
        # Each IP should have independent rate limiting
        for ip in ip_addresses:
            for _ in range(50):  # Within limit
                assert security_manager.check_rate_limit(ip) is True
        
        # Check that all IPs are tracked separately
        assert len(security_manager.rate_limit_storage) == 3
        for ip in ip_addresses:
            assert len(security_manager.rate_limit_storage[ip]) == 50
    
    def test_rate_limit_storage_cleanup(self, security_manager):
        """Test that old rate limit entries are cleaned up."""
        ip_address = "192.168.1.200"
        
        with patch('time.time') as mock_time:
            # Start at time 0
            mock_time.return_value = 0
            
            # Make some requests
            for _ in range(10):
                security_manager.check_rate_limit(ip_address)
            
            assert len(security_manager.rate_limit_storage[ip_address]) == 10
            
            # Advance time beyond window
            mock_time.return_value = security_manager.rate_limit_window + 1
            
            # Make one more request (should trigger cleanup)
            security_manager.check_rate_limit(ip_address)
            
            # Should only have the new request
            assert len(security_manager.rate_limit_storage[ip_address]) == 1
    
    def test_concurrent_rate_limiting(self, security_manager):
        """Test rate limiting under concurrent access."""
        import threading
        import time
        
        ip_address = "192.168.1.201"
        results = []
        
        def make_request():
            result = security_manager.check_rate_limit(ip_address)
            results.append(result)
        
        # Create multiple threads making requests
        threads = []
        for _ in range(50):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All should succeed (within rate limit)
        assert len(results) == 50
        assert all(results)
        assert len(security_manager.rate_limit_storage[ip_address]) == 50
    
    def test_comprehensive_input_sanitization(self, security_manager):
        """Test comprehensive input sanitization with complex input."""
        complex_input = """
        <script>alert('xss')</script>
        '; DROP TABLE users; --
        javascript:alert(1)
        My password is secret123
        <img onload="malicious()">
        UNION SELECT * FROM admin
        \x00\x01\x02control chars
        """
        
        result = security_manager.sanitize_input(complex_input)
        
        # Should remove all malicious content
        assert "<script>" not in result.lower()
        assert "drop table" not in result.lower()
        assert "javascript:" not in result.lower()
        assert "onload=" not in result.lower()
        assert "union select" not in result.lower()
        assert "\x00" not in result
        assert "\x01" not in result
        assert "\x02" not in result
    
    def test_child_input_validation_comprehensive(self, security_manager):
        """Test comprehensive child input validation."""
        test_cases = [
            {
                "input": "I love playing games!",
                "expected_safe": True,
                "expected_warnings": 0,
                "expected_blocked": 0
            },
            {
                "input": "MY PASSWORD IS SECRET123!!!",
                "expected_safe": False,
                "expected_warnings": 1,  # Caps warning
                "expected_blocked": 1    # Password detected
            },
            {
                "input": "aaaaaaaaaaaaaaaaaaaaaa",
                "expected_safe": True,
                "expected_warnings": 1,  # Repetitive warning
                "expected_blocked": 0
            },
            {
                "input": "Call me at 555-123-4567",
                "expected_safe": False,
                "expected_warnings": 0,
                "expected_blocked": 1    # Phone number detected
            }
        ]
        
        for case in test_cases:
            result = security_manager.validate_child_input(case["input"])
            
            assert result["is_safe"] == case["expected_safe"], \
                f"Safety check failed for: {case['input']}"
            assert len(result["warnings"]) == case["expected_warnings"], \
                f"Warning count mismatch for: {case['input']}"
            assert len(result["blocked_content"]) == case["expected_blocked"], \
                f"Blocked content count mismatch for: {case['input']}"
    
    def test_security_logging_behavior(self, security_manager):
        """Test that security events are properly logged."""
        with patch('src.infrastructure.security.api_security_manager.logger') as mock_logger:
            ip_address = "192.168.1.250"
            
            # Test rate limiting logging
            security_manager.check_rate_limit(ip_address)
            mock_logger.debug.assert_called()
            
            # Test IP blocking logging
            security_manager.block_ip(ip_address)
            mock_logger.warning.assert_called()
            
            # Test input sanitization logging
            security_manager.sanitize_input("test input")
            mock_logger.debug.assert_called()
    
    def test_edge_cases_special_characters(self, security_manager):
        """Test handling of special characters and Unicode."""
        special_inputs = [
            "emoji test 🎮🧸",
            "unicode test áéíóú",
            "symbols test !@#$%^&*()",
            "mixed test Hello世界",
            "newlines\nand\ttabs",
            "quotes 'single' \"double\"",
        ]
        
        for special_input in special_inputs:
            # Should not crash on special characters
            result = security_manager.sanitize_input(special_input)
            assert isinstance(result, str)
            
            # Should handle in child validation
            child_result = security_manager.validate_child_input(special_input)
            assert isinstance(child_result, dict)
            assert "is_safe" in child_result
    
    def test_performance_large_input(self, security_manager):
        """Test performance with large input."""
        # Create large input (within limits)
        large_input = "A" * 900  # Just under max_input_length
        
        start_time = time.time()
        result = security_manager.sanitize_input(large_input)
        end_time = time.time()
        
        # Should complete quickly (under 1 second)
        assert (end_time - start_time) < 1.0
        assert len(result) == 900
        
        # Test child validation performance
        start_time = time.time()
        child_result = security_manager.validate_child_input(large_input)
        end_time = time.time()
        
        assert (end_time - start_time) < 1.0
        assert child_result["is_safe"] is True