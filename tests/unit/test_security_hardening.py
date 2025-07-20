"""Unit tests for security hardening components
Ensures all security measures are properly implemented and effective
"""

import time

import pytest

from src.infrastructure.security.hardening.csrf_protection import (
    CSRFConfig,
    CSRFProtection,
    CSRFTokenManager,
)
from src.infrastructure.security.hardening.input_validation import (
    InputSanitizer,
    InputValidationConfig,
)
from src.infrastructure.security.hardening.rate_limiter import (
    ChildSafetyRateLimiter,
    RateLimitConfig,
    RedisRateLimiter,
)
from src.infrastructure.security.hardening.security_headers import (
    SecurityHeadersConfig,
    SecurityHeadersMiddleware,
    SecurityValidator,
)


class TestRateLimiter:
    """Test rate limiting functionality"""

    @pytest.fixture
    def rate_limiter(self):
        config = RateLimitConfig(requests_per_minute=10, requests_per_hour=100)
        return RedisRateLimiter(config)

    @pytest.mark.asyncio
    async def test_rate_limit_within_limits(self, rate_limiter):
        """Test that requests within limits are allowed"""
        await rate_limiter.initialize()  # Use local cache fallback

        result = await rate_limiter.check_rate_limit("test_user")

        assert result.allowed is True
        assert result.remaining > 0
        assert result.reset_time > time.time()

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self, rate_limiter):
        """Test that requests exceeding limits are blocked"""
        await rate_limiter.initialize()  # Use local cache fallback

        # Make requests up to limit
        for i in range(10):
            result = await rate_limiter.check_rate_limit("test_user_exceed")
            if i < 9:
                assert result.allowed is True

        # Next request should be blocked
        result = await rate_limiter.check_rate_limit("test_user_exceed")
        assert result.allowed is False
        assert result.retry_after is not None

    @pytest.mark.asyncio
    async def test_child_safety_rate_limiter(self):
        """Test child-specific rate limiting"""
        child_limiter = ChildSafetyRateLimiter()
        await child_limiter.initialize()

        # Test voice input limits
        result = await child_limiter.check_child_interaction_limit(
            "child_123", "voice_input"
        )

        assert result.allowed is True

        # Test story request limits
        result = await child_limiter.check_child_interaction_limit(
            "child_123", "story_request"
        )

        assert result.allowed is True

    @pytest.mark.asyncio
    async def test_rate_limit_reset(self, rate_limiter):
        """Test rate limit reset functionality"""
        await rate_limiter.initialize()

        # Use up some requests
        for i in range(5):
            await rate_limiter.check_rate_limit("reset_test_user")

        # Reset limits
        success = await rate_limiter.reset_rate_limit("reset_test_user")
        assert success is True

        # Should be able to make requests again
        result = await rate_limiter.check_rate_limit("reset_test_user")
        assert result.allowed is True


class TestCSRFProtection:
    """Test CSRF protection functionality"""

    @pytest.fixture
    def csrf_config(self):
        return CSRFConfig(
            secret_key="test_secret_key_that_is_long_enough_for_security",
            token_lifetime=3600,
        )

    @pytest.fixture
    def csrf_protection(self, csrf_config):
        return CSRFProtection(csrf_config)

    def test_token_generation(self, csrf_protection):
        """Test CSRF token generation"""
        session_id = "test_session_123"
        user_id = "user_456"

        token = csrf_protection.token_manager.generate_token(session_id, user_id)

        assert token is not None
        assert len(token) > 20
        assert "." in token  # Should contain separators

    def test_token_validation_success(self, csrf_protection):
        """Test successful CSRF token validation"""
        session_id = "test_session_123"
        user_id = "user_456"

        # Generate token
        token = csrf_protection.token_manager.generate_token(session_id, user_id)

        # Validate token
        is_valid = csrf_protection.token_manager.validate_token(
            token, session_id, user_id
        )

        assert is_valid is True

    def test_token_validation_failure(self, csrf_protection):
        """Test CSRF token validation failure"""
        session_id = "test_session_123"
        user_id = "user_456"

        # Generate token for one session
        token = csrf_protection.token_manager.generate_token(session_id, user_id)

        # Try to validate with different session
        is_valid = csrf_protection.token_manager.validate_token(
            token, "different_session", user_id
        )

        assert is_valid is False

    def test_token_invalidation(self, csrf_protection):
        """Test CSRF token invalidation"""
        session_id = "test_session_123"

        # Generate token
        token = csrf_protection.token_manager.generate_token(session_id)

        # Validate it works
        assert csrf_protection.token_manager.validate_token(token, session_id) is True

        # Invalidate token
        success = csrf_protection.token_manager.invalidate_token(token)
        assert success is True

        # Should no longer be valid
        assert csrf_protection.token_manager.validate_token(token, session_id) is False

    def test_session_token_cleanup(self, csrf_protection):
        """Test session-based token cleanup"""
        session_id = "cleanup_session"

        # Generate multiple tokens for same session
        tokens = []
        for i in range(3):
            token = csrf_protection.token_manager.generate_token(
                session_id, f"user_{i}"
            )
            tokens.append(token)

        # Invalidate all tokens for session
        count = csrf_protection.token_manager.invalidate_session_tokens(session_id)
        assert count == 3

        # All tokens should be invalid
        for token in tokens:
            assert (
                csrf_protection.token_manager.validate_token(
                    token, session_id, "user_0"
                )
                is False
            )


