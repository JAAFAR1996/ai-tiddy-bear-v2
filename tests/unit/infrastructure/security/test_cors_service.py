"""
Tests for CORS Security Service
Testing CORS policies, origin validation, and security headers.
"""

import pytest
from unittest.mock import patch, Mock, MagicMock
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Union
import urllib.parse
import re

from src.infrastructure.security.cors_service import (
    CORSSecurityService,
    CORSPolicy,
    CORSConfiguration,
)


class TestCORSPolicy:
    """Test the CORSPolicy enum."""

    def test_cors_policy_values(self):
        """Test CORS policy enumeration values."""
        assert CORSPolicy.STRICT.value == "strict"
        assert CORSPolicy.MODERATE.value == "moderate"
        assert CORSPolicy.PERMISSIVE.value == "permissive"

    def test_cors_policy_coverage(self):
        """Test all CORS policy levels are defined."""
        policies = [policy.value for policy in CORSPolicy]
        expected_policies = ["strict", "moderate", "permissive"]
        assert sorted(policies) == sorted(expected_policies)


class TestCORSConfiguration:
    """Test the CORSConfiguration dataclass."""

    def test_cors_configuration_creation(self):
        """Test CORSConfiguration creation with all fields."""
        config = CORSConfiguration(
            allowed_origins={"https://example.com"},
            allowed_methods={"GET", "POST"},
            allowed_headers={"Content-Type", "Authorization"},
            expose_headers={"X-Total-Count"},
            allow_credentials=True,
            max_age=3600,
            policy_level=CORSPolicy.STRICT,
        )

        assert config.allowed_origins == {"https://example.com"}
        assert config.allowed_methods == {"GET", "POST"}
        assert config.allowed_headers == {"Content-Type", "Authorization"}
        assert config.expose_headers == {"X-Total-Count"}
        assert config.allow_credentials is True
        assert config.max_age == 3600
        assert config.policy_level == CORSPolicy.STRICT

    def test_cors_configuration_validation_valid(self):
        """Test CORSConfiguration validation with valid settings."""
        config = CORSConfiguration(
            allowed_origins={"https://example.com"},
            allowed_methods={"GET", "POST"},
            allowed_headers={"Content-Type"},
            expose_headers={"X-Total-Count"},
            allow_credentials=True,
            max_age=3600,
            policy_level=CORSPolicy.STRICT,
        )
        # Should not raise any exception
        assert config.allowed_origins == {"https://example.com"}

    def test_cors_configuration_validation_invalid_wildcard_with_credentials(
            self):
        """Test CORSConfiguration validation fails with wildcard and credentials."""
        with pytest.raises(
            ValueError, match="Cannot allow credentials with wildcard origins"
        ):
            CORSConfiguration(
                allowed_origins={"*"},
                allowed_methods={"GET", "POST"},
                allowed_headers={"Content-Type"},
                expose_headers={"X-Total-Count"},
                allow_credentials=True,
                max_age=3600,
                policy_level=CORSPolicy.STRICT,
            )

    def test_cors_configuration_wildcard_without_credentials(self):
        """Test CORSConfiguration allows wildcard without credentials."""
        config = CORSConfiguration(
            allowed_origins={"*"},
            allowed_methods={"GET", "POST"},
            allowed_headers={"Content-Type"},
            expose_headers={"X-Total-Count"},
            allow_credentials=False,
            max_age=3600,
            policy_level=CORSPolicy.PERMISSIVE,
        )
        assert config.allowed_origins == {"*"}
        assert config.allow_credentials is False