class TestSecurityHeaders:
    """Test security headers functionality"""

    @pytest.fixture
    def security_config(self):
        return SecurityHeadersConfig(child_safety_mode=True, hsts_max_age=31536000)

    def test_security_headers_configuration(self, security_config):
        """Test security headers configuration"""
        middleware = SecurityHeadersMiddleware(None, security_config)

        static_headers = middleware.static_headers

        # Check essential security headers
        assert "Content-Security-Policy" in static_headers
        assert "Strict-Transport-Security" in static_headers
        assert "X-Frame-Options" in static_headers
        assert "X-Content-Type-Options" in static_headers

        # Check child safety headers
        assert "X-Child-Safe" in static_headers
        assert "X-COPPA-Compliant" in static_headers

    def test_security_validator(self, security_config):
        """Test security configuration validation"""
        validator = SecurityValidator(security_config)

        issues = validator.validate_configuration()
        score = validator.get_security_score()

        assert isinstance(issues, dict)
        assert "errors" in issues
        assert "warnings" in issues
        assert "recommendations" in issues
        assert isinstance(score, int)
        assert 0 <= score <= 100

    def test_child_safety_headers(self):
        """Test child safety specific headers"""
        config = SecurityHeadersConfig(child_safety_mode=True)
        middleware = SecurityHeadersMiddleware(None, config)

        child_headers = middleware._get_child_safety_headers()

        assert "X-Child-Safe" in child_headers
        assert "X-COPPA-Compliant" in child_headers
        assert "X-Content-Rating" in child_headers
        assert child_headers["X-Child-Safe"] == "1"

    def test_csp_configuration(self, security_config):
        """Test Content Security Policy configuration"""
        middleware = SecurityHeadersMiddleware(None, security_config)

        csp = middleware.static_headers["Content-Security-Policy"]

        # Check that child safety CSP directives are included
        assert "frame-ancestors 'none'" in csp
        assert "object-src 'none'" in csp
        assert "base-uri 'self'" in csp


class TestInputValidation:
    """Test input validation and sanitization"""

    @pytest.fixture
    def input_sanitizer(self):
        config = InputValidationConfig(
            max_string_length=1000,
            child_max_string_length=500,
            enable_profanity_filter=True,
        )
        return InputSanitizer(config)

    def test_string_sanitization_safe_input(self, input_sanitizer):
        """Test sanitization of safe input"""
        safe_text = "Hello, I want to hear a story about animals!"

        result = input_sanitizer.sanitize_string(safe_text, is_child_input=True)

        assert result["is_safe"] is True
        assert result["sanitized"] == safe_text
        assert len(result["violations"]) == 0

    def test_string_sanitization_unsafe_characters(self, input_sanitizer):
        """Test sanitization of input with unsafe characters"""
        unsafe_text = "Hello <script>alert('xss')</script>"

        result = input_sanitizer.sanitize_string(unsafe_text, is_child_input=True)

        assert result["is_safe"] is False
        assert len(result["violations"]) > 0
        assert "dangerous_pattern" in [v["type"] for v in result["violations"]]

    def test_string_sanitization_length_limit(self, input_sanitizer):
        """Test string length limit enforcement"""
        long_text = "a" * 600  # Exceeds child limit of 500

        result = input_sanitizer.sanitize_string(long_text, is_child_input=True)

        assert result["is_safe"] is False
        assert len(result["sanitized"]) == 500
        assert any(v["type"] == "length_exceeded" for v in result["violations"])

    def test_child_safe_characters(self, input_sanitizer):
        """Test child-safe character validation"""
        unsafe_child_text = "Hello @#$%^&* world!"

        result = input_sanitizer.sanitize_string(unsafe_child_text, is_child_input=True)

        assert result["is_safe"] is False
        assert any(v["type"] == "unsafe_characters" for v in result["violations"])
        # Unsafe characters should be removed
        assert "@#$%^&*" not in result["sanitized"]

    def test_sql_injection_detection(self, input_sanitizer):
        """Test SQL injection pattern detection"""
        sql_injection = "'; DROP TABLE users; --"

        result = input_sanitizer.sanitize_string(sql_injection)

        assert result["is_safe"] is False
        assert any(
            "sql" in v["message"].lower() or "command" in v["message"].lower()
            for v in result["violations"]
        )

    def test_personal_info_detection(self, input_sanitizer):
        """Test personal information detection"""
        email_text = "My email is test@example.com"

        result = input_sanitizer.sanitize_string(email_text, is_child_input=True)

        # Should detect email and either block or sanitize
        violations_and_warnings = result["violations"] + result["warnings"]
        assert any("email" in v["message"].lower() for v in violations_and_warnings)

    def test_json_sanitization(self, input_sanitizer):
        """Test JSON data sanitization"""
        test_data = {
            "child_name": "Alice",
            "message": "Hello world!",
            "unsafe_field": "<script>alert('xss')</script>",
            "nested": {"safe": "content", "unsafe": "javascript:alert(1)"},
        }

        result = input_sanitizer.sanitize_json(test_data, is_child_input=True)

        # Should sanitize unsafe content
        assert result["sanitized"]["child_name"] == "Alice"
        assert result["sanitized"]["message"] == "Hello world!"
        assert "<script>" not in str(result["sanitized"])

    def test_array_size_limits(self, input_sanitizer):
        """Test array size limit enforcement"""
        large_array = ["item"] * 150  # Exceeds child limit of 100

        result = input_sanitizer.sanitize_json(large_array, is_child_input=True)

        assert result["is_safe"] is False
        assert len(result["sanitized"]) == 100
        assert any(v["type"] == "array_size_exceeded" for v in result["violations"])

    def test_object_depth_limits(self, input_sanitizer):
        """Test object depth limit enforcement"""
        # Create deeply nested object
        deep_object = {"level": 1}
        current = deep_object
        for i in range(2, 15):  # Exceeds max depth of 10
            current["nested"] = {"level": i}
            current = current["nested"]

        result = input_sanitizer.sanitize_json(deep_object, is_child_input=True)

        assert result["is_safe"] is False
        assert any(v["type"] == "depth_exceeded" for v in result["violations"])