class TestCORSSecurityService:
    """Test the CORSSecurityService class."""

    @pytest.fixture
    def cors_service(self):
        """Create a CORSSecurityService instance."""
        return CORSSecurityService()

    @pytest.fixture
    def cors_service_moderate(self):
        """Create a CORSSecurityService with moderate policy."""
        return CORSSecurityService(default_policy=CORSPolicy.MODERATE)

    @pytest.fixture
    def cors_service_permissive(self):
        """Create a CORSSecurityService with permissive policy."""
        return CORSSecurityService(default_policy=CORSPolicy.PERMISSIVE)

    def test_cors_service_initialization(self, cors_service):
        """Test CORSSecurityService initialization."""
        assert cors_service.default_policy == CORSPolicy.STRICT
        assert len(cors_service.configurations) == 3
        assert cors_service.origin_cache == {}
        assert cors_service.violation_count == {}
        assert cors_service.max_cache_size == 1000

    def test_cors_service_initialization_with_policy(
            self, cors_service_moderate):
        """Test CORSSecurityService initialization with custom policy."""
        assert cors_service_moderate.default_policy == CORSPolicy.MODERATE
        assert len(cors_service_moderate.configurations) == 3

    def test_cors_configurations_initialization(self, cors_service):
        """Test that CORS configurations are properly initialized."""
        configs = cors_service.configurations

        # Check all policies are present
        assert CORSPolicy.STRICT in configs
        assert CORSPolicy.MODERATE in configs
        assert CORSPolicy.PERMISSIVE in configs

        # Check strict policy configuration
        strict_config = configs[CORSPolicy.STRICT]
        assert "https://ai-teddy.com" in strict_config.allowed_origins
        assert "GET" in strict_config.allowed_methods
        assert "POST" in strict_config.allowed_methods
        assert "Content-Type" in strict_config.allowed_headers
        assert strict_config.allow_credentials is True
        assert strict_config.max_age == 300

        # Check moderate policy configuration
        moderate_config = configs[CORSPolicy.MODERATE]
        assert "https://localhost:3000" in moderate_config.allowed_origins
        assert "DELETE" in moderate_config.allowed_methods
        assert moderate_config.max_age == 3600

        # Check permissive policy configuration
        permissive_config = configs[CORSPolicy.PERMISSIVE]
        assert "http://localhost:3000" in permissive_config.allowed_origins
        assert "PATCH" in permissive_config.allowed_methods
        assert permissive_config.max_age == 86400

    def test_validate_origin_missing_origin(self, cors_service):
        """Test origin validation with missing origin."""
        result = cors_service.validate_origin(None)

        assert result["allowed"] is False
        assert result["reason"] == "Missing origin header"
        assert "headers" in result
        assert result["headers"]["Access-Control-Allow-Origin"] == ""

    def test_validate_origin_empty_origin(self, cors_service):
        """Test origin validation with empty origin."""
        result = cors_service.validate_origin("")

        assert result["allowed"] is False
        assert result["reason"] == "Missing origin header"

    def test_validate_origin_allowed_strict(self, cors_service):
        """Test origin validation with allowed origin in strict policy."""
        result = cors_service.validate_origin("https://ai-teddy.com")

        assert result["allowed"] is True
        assert result["origin"] == "https://ai-teddy.com"
        assert "headers" in result
        assert (
            result["headers"]["Access-Control-Allow-Origin"] == "https://ai-teddy.com"
        )
        assert result["policy"] == "strict"

    def test_validate_origin_not_allowed_strict(self, cors_service):
        """Test origin validation with disallowed origin in strict policy."""
        result = cors_service.validate_origin("https://malicious.com")

        assert result["allowed"] is False
        assert result["reason"] == "Origin not allowed"
        assert result["headers"]["Access-Control-Allow-Origin"] == ""

    def test_validate_origin_allowed_moderate(self, cors_service_moderate):
        """Test origin validation with allowed origin in moderate policy."""
        result = cors_service_moderate.validate_origin(
            "https://localhost:3000")

        assert result["allowed"] is True
        assert result["origin"] == "https://localhost:3000"
        assert result["policy"] == "moderate"

    def test_validate_origin_allowed_permissive(self, cors_service_permissive):
        """Test origin validation with allowed origin in permissive policy."""
        result = cors_service_permissive.validate_origin(
            "http://localhost:3000")

        assert result["allowed"] is True
        assert result["origin"] == "http://localhost:3000"
        assert result["policy"] == "permissive"

    def test_validate_origin_with_custom_policy(self, cors_service):
        """Test origin validation with custom policy parameter."""
        result = cors_service.validate_origin(
            "https://localhost:3000", policy=CORSPolicy.MODERATE
        )

        assert result["allowed"] is True
        assert result["policy"] == "moderate"

    def test_validate_origin_caching(self, cors_service):
        """Test origin validation caching mechanism."""
        # First call should not be cached
        result1 = cors_service.validate_origin("https://ai-teddy.com")
        assert result1["allowed"] is True
        assert "cached" not in result1

        # Second call should be cached
        result2 = cors_service.validate_origin("https://ai-teddy.com")
        assert result2["allowed"] is True
        assert result2["cached"] is True

    def test_validate_origin_security_invalid_format(self, cors_service):
        """Test origin validation with invalid format."""
        result = cors_service.validate_origin("not-a-valid-url")

        assert result["allowed"] is False
        assert "security_violation" in result
        assert result["security_violation"] is True

    def test_validate_origin_security_http_non_localhost(self, cors_service):
        """Test origin validation blocks HTTP for non-localhost."""
        result = cors_service.validate_origin("http://example.com")

        assert result["allowed"] is False
        assert "security_violation" in result
        assert result["security_violation"] is True

    def test_validate_origin_security_suspicious_chars(self, cors_service):
        """Test origin validation with suspicious characters."""
        result = cors_service.validate_origin("https://example.com<script>")

        assert result["allowed"] is False
        assert "security_violation" in result
        assert result["security_violation"] is True

    def test_validate_origin_security_localhost_http_allowed(
            self, cors_service):
        """Test origin validation allows HTTP for localhost."""
        with patch.object(cors_service, "_is_origin_allowed", return_value=True):
            result = cors_service.validate_origin("http://localhost:3000")

            # Should pass security validation
            assert result["allowed"] is True

    def test_handle_preflight_request_valid(self, cors_service):
        """Test preflight request handling with valid parameters."""
        result = cors_service.handle_preflight_request(
            origin="https://ai-teddy.com",
            method="POST",
            headers="Content-Type, Authorization",
        )

        assert result["allowed"] is True
        assert result["origin"] == "https://ai-teddy.com"
        assert result["method"] == "POST"
        assert "headers" in result
        assert result["policy"] == "strict"

    def test_handle_preflight_request_invalid_origin(self, cors_service):
        """Test preflight request handling with invalid origin."""
        result = cors_service.handle_preflight_request(
            origin="https://malicious.com", method="POST", headers="Content-Type"
        )

        assert result["allowed"] is False
        assert result["reason"] == "Origin not allowed"

    def test_handle_preflight_request_invalid_method(self, cors_service):
        """Test preflight request handling with invalid method."""
        result = cors_service.handle_preflight_request(
            origin="https://ai-teddy.com",
            method="PATCH",  # Not allowed in strict policy
            headers="Content-Type",
        )

        assert result["allowed"] is False
        assert "Method PATCH not allowed" in result["reason"]

    def test_handle_preflight_request_invalid_headers(self, cors_service):
        """Test preflight request handling with invalid headers."""
        result = cors_service.handle_preflight_request(
            origin="https://ai-teddy.com",
            method="POST",
            headers="Content-Type, X-Custom-Header",  # X-Custom-Header not allowed
        )

        assert result["allowed"] is False
        assert "Headers not allowed" in result["reason"]

    def test_handle_preflight_request_no_method(self, cors_service):
        """Test preflight request handling without method."""
        result = cors_service.handle_preflight_request(
            origin="https://ai-teddy.com", method=None, headers="Content-Type"
        )

        # Method validation should pass if None
        assert result["allowed"] is True

    def test_handle_preflight_request_no_headers(self, cors_service):
        """Test preflight request handling without headers."""
        result = cors_service.handle_preflight_request(
            origin="https://ai-teddy.com", method="POST", headers=None
        )

        # Headers validation should pass if None
        assert result["allowed"] is True

    def test_get_security_headers_strict(self, cors_service):
        """Test security headers for strict policy."""
        headers = cors_service.get_security_headers(CORSPolicy.STRICT)

        assert "X-Content-Type-Options" in headers
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert "X-Frame-Options" in headers
        assert headers["X-Frame-Options"] == "DENY"
        assert "X-XSS-Protection" in headers
        assert "Referrer-Policy" in headers
        assert "Content-Security-Policy" in headers
        assert "Strict-Transport-Security" in headers
        assert "X-Child-Safety" in headers
        assert headers["X-Child-Safety"] == "enabled"

    def test_get_security_headers_moderate(self, cors_service):
        """Test security headers for moderate policy."""
        headers = cors_service.get_security_headers(CORSPolicy.MODERATE)

        assert "X-Content-Type-Options" in headers
        assert "X-Frame-Options" in headers
        assert "Content-Security-Policy" in headers
        assert "X-Child-Safety" not in headers  # Only for strict
        assert "Strict-Transport-Security" not in headers  # Only for strict

    def test_get_security_headers_permissive(self, cors_service):
        """Test security headers for permissive policy."""
        headers = cors_service.get_security_headers(CORSPolicy.PERMISSIVE)

        assert "X-Content-Type-Options" in headers
        assert "X-Frame-Options" in headers
        assert "Content-Security-Policy" in headers
        assert "X-Child-Safety" not in headers
        assert "Strict-Transport-Security" not in headers

    def test_get_security_headers_default_policy(self, cors_service):
        """Test security headers with default policy."""
        headers = cors_service.get_security_headers()

        # Should use default policy (STRICT)
        assert "X-Child-Safety" in headers
        assert "Strict-Transport-Security" in headers

    def test_validate_origin_security_valid_https(self, cors_service):
        """Test origin security validation with valid HTTPS."""
        result = cors_service._validate_origin_security("https://example.com")

        assert result["secure"] is True

    def test_validate_origin_security_valid_localhost_http(self, cors_service):
        """Test origin security validation with localhost HTTP."""
        result = cors_service._validate_origin_security(
            "http://localhost:3000")

        assert result["secure"] is True

    def test_validate_origin_security_invalid_scheme(self, cors_service):
        """Test origin security validation with invalid scheme."""
        result = cors_service._validate_origin_security("ftp://example.com")

        assert result["secure"] is False
        assert result["reason"] == "Invalid scheme"

    def test_validate_origin_security_invalid_format(self, cors_service):
        """Test origin security validation with invalid format."""
        result = cors_service._validate_origin_security("not-a-url")

        assert result["secure"] is False
        assert result["reason"] == "Invalid origin format"

    def test_validate_origin_security_suspicious_chars(self, cors_service):
        """Test origin security validation with suspicious characters."""
        result = cors_service._validate_origin_security(
            "https://example.com<script>")

        assert result["secure"] is False
        assert result["reason"] == "Suspicious characters in origin"

    def test_validate_origin_security_invalid_domain(self, cors_service):
        """Test origin security validation with invalid domain."""
        result = cors_service._validate_origin_security("https://exam@ple.com")

        assert result["secure"] is False
        assert result["reason"] == "Invalid domain format"

    def test_validate_origin_security_exception_handling(self, cors_service):
        """Test origin security validation exception handling."""
        with patch("urllib.parse.urlparse", side_effect=Exception("Parse error")):
            result = cors_service._validate_origin_security(
                "https://example.com")

            assert result["secure"] is False
            assert result["reason"] == "Origin validation error"

    def test_is_origin_allowed_exact_match(self, cors_service):
        """Test origin allowed check with exact match."""
        config = cors_service.configurations[CORSPolicy.STRICT]
        result = cors_service._is_origin_allowed(
            "https://ai-teddy.com", config)

        assert result is True

    def test_is_origin_allowed_not_in_list(self, cors_service):
        """Test origin allowed check with origin not in list."""
        config = cors_service.configurations[CORSPolicy.STRICT]
        result = cors_service._is_origin_allowed(
            "https://malicious.com", config)

        assert result is False

    def test_is_origin_allowed_wildcard_subdomain(self, cors_service):
        """Test origin allowed check with wildcard subdomain."""
        config = cors_service.configurations[CORSPolicy.STRICT]
        config.allowed_origins.add("*.example.com")

        result1 = cors_service._is_origin_allowed(
            "https://sub.example.com", config)
        result2 = cors_service._is_origin_allowed(
            "https://example.com", config)
        result3 = cors_service._is_origin_allowed(
            "https://malicious.com", config)

        assert result1 is True
        assert result2 is True
        assert result3 is False

    def test_generate_cors_headers(self, cors_service):
        """Test CORS headers generation."""
        config = cors_service.configurations[CORSPolicy.STRICT]
        headers = cors_service._generate_cors_headers(
            "https://ai-teddy.com", config)

        assert headers["Access-Control-Allow-Origin"] == "https://ai-teddy.com"
        assert "Access-Control-Allow-Methods" in headers
        assert "Access-Control-Allow-Headers" in headers
        assert "Access-Control-Max-Age" in headers
        assert headers["Access-Control-Max-Age"] == "300"
        assert "Access-Control-Expose-Headers" in headers
        assert headers["Access-Control-Allow-Credentials"] == "true"

    def test_generate_cors_headers_no_credentials(self, cors_service):
        """Test CORS headers generation without credentials."""
        config = cors_service.configurations[CORSPolicy.STRICT]
        config.allow_credentials = False
        headers = cors_service._generate_cors_headers(
            "https://ai-teddy.com", config)

        assert "Access-Control-Allow-Credentials" not in headers

    def test_generate_cors_headers_no_expose_headers(self, cors_service):
        """Test CORS headers generation without expose headers."""
        config = cors_service.configurations[CORSPolicy.STRICT]
        config.expose_headers = set()
        headers = cors_service._generate_cors_headers(
            "https://ai-teddy.com", config)

        assert "Access-Control-Expose-Headers" not in headers

    def test_generate_preflight_headers(self, cors_service):
        """Test preflight headers generation."""
        config = cors_service.configurations[CORSPolicy.STRICT]
        headers = cors_service._generate_preflight_headers(
            "https://ai-teddy.com", config
        )

        assert "Access-Control-Allow-Origin" in headers
        assert "Vary" in headers
        assert "Cache-Control" in headers
        assert (
            headers["Vary"]
            == "Origin, Access-Control-Request-Method, Access-Control-Request-Headers"
        )
        assert headers["Cache-Control"] == "max-age=300"

    def test_get_cors_headers_for_error(self, cors_service):
        """Test error CORS headers generation."""
        headers = cors_service._get_cors_headers_for_error()

        assert headers["Access-Control-Allow-Origin"] == ""
        assert headers["Access-Control-Allow-Methods"] == ""
        assert headers["Access-Control-Allow-Headers"] == ""
        assert headers["Vary"] == "Origin"

    def test_get_csp_header_strict(self, cors_service):
        """Test CSP header for strict policy."""
        csp = cors_service._get_csp_header(CORSPolicy.STRICT)

        assert "default-src 'self'" in csp
        assert "frame-ancestors 'none'" in csp
        assert "connect-src 'self'" in csp

    def test_get_csp_header_moderate(self, cors_service):
        """Test CSP header for moderate policy."""
        csp = cors_service._get_csp_header(CORSPolicy.MODERATE)

        assert "default-src 'self'" in csp
        assert "connect-src 'self' https:" in csp
        assert "frame-ancestors 'none'" not in csp

    def test_get_csp_header_permissive(self, cors_service):
        """Test CSP header for permissive policy."""
        csp = cors_service._get_csp_header(CORSPolicy.PERMISSIVE)

        assert "default-src 'self'" in csp
        assert "connect-src 'self' https: http: ws: wss:" in csp
        assert "img-src 'self' data: https: http:" in csp

    def test_log_cors_violation(self, cors_service):
        """Test CORS violation logging."""
        with patch("src.infrastructure.security.cors_service.logger") as mock_logger:
            cors_service._log_cors_violation(
                "https://malicious.com", "Origin not allowed"
            )

            mock_logger.warning.assert_called_once()
            assert cors_service.violation_count["https://malicious.com"] == 1

    def test_log_cors_violation_repeated(self, cors_service):
        """Test repeated CORS violation logging."""
        with patch("src.infrastructure.security.cors_service.logger") as mock_logger:
            origin = "https://malicious.com"

            # Log 5 violations
            for i in range(5):
                cors_service._log_cors_violation(origin, "Origin not allowed")

            assert cors_service.violation_count[origin] == 5
            mock_logger.error.assert_called_once()

            error_call = mock_logger.error.call_args[0][0]
            assert "Repeated CORS violations" in error_call
            assert "possible attack" in error_call

    def test_update_origin_cache(self, cors_service):
        """Test origin cache update."""
        cors_service._update_origin_cache("https://example.com:strict", True)

        assert cors_service.origin_cache["https://example.com:strict"] is True

    def test_update_origin_cache_size_limit(self, cors_service):
        """Test origin cache size limit."""
        cors_service.max_cache_size = 5

        # Fill cache beyond limit
        for i in range(10):
            cors_service._update_origin_cache(
                f"https://example{i}.com:strict", True)

        assert len(cors_service.origin_cache) <= 5

    def test_get_cors_statistics(self, cors_service):
        """Test CORS statistics retrieval."""
        # Add some test data
        cors_service.origin_cache["test1"] = True
        cors_service.origin_cache["test2"] = True
        cors_service.violation_count["malicious1.com"] = 5
        cors_service.violation_count["malicious2.com"] = 3

        stats = cors_service.get_cors_statistics()

        assert stats["default_policy"] == "strict"
        assert stats["cached_origins"] == 2
        assert stats["violation_count"] == 8
        assert stats["unique_violating_origins"] == 2
        assert len(stats["top_violating_origins"]) == 2
        assert stats["top_violating_origins"][0] == ("malicious1.com", 5)

    def test_add_allowed_origin_valid(self, cors_service):
        """Test adding valid origin to policy."""
        result = cors_service.add_allowed_origin(
            "https://newdomain.com", CORSPolicy.STRICT
        )

        assert result is True
        assert (
            "https://newdomain.com"
            in cors_service.configurations[CORSPolicy.STRICT].allowed_origins
        )

    def test_add_allowed_origin_invalid_security(self, cors_service):
        """Test adding invalid origin fails."""
        result = cors_service.add_allowed_origin(
            "http://malicious.com", CORSPolicy.STRICT
        )

        assert result is False
        assert (
            "http://malicious.com"
            not in cors_service.configurations[CORSPolicy.STRICT].allowed_origins
        )

    def test_add_allowed_origin_clears_cache(self, cors_service):
        """Test adding origin clears related cache entries."""
        origin = "https://newdomain.com"
        cache_key = f"{origin}:strict"

        # Add cache entry
        cors_service.origin_cache[cache_key] = False

        # Add origin
        cors_service.add_allowed_origin(origin, CORSPolicy.STRICT)

        # Cache should be cleared
        assert cache_key not in cors_service.origin_cache

    def test_add_allowed_origin_exception_handling(self, cors_service):
        """Test adding origin with exception handling."""
        with patch.object(
            cors_service,
            "_validate_origin_security",
            side_effect=Exception("Test error"),
        ):
            result = cors_service.add_allowed_origin(
                "https://example.com", CORSPolicy.STRICT
            )

            assert result is False

    def test_remove_allowed_origin(self, cors_service):
        """Test removing allowed origin from policy."""
        origin = "https://ai-teddy.com"

        # Verify origin is initially present
        assert origin in cors_service.configurations[CORSPolicy.STRICT].allowed_origins

        result = cors_service.remove_allowed_origin(origin, CORSPolicy.STRICT)

        assert result is True
        assert (
            origin not in cors_service.configurations[CORSPolicy.STRICT].allowed_origins
        )

    def test_remove_allowed_origin_clears_cache(self, cors_service):
        """Test removing origin clears related cache entries."""
        origin = "https://ai-teddy.com"
        cache_key = f"{origin}:strict"

        # Add cache entry
        cors_service.origin_cache[cache_key] = True

        # Remove origin
        cors_service.remove_allowed_origin(origin, CORSPolicy.STRICT)

        # Cache should be cleared
        assert cache_key not in cors_service.origin_cache

    def test_remove_allowed_origin_nonexistent(self, cors_service):
        """Test removing non-existent origin."""
        origin = "https://nonexistent.com"

        result = cors_service.remove_allowed_origin(origin, CORSPolicy.STRICT)

        assert result is True  # Should succeed even if origin not present

    def test_remove_allowed_origin_exception_handling(self, cors_service):
        """Test removing origin with exception handling."""
        with patch.object(
            cors_service.configurations[CORSPolicy.STRICT],
            "allowed_origins",
            side_effect=Exception("Test error"),
        ):
            result = cors_service.remove_allowed_origin(
                "https://example.com", CORSPolicy.STRICT
            )

            assert result is False


class TestCORSServiceIntegration:
    """Integration tests for CORS service."""

    @pytest.fixture
    def cors_service(self):
        """Create a CORSSecurityService instance."""
        return CORSSecurityService()

    def test_full_cors_flow_allowed(self, cors_service):
        """Test complete CORS flow for allowed origin."""
        # First validate origin
        validation_result = cors_service.validate_origin(
            "https://ai-teddy.com")
        assert validation_result["allowed"] is True

        # Then handle preflight
        preflight_result = cors_service.handle_preflight_request(
            origin="https://ai-teddy.com",
            method="POST",
            headers="Content-Type, Authorization",
        )
        assert preflight_result["allowed"] is True

        # Get security headers
        security_headers = cors_service.get_security_headers()
        assert "X-Child-Safety" in security_headers

    def test_full_cors_flow_blocked(self, cors_service):
        """Test complete CORS flow for blocked origin."""
        # First validate origin
        validation_result = cors_service.validate_origin(
            "https://malicious.com")
        assert validation_result["allowed"] is False

        # Preflight should also be blocked
        preflight_result = cors_service.handle_preflight_request(
            origin="https://malicious.com", method="POST", headers="Content-Type"
        )
        assert preflight_result["allowed"] is False

    def test_cors_policy_escalation(self, cors_service):
        """Test CORS policy escalation from strict to permissive."""
        # Start with strict policy
        strict_result = cors_service.validate_origin("http://localhost:3000")
        assert strict_result["allowed"] is False

        # Try with moderate policy
        moderate_result = cors_service.validate_origin(
            "http://localhost:3000", policy=CORSPolicy.MODERATE
        )
        assert moderate_result["allowed"] is False

        # Try with permissive policy
        permissive_result = cors_service.validate_origin(
            "http://localhost:3000", policy=CORSPolicy.PERMISSIVE
        )
        assert permissive_result["allowed"] is True

    def test_cors_cache_behavior(self, cors_service):
        """Test CORS caching behavior across requests."""
        origin = "https://ai-teddy.com"

        # First request
        result1 = cors_service.validate_origin(origin)
        assert result1["allowed"] is True
        assert "cached" not in result1

        # Second request should be cached
        result2 = cors_service.validate_origin(origin)
        assert result2["allowed"] is True
        assert result2["cached"] is True

        # Different policy should not be cached
        result3 = cors_service.validate_origin(
            origin, policy=CORSPolicy.MODERATE)
        assert result3["allowed"] is True
        assert "cached" not in result3

    def test_cors_violation_tracking(self, cors_service):
        """Test CORS violation tracking and statistics."""
        malicious_origin = "https://malicious.com"

        # Generate violations
        for i in range(3):
            cors_service.validate_origin(malicious_origin)

        # Check statistics
        stats = cors_service.get_cors_statistics()
        assert stats["violation_count"] == 3
        assert stats["unique_violating_origins"] == 1
        assert malicious_origin in [
            origin for origin, count in stats["top_violating_origins"]
        ]

    def test_cors_dynamic_origin_management(self, cors_service):
        """Test dynamic origin management."""
        new_origin = "https://newpartner.com"

        # Initially not allowed
        result1 = cors_service.validate_origin(new_origin)
        assert result1["allowed"] is False

        # Add origin
        add_result = cors_service.add_allowed_origin(
            new_origin, CORSPolicy.STRICT)
        assert add_result is True

        # Now should be allowed
        result2 = cors_service.validate_origin(new_origin)
        assert result2["allowed"] is True

        # Remove origin
        remove_result = cors_service.remove_allowed_origin(
            new_origin, CORSPolicy.STRICT
        )
        assert remove_result is True

        # Should not be allowed again
        result3 = cors_service.validate_origin(new_origin)
        assert result3["allowed"] is False

    def test_cors_security_headers_integration(self, cors_service):
        """Test CORS security headers integration."""
        # Test strict policy headers
        strict_headers = cors_service.get_security_headers(CORSPolicy.STRICT)
        assert "X-Child-Safety" in strict_headers
        assert "Strict-Transport-Security" in strict_headers

        # Test moderate policy headers
        moderate_headers = cors_service.get_security_headers(
            CORSPolicy.MODERATE)
        assert "X-Child-Safety" not in moderate_headers
        assert "Strict-Transport-Security" not in moderate_headers

        # Common headers should be present in all policies
        for headers in [strict_headers, moderate_headers]:
            assert "X-Content-Type-Options" in headers
            assert "X-Frame-Options" in headers
            assert "Content-Security-Policy" in headers

    def test_cors_edge_cases(self, cors_service):
        """Test CORS edge cases and error conditions."""
        # Test with None values
        none_result = cors_service.validate_origin(None)
        assert none_result["allowed"] is False

        # Test with empty string
        empty_result = cors_service.validate_origin("")
        assert empty_result["allowed"] is False

        # Test with malformed origins
        malformed_result = cors_service.validate_origin("not-a-url")
        assert malformed_result["allowed"] is False
        assert malformed_result["security_violation"] is True

        # Test preflight with malformed origin
        preflight_malformed = cors_service.handle_preflight_request(
            origin="not-a-url", method="POST", headers="Content-Type"
        )
        assert preflight_malformed["allowed"] is False