class TestSecurityIntegration:
    """Integration tests for security components"""

    @pytest.mark.asyncio
    async def test_child_request_security_pipeline(self):
        """Test complete security pipeline for child requests"""
        # Simulate a child request going through all security layers

        # 1. Rate limiting
        child_limiter = ChildSafetyRateLimiter()
        await child_limiter.initialize()

        rate_result = await child_limiter.check_child_interaction_limit(
            "child_123", "voice_input"
        )
        assert rate_result.allowed is True

        # 2. Input validation
        config = InputValidationConfig(child_max_string_length=500)
        sanitizer = InputSanitizer(config)

        child_message = "I want to hear a story about dragons!"
        validation_result = sanitizer.sanitize_string(
            child_message, is_child_input=True
        )
        assert validation_result["is_safe"] is True

        # 3. CSRF protection (for form submissions)
        csrf_config = CSRFConfig(
            secret_key="test_key_long_enough_for_security_requirements"
        )
        csrf_protection = CSRFProtection(csrf_config)

        session_id = "child_session_123"
        csrf_token = csrf_protection.token_manager.generate_token(session_id)
        assert csrf_token is not None

        # 4. Security headers
        security_config = SecurityHeadersConfig(child_safety_mode=True)
        middleware = SecurityHeadersMiddleware(None, security_config)

        headers = middleware.static_headers
        assert headers["X-Child-Safe"] == "1"
        assert headers["X-COPPA-Compliant"] == "1"

    def test_security_configuration_validation(self):
        """Test overall security configuration validation"""
        # Test that all security components can be configured together

        # Rate limiting config
        rate_config = RateLimitConfig(
            child_requests_per_minute=20, child_requests_per_hour=300
        )
        assert rate_config.child_requests_per_minute == 20

        # CSRF config
        csrf_config = CSRFConfig(
            secret_key="secure_key_for_csrf_protection_testing",
            require_https=True,
        )
        assert csrf_config.require_https is True

        # Security headers config
        headers_config = SecurityHeadersConfig(
            child_safety_mode=True, hsts_max_age=31536000
        )
        assert headers_config.child_safety_mode is True

        # Input validation config
        validation_config = InputValidationConfig(
            child_max_string_length=500, enable_profanity_filter=True
        )
        assert validation_config.enable_profanity_filter is True

    def test_error_handling_security(self):
        """Test that security components handle errors gracefully"""
        # Test input sanitizer with malformed data
        config = InputValidationConfig()
        sanitizer = InputSanitizer(config)

        # Should handle None input gracefully
        result = sanitizer.sanitize_string("", is_child_input=True)
        assert result["is_safe"] is True

        # Test CSRF with invalid token
        csrf_config = CSRFConfig(secret_key="test_key_for_error_handling_validation")
        csrf_manager = CSRFTokenManager(csrf_config)

        # Invalid token should return False, not raise exception
        is_valid = csrf_manager.validate_token("invalid_token", "session_123")
        assert is_valid is False
