"""Tests for Comprehensive Input Validation Middleware
Testing comprehensive input validation and security threat detection middleware.
"""

import json
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import Request, Response

from src.infrastructure.validation.comprehensive_validator import (
    ComprehensiveInputValidator as ImportedComprehensiveInputValidator,
)
from src.infrastructure.validation.comprehensive_validator import (
    InputValidationMiddleware as ImportedInputValidationMiddleware,
)
from src.infrastructure.validation.comprehensive_validator import (
    InputValidationResult as ImportedInputValidationResult,
)
from src.infrastructure.validation.comprehensive_validator import (
    SecurityThreat as ImportedSecurityThreat,
)
from src.infrastructure.validation.comprehensive_validator import (
    create_input_validation_middleware as imported_create_input_validation_middleware,
)
from src.infrastructure.validation.comprehensive_validator import (
    get_input_validator as imported_get_input_validator,
)
from src.infrastructure.validation.comprehensive_validator import (
    validate_child_message as imported_validate_child_message,
)
from src.infrastructure.validation.comprehensive_validator import (
    validate_user_input as imported_validate_user_input,
)
from src.infrastructure.security.input_validation.core import (
    InputValidationResult,
    SecurityThreat,
)
from src.infrastructure.security.input_validation.middleware import (
    InputValidationMiddleware,
    create_input_validation_middleware,
)
from src.infrastructure.security.input_validation.validator import (
    ComprehensiveInputValidator,
    get_input_validator,
    validate_child_message,
    validate_user_input,
)


class TestSecurityThreat:
    """Test the SecurityThreat class."""

    def test_security_threat_initialization(self):
        """Test SecurityThreat initialization."""
        threat = SecurityThreat(
            threat_type="sql_injection",
            severity="high",
            field="username",
            value="admin'; DROP TABLE users; --",
            description="SQL injection attempt detected",
        )

        assert threat.threat_type == "sql_injection"
        assert threat.severity == "high"
        assert threat.field == "username"
        assert threat.value == "admin'; DROP TABLE users; --"
        assert threat.description == "SQL injection attempt detected"
        assert isinstance(threat.detected_at, datetime)

    def test_security_threat_value_truncation(self):
        """Test that SecurityThreat truncates long values."""
        long_value = "a" * 200  # 200 characters
        threat = SecurityThreat(
            threat_type="xss",
            severity="medium",
            field="comment",
            value=long_value,
            description="XSS attempt",
        )

        assert len(threat.value) == 100  # Should be truncated to 100 chars
        assert threat.value == "a" * 100

    def test_security_threat_empty_value(self):
        """Test SecurityThreat with empty value."""
        threat = SecurityThreat(
            threat_type="empty_test",
            severity="low",
            field="test_field",
            value="",
            description="Empty value test",
        )

        assert threat.value == ""
        assert len(threat.value) == 0

    def test_security_threat_detection_time(self):
        """Test that detection time is set correctly."""
        with patch(
            "src.infrastructure.security.input_validation.core.datetime"
        ) as mock_dt:
            mock_dt.utcnow.return_value = datetime(2024, 1, 1, 12, 0, 0)

            threat = SecurityThreat("test", "low", "field", "value", "desc")

            assert threat.detected_at == datetime(2024, 1, 1, 12, 0, 0)


class TestInputValidationResult:
    """Test the InputValidationResult class."""

    def test_input_validation_result_initialization_basic(self):
        """Test basic InputValidationResult initialization."""
        result = InputValidationResult(is_valid=True)

        assert result.is_valid is True
        assert result.threats == []
        assert result.errors == []
        assert result.child_safety_violations == []
        assert result.has_critical_threats is False
        assert result.has_child_safety_issues is False

    def test_input_validation_result_with_threats(self):
        """Test InputValidationResult with threats."""
        threats = [
            SecurityThreat("sql_injection", "high", "field1", "value1", "desc1"),
            SecurityThreat("xss", "critical", "field2", "value2", "desc2"),
        ]

        result = InputValidationResult(
            is_valid=False,
            threats=threats,
            errors=["error1", "error2"],
            child_safety_violations=["inappropriate_content"],
        )

        assert result.is_valid is False
        assert len(result.threats) == 2
        assert len(result.errors) == 2
        assert len(result.child_safety_violations) == 1
        assert result.has_critical_threats is True
        assert result.has_child_safety_issues is True

    def test_input_validation_result_critical_threat_detection(self):
        """Test critical threat detection."""
        critical_threat = SecurityThreat(
            "command_injection",
            "critical",
            "cmd",
            "rm -rf /",
            "Critical threat",
        )
        high_threat = SecurityThreat(
            "path_traversal",
            "high",
            "path",
            "../../../etc/passwd",
            "High threat",
        )

        result = InputValidationResult(
            is_valid=False, threats=[critical_threat, high_threat]
        )

        assert result.has_critical_threats is True

    def test_input_validation_result_no_critical_threats(self):
        """Test when no critical threats are present."""
        medium_threat = SecurityThreat(
            "suspicious_input", "medium", "field", "value", "Medium threat"
        )
        low_threat = SecurityThreat(
            "minor_issue", "low", "field", "value", "Low threat"
        )

        result = InputValidationResult(
            is_valid=True, threats=[medium_threat, low_threat]
        )

        assert result.has_critical_threats is False

    def test_input_validation_result_child_safety_issues(self):
        """Test child safety issue detection."""
        result = InputValidationResult(
            is_valid=False,
            child_safety_violations=["profanity", "personal_info"],
        )

        assert result.has_child_safety_issues is True
        assert len(result.child_safety_violations) == 2

    def test_input_validation_result_no_child_safety_issues(self):
        """Test when no child safety issues are present."""
        result = InputValidationResult(is_valid=True)

        assert result.has_child_safety_issues is False
        assert len(result.child_safety_violations) == 0


class TestComprehensiveInputValidator:
    """Test the ComprehensiveInputValidator class."""

    @pytest.fixture
    def mock_audit_integration(self):
        """Create mock audit integration."""
        mock_audit = Mock()
        mock_audit.log_security_event = AsyncMock()

        with patch(
            "src.infrastructure.security.input_validation.validator.get_audit_integration",
            return_value=mock_audit,
        ):
            yield mock_audit

    @pytest.fixture
    def validator(self, mock_audit_integration):
        """Create a validator instance."""
        return ComprehensiveInputValidator()

    @pytest.mark.asyncio
    async def test_validate_input_clean_string(self, validator):
        """Test validation of clean string input."""
        result = await validator.validate_input("Hello, world!", "message")

        assert result.is_valid is True
        assert len(result.threats) == 0
        assert len(result.errors) == 0
        assert len(result.child_safety_violations) == 0

    @pytest.mark.asyncio
    async def test_validate_input_none_value(self, validator):
        """Test validation of None value."""
        result = await validator.validate_input(None, "field")

        assert result.is_valid is True
        assert len(result.threats) == 0
        assert len(result.errors) == 0
        assert len(result.child_safety_violations) == 0

    @pytest.mark.asyncio
    async def test_validate_input_empty_string(self, validator):
        """Test validation of empty string."""
        result = await validator.validate_input("", "field")

        assert result.is_valid is True
        assert len(result.threats) == 0
        assert len(result.errors) == 0
        assert len(result.child_safety_violations) == 0

    @pytest.mark.asyncio
    async def test_validate_input_dict_data(self, validator):
        """Test validation of dictionary data."""
        test_data = {"key": "value", "number": 42}

        result = await validator.validate_input(test_data, "json_field")

        assert result.is_valid is True
        assert len(result.threats) == 0

    @pytest.mark.asyncio
    async def test_validate_input_list_data(self, validator):
        """Test validation of list data."""
        test_data = ["item1", "item2", "item3"]

        result = await validator.validate_input(test_data, "list_field")

        assert result.is_valid is True
        assert len(result.threats) == 0

    @pytest.mark.asyncio
    async def test_validate_input_numeric_data(self, validator):
        """Test validation of numeric data."""
        test_cases = [42, 3.14, True, False]

        for test_data in test_cases:
            result = await validator.validate_input(test_data, "numeric_field")
            assert result.is_valid is True
            assert len(result.threats) == 0

    @pytest.mark.asyncio
    async def test_validate_input_oversized_input(self, validator):
        """Test validation of oversized input."""
        large_input = "a" * 200000  # 200KB

        result = await validator.validate_input(large_input, "large_field")

        assert result.is_valid is False
        assert len(result.threats) > 0

        # Check for oversized input threat
        oversized_threats = [
            t for t in result.threats if t.threat_type == "oversized_input"
        ]
        assert len(oversized_threats) == 1
        assert oversized_threats[0].severity == "high"

    @pytest.mark.asyncio
    async def test_validate_input_with_context(self, validator):
        """Test validation with context information."""
        context = {
            "user_id": "test_user",
            "endpoint": "/api/test",
            "is_child_endpoint": True,
        }

        result = await validator.validate_input("test input", "message", context)

        assert result.is_valid is True
        assert len(result.threats) == 0

    @pytest.mark.asyncio
    async def test_validate_input_exception_handling(self, validator):
        """Test validation exception handling."""
        # Mock threat detection to raise exception
        with patch.object(
            validator,
            "detect_sql_injection",
            side_effect=Exception("Detection error"),
        ):
            result = await validator.validate_input("test input", "field")

            assert result.is_valid is False
            assert len(result.errors) > 0
            assert "Validation failed" in result.errors[0]

    @pytest.mark.asyncio
    async def test_validate_input_mock_threat_detection(self, validator):
        """Test validation with mocked threat detection."""
        mock_threat = SecurityThreat(
            "sql_injection", "high", "field", "value", "SQL injection detected"
        )

        with patch.object(
            validator, "detect_sql_injection", return_value=[mock_threat]
        ):
            with patch.object(validator, "detect_xss", return_value=[]):
                with patch.object(validator, "detect_path_traversal", return_value=[]):
                    with patch.object(
                        validator, "detect_command_injection", return_value=[]
                    ):
                        with patch.object(
                            validator, "detect_ldap_injection", return_value=[]
                        ):
                            with patch.object(
                                validator,
                                "detect_template_injection",
                                return_value=[],
                            ):
                                with patch.object(
                                    validator,
                                    "detect_inappropriate_content",
                                    return_value=[],
                                ):
                                    with patch.object(
                                        validator,
                                        "detect_pii",
                                        return_value=[],
                                    ):
                                        with patch.object(
                                            validator,
                                            "detect_encoding_attacks",
                                            return_value=[],
                                        ):
                                            result = await validator.validate_input(
                                                "'; DROP TABLE users; --",
                                                "query",
                                            )

                                            assert result.is_valid is False
                                            assert len(result.threats) == 1
                                            assert (
                                                result.threats[0].threat_type
                                                == "sql_injection"
                                            )

    @pytest.mark.asyncio
    async def test_validate_input_child_safety_violations(self, validator):
        """Test validation with child safety violations."""
        with patch.object(validator, "detect_sql_injection", return_value=[]):
            with patch.object(validator, "detect_xss", return_value=[]):
                with patch.object(validator, "detect_path_traversal", return_value=[]):
                    with patch.object(
                        validator, "detect_command_injection", return_value=[]
                    ):
                        with patch.object(
                            validator, "detect_ldap_injection", return_value=[]
                        ):
                            with patch.object(
                                validator,
                                "detect_template_injection",
                                return_value=[],
                            ):
                                with patch.object(
                                    validator,
                                    "detect_inappropriate_content",
                                    return_value=["profanity"],
                                ):
                                    with patch.object(
                                        validator,
                                        "detect_pii",
                                        return_value=["personal_info"],
                                    ):
                                        with patch.object(
                                            validator,
                                            "detect_encoding_attacks",
                                            return_value=[],
                                        ):
                                            result = await validator.validate_input(
                                                "inappropriate content",
                                                "message",
                                            )

                                            assert result.is_valid is False
                                            assert (
                                                len(result.child_safety_violations) == 2
                                            )
                                            assert (
                                                "profanity"
                                                in result.child_safety_violations
                                            )
                                            assert (
                                                "personal_info"
                                                in result.child_safety_violations
                                            )

    @pytest.mark.asyncio
    async def test_validate_input_critical_vs_high_threats(self, validator):
        """Test validation result for critical vs high severity threats."""
        critical_threat = SecurityThreat(
            "command_injection", "critical", "field", "value", "Critical"
        )
        high_threat = SecurityThreat("sql_injection", "high", "field", "value", "High")

        # Test critical threat
        with patch.object(
            validator,
            "detect_command_injection",
            return_value=[critical_threat],
        ):
            with patch.object(validator, "detect_sql_injection", return_value=[]):
                with patch.object(validator, "detect_xss", return_value=[]):
                    with patch.object(
                        validator, "detect_path_traversal", return_value=[]
                    ):
                        with patch.object(
                            validator, "detect_ldap_injection", return_value=[]
                        ):
                            with patch.object(
                                validator,
                                "detect_template_injection",
                                return_value=[],
                            ):
                                with patch.object(
                                    validator,
                                    "detect_inappropriate_content",
                                    return_value=[],
                                ):
                                    with patch.object(
                                        validator,
                                        "detect_pii",
                                        return_value=[],
                                    ):
                                        with patch.object(
                                            validator,
                                            "detect_encoding_attacks",
                                            return_value=[],
                                        ):
                                            result = await validator.validate_input(
                                                "rm -rf /", "command"
                                            )

                                            assert result.is_valid is False
                                            assert result.has_critical_threats is True

        # Test high threat
        with patch.object(validator, "detect_command_injection", return_value=[]):
            with patch.object(
                validator, "detect_sql_injection", return_value=[high_threat]
            ):
                with patch.object(validator, "detect_xss", return_value=[]):
                    with patch.object(
                        validator, "detect_path_traversal", return_value=[]
                    ):
                        with patch.object(
                            validator, "detect_ldap_injection", return_value=[]
                        ):
                            with patch.object(
                                validator,
                                "detect_template_injection",
                                return_value=[],
                            ):
                                with patch.object(
                                    validator,
                                    "detect_inappropriate_content",
                                    return_value=[],
                                ):
                                    with patch.object(
                                        validator,
                                        "detect_pii",
                                        return_value=[],
                                    ):
                                        with patch.object(
                                            validator,
                                            "detect_encoding_attacks",
                                            return_value=[],
                                        ):
                                            result = await validator.validate_input(
                                                "'; DROP TABLE users; --",
                                                "query",
                                            )

                                            assert result.is_valid is False
                                            assert result.has_critical_threats is False


class TestInputValidationMiddleware:
    """Test the InputValidationMiddleware class."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock FastAPI app."""
        app = Mock()
        return app

    @pytest.fixture
    def mock_validator(self):
        """Create a mock validator."""
        validator = Mock()
        validator.validate_input = AsyncMock()

        with patch(
            "src.infrastructure.security.input_validation.middleware.get_input_validator",
            return_value=validator,
        ):
            yield validator

    @pytest.fixture
    def mock_audit_integration(self):
        """Create mock audit integration."""
        mock_audit = Mock()
        mock_audit.log_security_event = AsyncMock()

        with patch(
            "src.infrastructure.security.input_validation.middleware.get_audit_integration",
            return_value=mock_audit,
        ):
            yield mock_audit

    @pytest.fixture
    def middleware(self, mock_app, mock_validator, mock_audit_integration):
        """Create middleware instance."""
        return InputValidationMiddleware(
            mock_app, enable_child_safety=True, strict_mode=False
        )

    @pytest.fixture
    def mock_request(self):
        """Create a mock request."""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = Mock()
        request.url.path = "/api/test"
        request.query_params = {}
        request.headers = {"user-agent": "test-agent"}
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.body = AsyncMock(return_value=b"")
        return request

    @pytest.fixture
    def mock_response(self):
        """Create a mock response."""
        response = Mock(spec=Response)
        response.headers = {}
        return response

    def test_middleware_initialization(self, mock_app):
        """Test middleware initialization."""
        middleware = InputValidationMiddleware(
            mock_app, enable_child_safety=True, strict_mode=True
        )

        assert middleware.enable_child_safety is True
        assert middleware.strict_mode is True
        assert "/api/children" in middleware.child_endpoints
        assert "/api/auth" in middleware.auth_endpoints
        assert "/health" in middleware.skip_validation

    @pytest.mark.asyncio
    async def test_dispatch_skip_validation_endpoints(self, middleware, mock_request):
        """Test that validation is skipped for certain endpoints."""
        mock_request.url.path = "/health"

        async def mock_call_next(request):
            return Mock(spec=Response, headers={})

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response is not None
        # Should not call validator for health endpoint
        assert not middleware.validator.validate_input.called

    @pytest.mark.asyncio
    async def test_dispatch_get_request_validation(
        self, middleware, mock_request, mock_validator
    ):
        """Test validation of GET request."""
        mock_request.method = "GET"
        mock_request.query_params = {"param1": "value1", "param2": "value2"}
        mock_request.url.path = "/api/test"

        # Mock validator to return clean results
        mock_validator.validate_input.return_value = InputValidationResult(
            is_valid=True
        )

        async def mock_call_next(request):
            return Mock(spec=Response, headers={})

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response is not None
        assert response.headers.get("X-Input-Validation") == "passed"

        # Should validate query parameters
        assert mock_validator.validate_input.call_count >= 2

    @pytest.mark.asyncio
    async def test_dispatch_post_request_validation(
        self, middleware, mock_request, mock_validator
    ):
        """Test validation of POST request with body."""
        mock_request.method = "POST"
        mock_request.headers = {
            "content-type": "application/json",
            "user-agent": "test-agent",
        }
        mock_request.body = AsyncMock(return_value=b'{"key": "value"}')

        # Mock validator to return clean results
        mock_validator.validate_input.return_value = InputValidationResult(
            is_valid=True
        )

        async def mock_call_next(request):
            return Mock(spec=Response, headers={})

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response is not None
        assert response.headers.get("X-Input-Validation") == "passed"

        # Should validate body and headers
        assert mock_validator.validate_input.call_count >= 2

    @pytest.mark.asyncio
    async def test_dispatch_security_threat_blocking(
        self, middleware, mock_request, mock_validator
    ):
        """Test that security threats are blocked."""
        mock_request.method = "POST"
        mock_request.query_params = {"param": "malicious_value"}

        # Mock validator to return critical threat
        critical_threat = SecurityThreat(
            "sql_injection",
            "critical",
            "param",
            "malicious_value",
            "SQL injection",
        )
        mock_validator.validate_input.return_value = InputValidationResult(
            is_valid=False, threats=[critical_threat]
        )

        async def mock_call_next(request):
            return Mock(spec=Response, headers={})

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response.status_code == 400
        assert "X-Security-Block" in response.headers

        # Should not call the next handler
        response_data = json.loads(response.body.decode())
        assert "security_threat_detected" in response_data.get("error", "")

    @pytest.mark.asyncio
    async def test_dispatch_child_safety_blocking(
        self, middleware, mock_request, mock_validator
    ):
        """Test that child safety violations are blocked on child endpoints."""
        mock_request.method = "POST"
        mock_request.url.path = "/api/children/chat"

        # Mock validator to return child safety violations
        mock_validator.validate_input.return_value = InputValidationResult(
            is_valid=False, child_safety_violations=["inappropriate_content"]
        )

        async def mock_call_next(request):
            return Mock(spec=Response, headers={})

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response.status_code == 400

        response_data = json.loads(response.body.decode())
        assert "child_safety_violation" in response_data.get("error", "")

    @pytest.mark.asyncio
    async def test_dispatch_strict_mode_blocking(
        self, middleware, mock_request, mock_validator
    ):
        """Test that strict mode blocks high severity threats."""
        # Enable strict mode
        middleware.strict_mode = True

        mock_request.method = "POST"
        mock_request.query_params = {"param": "suspicious_value"}

        # Mock validator to return high threat
        high_threat = SecurityThreat(
            "xss", "high", "param", "suspicious_value", "XSS attempt"
        )
        mock_validator.validate_input.return_value = InputValidationResult(
            is_valid=False, threats=[high_threat]
        )

        async def mock_call_next(request):
            return Mock(spec=Response, headers={})

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response.status_code == 400

        response_data = json.loads(response.body.decode())
        assert "security_threat_detected" in response_data.get("error", "")

    @pytest.mark.asyncio
    async def test_dispatch_multiple_medium_threats_blocking(
        self, middleware, mock_request, mock_validator
    ):
        """Test that multiple medium threats are blocked."""
        mock_request.method = "POST"
        mock_request.query_params = {"param": "suspicious_value"}

        # Mock validator to return multiple medium threats
        threats = [
            SecurityThreat(
                "suspicious_pattern",
                "medium",
                "param",
                "value",
                "Suspicious pattern 1",
            ),
            SecurityThreat(
                "suspicious_pattern",
                "medium",
                "param",
                "value",
                "Suspicious pattern 2",
            ),
            SecurityThreat(
                "suspicious_pattern",
                "medium",
                "param",
                "value",
                "Suspicious pattern 3",
            ),
        ]
        mock_validator.validate_input.return_value = InputValidationResult(
            is_valid=False, threats=threats
        )

        async def mock_call_next(request):
            return Mock(spec=Response, headers={})

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response.status_code == 400

        response_data = json.loads(response.body.decode())
        assert "security_threat_detected" in response_data.get("error", "")

    @pytest.mark.asyncio
    async def test_dispatch_low_threats_allowed(
        self, middleware, mock_request, mock_validator
    ):
        """Test that low severity threats are allowed through."""
        mock_request.method = "GET"
        mock_request.query_params = {"param": "slightly_suspicious"}

        # Mock validator to return low threat
        low_threat = SecurityThreat(
            "minor_issue", "low", "param", "slightly_suspicious", "Minor issue"
        )
        mock_validator.validate_input.return_value = InputValidationResult(
            is_valid=True, threats=[low_threat]
        )

        async def mock_call_next(request):
            return Mock(spec=Response, headers={})

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response.headers.get("X-Input-Validation") == "passed"
        assert response.headers.get("X-Security-Warnings") == "1"

    @pytest.mark.asyncio
    async def test_extract_request_context(self, middleware, mock_request):
        """Test request context extraction."""
        mock_request.method = "POST"
        mock_request.url.path = "/api/children/chat"
        mock_request.headers = {
            "user-agent": "test-agent",
            "x-forwarded-for": "192.168.1.1",
        }

        context = await middleware._extract_request_context(mock_request)

        assert context["method"] == "POST"
        assert context["path"] == "/api/children/chat"
        assert context["ip_address"] == "192.168.1.1"
        assert context["user_agent"] == "test-agent"
        assert context["is_child_endpoint"] is True
        assert context["is_auth_endpoint"] is False

    @pytest.mark.asyncio
    async def test_get_request_body_json(self, middleware, mock_request):
        """Test JSON request body parsing."""
        mock_request.headers = {"content-type": "application/json"}
        mock_request.body = AsyncMock(return_value=b'{"key": "value", "number": 42}')

        body = await middleware._get_request_body(mock_request)

        assert body == {"key": "value", "number": 42}

    @pytest.mark.asyncio
    async def test_get_request_body_form_data(self, middleware, mock_request):
        """Test form data request body parsing."""
        mock_request.headers = {"content-type": "application/x-www-form-urlencoded"}
        mock_form = {"field1": "value1", "field2": "value2"}
        mock_request.form = AsyncMock(return_value=mock_form)

        body = await middleware._get_request_body(mock_request)

        assert body == mock_form

    @pytest.mark.asyncio
    async def test_get_request_body_multipart(self, middleware, mock_request):
        """Test multipart form data request body parsing."""
        mock_request.headers = {"content-type": "multipart/form-data"}
        mock_form = {"field1": "value1", "field2": "value2"}
        mock_request.form = AsyncMock(return_value=mock_form)

        body = await middleware._get_request_body(mock_request)

        assert body == mock_form

    @pytest.mark.asyncio
    async def test_get_request_body_parse_error(self, middleware, mock_request):
        """Test request body parsing error handling."""
        mock_request.headers = {"content-type": "application/json"}
        mock_request.body = AsyncMock(side_effect=Exception("Parse error"))

        body = await middleware._get_request_body(mock_request)

        assert body is None

    def test_get_client_ip_forwarded_for(self, middleware, mock_request):
        """Test client IP extraction from x-forwarded-for header."""
        mock_request.headers = {"x-forwarded-for": "192.168.1.1, 10.0.0.1"}

        ip = middleware._get_client_ip(mock_request)

        assert ip == "192.168.1.1"

    def test_get_client_ip_real_ip(self, middleware, mock_request):
        """Test client IP extraction from x-real-ip header."""
        mock_request.headers = {"x-real-ip": "203.0.113.1"}

        ip = middleware._get_client_ip(mock_request)

        assert ip == "203.0.113.1"

    def test_get_client_ip_client_host(self, middleware, mock_request):
        """Test client IP extraction from client host."""
        mock_request.headers = {}
        mock_request.client = Mock()
        mock_request.client.host = "127.0.0.1"

        ip = middleware._get_client_ip(mock_request)

        assert ip == "127.0.0.1"

    def test_get_client_ip_unknown(self, middleware, mock_request):
        """Test client IP extraction when unknown."""
        mock_request.headers = {}
        mock_request.client = None

        ip = middleware._get_client_ip(mock_request)

        assert ip == "unknown"

    @pytest.mark.asyncio
    async def test_should_block_request_critical_threats(self, middleware):
        """Test that critical threats cause blocking."""
        threats = [
            SecurityThreat(
                "command_injection", "critical", "field", "value", "Critical"
            )
        ]
        context = {"is_child_endpoint": False}

        should_block = await middleware._should_block_request(threats, [], context)

        assert should_block is True

    @pytest.mark.asyncio
    async def test_should_block_request_child_safety_on_child_endpoint(
        self, middleware
    ):
        """Test that child safety violations cause blocking on child endpoints."""
        threats = []
        child_safety_violations = ["inappropriate_content"]
        context = {"is_child_endpoint": True}

        should_block = await middleware._should_block_request(
            threats, child_safety_violations, context
        )

        assert should_block is True

    @pytest.mark.asyncio
    async def test_should_block_request_child_safety_on_regular_endpoint(
        self, middleware
    ):
        """Test that child safety violations don't cause blocking on regular endpoints."""
        threats = []
        child_safety_violations = ["inappropriate_content"]
        context = {"is_child_endpoint": False}

        should_block = await middleware._should_block_request(
            threats, child_safety_violations, context
        )

        assert should_block is False

    @pytest.mark.asyncio
    async def test_should_block_request_strict_mode_high_threats(self, middleware):
        """Test that strict mode blocks high severity threats."""
        middleware.strict_mode = True
        threats = [SecurityThreat("xss", "high", "field", "value", "High threat")]
        context = {"is_child_endpoint": False}

        should_block = await middleware._should_block_request(threats, [], context)

        assert should_block is True

    @pytest.mark.asyncio
    async def test_should_block_request_multiple_medium_threats(self, middleware):
        """Test that multiple medium threats cause blocking."""
        threats = [
            SecurityThreat("suspicious1", "medium", "field", "value", "Medium 1"),
            SecurityThreat("suspicious2", "medium", "field", "value", "Medium 2"),
            SecurityThreat("suspicious3", "medium", "field", "value", "Medium 3"),
        ]
        context = {"is_child_endpoint": False}

        should_block = await middleware._should_block_request(threats, [], context)

        assert should_block is True

    @pytest.mark.asyncio
    async def test_should_block_request_few_medium_threats(self, middleware):
        """Test that few medium threats don't cause blocking."""
        threats = [
            SecurityThreat("suspicious1", "medium", "field", "value", "Medium 1"),
            SecurityThreat("suspicious2", "medium", "field", "value", "Medium 2"),
        ]
        context = {"is_child_endpoint": False}

        should_block = await middleware._should_block_request(threats, [], context)

        assert should_block is False

    @pytest.mark.asyncio
    async def test_log_security_incident(
        self, middleware, mock_request, mock_audit_integration
    ):
        """Test security incident logging."""
        threats = [
            SecurityThreat(
                "sql_injection", "critical", "field", "value", "SQL injection"
            )
        ]
        child_safety_violations = ["inappropriate_content"]

        await middleware._log_security_incident(
            mock_request, threats, child_safety_violations
        )

        # Verify audit integration was called
        mock_audit_integration.log_security_event.assert_called_once()
        call_args = mock_audit_integration.log_security_event.call_args[1]

        assert call_args["event_type"] == "input_validation_blocked"
        assert call_args["severity"] == "critical"
        assert (
            "Request blocked due to input validation failures"
            in call_args["description"]
        )

    @pytest.mark.asyncio
    async def test_log_security_warning(
        self, middleware, mock_request, mock_audit_integration
    ):
        """Test security warning logging."""
        threats = [
            SecurityThreat(
                "suspicious_pattern", "medium", "field", "value", "Suspicious"
            )
        ]
        child_safety_violations = []

        await middleware._log_security_warning(
            mock_request, threats, child_safety_violations
        )

        # Verify audit integration was called
        mock_audit_integration.log_security_event.assert_called_once()
        call_args = mock_audit_integration.log_security_event.call_args[1]

        assert call_args["event_type"] == "input_validation_warning"
        assert call_args["severity"] == "warning"
        assert "Request processed with security warnings" in call_args["description"]

    @pytest.mark.asyncio
    async def test_create_security_error_response_child_safety(self, middleware):
        """Test security error response for child safety violations."""
        threats = []
        child_safety_violations = ["inappropriate_content"]
        context = {"is_child_endpoint": True}

        response = await middleware._create_security_error_response(
            threats, child_safety_violations, context
        )

        assert response.status_code == 400
        assert "X-Security-Block" in response.headers

        response_data = json.loads(response.body.decode())
        assert "request_not_allowed" in response_data.get("error", "")

    @pytest.mark.asyncio
    async def test_create_security_error_response_critical_threat(self, middleware):
        """Test security error response for critical threats."""
        threats = [
            SecurityThreat(
                "command_injection", "critical", "field", "value", "Critical"
            )
        ]
        child_safety_violations = []
        context = {"is_child_endpoint": False}

        response = await middleware._create_security_error_response(
            threats, child_safety_violations, context
        )

        assert response.status_code == 400
        assert "X-Security-Block" in response.headers

        response_data = json.loads(response.body.decode())
        assert "security_threat_detected" in response_data.get("error", "")
        assert "potentially malicious content" in response_data.get("message", "")

    @pytest.mark.asyncio
    async def test_create_security_error_response_generic(self, middleware):
        """Test generic security error response."""
        threats = [
            SecurityThreat("suspicious_pattern", "high", "field", "value", "Suspicious")
        ]
        child_safety_violations = []
        context = {"is_child_endpoint": False}

        response = await middleware._create_security_error_response(
            threats, child_safety_violations, context
        )

        assert response.status_code == 400
        assert "X-Security-Block" in response.headers

        response_data = json.loads(response.body.decode())
        assert "security_threat_detected" in response_data.get("error", "")

    @pytest.mark.asyncio
    async def test_dispatch_middleware_error_handling(self, middleware, mock_request):
        """Test middleware error handling."""
        # Mock validator to raise exception
        middleware.validator.validate_input.side_effect = Exception("Validation error")

        async def mock_call_next(request):
            return Mock(spec=Response, headers={})

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response.headers.get("X-Input-Validation") == "error"


class TestGlobalValidator:
    """Test the global validator functions."""

    def test_get_input_validator_singleton(self):
        """Test that get_input_validator returns singleton instance."""
        # Clear global instance
        import src.infrastructure.security.input_validation.validator as validator_module

        validator_module._global_validator = None

        # Get first instance
        validator1 = get_input_validator()
        assert validator1 is not None

        # Get second instance - should be same
        validator2 = get_input_validator()
        assert validator1 is validator2

    def test_get_input_validator_type(self):
        """Test that get_input_validator returns correct type."""
        validator = get_input_validator()
        assert isinstance(validator, ComprehensiveInputValidator)

    @pytest.mark.asyncio
    async def test_validate_user_input_function(self):
        """Test validate_user_input convenience function."""
        with patch(
            "src.infrastructure.security.input_validation.validator.get_input_validator"
        ) as mock_get_validator:
            mock_validator = Mock()
            mock_validator.validate_input = AsyncMock(
                return_value=InputValidationResult(True)
            )
            mock_get_validator.return_value = mock_validator

            result = await validate_user_input("test input", "field", False)

            assert result.is_valid is True
            mock_validator.validate_input.assert_called_once_with("test input", "field")

    @pytest.mark.asyncio
    async def test_validate_user_input_require_child_safe(self):
        """Test validate_user_input with child safety requirement."""
        with patch(
            "src.infrastructure.security.input_validation.validator.get_input_validator"
        ) as mock_get_validator:
            mock_validator = Mock()
            mock_validator.validate_input = AsyncMock(
                return_value=InputValidationResult(
                    True, child_safety_violations=["inappropriate_content"]
                )
            )
            mock_get_validator.return_value = mock_validator

            result = await validate_user_input("test input", "field", True)

            assert result.is_valid is False
            assert len(result.child_safety_violations) == 1

    @pytest.mark.asyncio
    async def test_validate_child_message_function(self):
        """Test validate_child_message convenience function."""
        with patch(
            "src.infrastructure.security.input_validation.validator.validate_user_input"
        ) as mock_validate:
            mock_validate.return_value = InputValidationResult(True)

            result = await validate_child_message("Hello, world!")

            assert result.is_valid is True
            mock_validate.assert_called_once_with(
                "Hello, world!", "message", require_child_safe=True
            )


class TestFactoryFunction:
    """Test the factory function."""

    def test_create_input_validation_middleware(self):
        """Test create_input_validation_middleware factory function."""
        mock_app = Mock()

        middleware = create_input_validation_middleware(
            mock_app, enable_child_safety=True, strict_mode=True
        )

        assert isinstance(middleware, InputValidationMiddleware)
        assert middleware.enable_child_safety is True
        assert middleware.strict_mode is True

    def test_create_input_validation_middleware_defaults(self):
        """Test create_input_validation_middleware with default parameters."""
        mock_app = Mock()

        middleware = create_input_validation_middleware(mock_app)

        assert isinstance(middleware, InputValidationMiddleware)
        assert middleware.enable_child_safety is True
        assert middleware.strict_mode is False


class TestBackwardsCompatibilityImports:
    """Test backwards compatibility imports."""

    def test_security_threat_import(self):
        """Test SecurityThreat import."""
        assert ImportedSecurityThreat is SecurityThreat

    def test_input_validation_result_import(self):
        """Test InputValidationResult import."""
        assert ImportedInputValidationResult is InputValidationResult

    def test_comprehensive_input_validator_import(self):
        """Test ComprehensiveInputValidator import."""
        assert ImportedComprehensiveInputValidator is ComprehensiveInputValidator

    def test_get_input_validator_import(self):
        """Test get_input_validator import."""
        assert imported_get_input_validator is get_input_validator

    def test_validate_user_input_import(self):
        """Test validate_user_input import."""
        assert imported_validate_user_input is validate_user_input

    def test_validate_child_message_import(self):
        """Test validate_child_message import."""
        assert imported_validate_child_message is validate_child_message

    def test_input_validation_middleware_import(self):
        """Test InputValidationMiddleware import."""
        assert ImportedInputValidationMiddleware is InputValidationMiddleware

    def test_create_input_validation_middleware_import(self):
        """Test create_input_validation_middleware import."""
        assert (
            imported_create_input_validation_middleware
            is create_input_validation_middleware
        )

    def test_all_exports_available(self):
        """Test that all exports are available."""
        from src.infrastructure.validation.comprehensive_validator import (
            __all__,
        )

        expected_exports = [
            "SecurityThreat",
            "InputValidationResult",
            "ComprehensiveInputValidator",
            "get_input_validator",
            "validate_user_input",
            "validate_child_message",
            "InputValidationMiddleware",
            "create_input_validation_middleware",
        ]

        assert set(__all__) == set(expected_exports)


class TestInputValidationIntegration:
    """Integration tests for input validation."""

    @pytest.mark.asyncio
    async def test_full_middleware_workflow_clean_request(self):
        """Test full middleware workflow with clean request."""
        mock_app = Mock()

        with patch(
            "src.infrastructure.security.input_validation.middleware.get_input_validator"
        ) as mock_get_validator:
            mock_validator = Mock()
            mock_validator.validate_input = AsyncMock(
                return_value=InputValidationResult(True)
            )
            mock_get_validator.return_value = mock_validator

            with patch(
                "src.infrastructure.security.input_validation.middleware.get_audit_integration"
            ) as mock_get_audit:
                mock_audit = Mock()
                mock_audit.log_security_event = AsyncMock()
                mock_get_audit.return_value = mock_audit

                middleware = InputValidationMiddleware(mock_app)

                # Create mock request
                mock_request = Mock(spec=Request)
                mock_request.method = "GET"
                mock_request.url = Mock()
                mock_request.url.path = "/api/test"
                mock_request.query_params = {"param": "clean_value"}
                mock_request.headers = {"user-agent": "test-agent"}
                mock_request.client = Mock()
                mock_request.client.host = "127.0.0.1"

                async def mock_call_next(request):
                    return Mock(spec=Response, headers={})

                response = await middleware.dispatch(mock_request, mock_call_next)

                assert response.headers.get("X-Input-Validation") == "passed"
                assert mock_validator.validate_input.called
                assert not mock_audit.log_security_event.called

    @pytest.mark.asyncio
    async def test_full_middleware_workflow_malicious_request(self):
        """Test full middleware workflow with malicious request."""
        mock_app = Mock()

        with patch(
            "src.infrastructure.security.input_validation.middleware.get_input_validator"
        ) as mock_get_validator:
            mock_validator = Mock()

            # Mock validator to return critical threat
            critical_threat = SecurityThreat(
                "sql_injection",
                "critical",
                "param",
                "'; DROP TABLE users; --",
                "SQL injection",
            )
            mock_validator.validate_input = AsyncMock(
                return_value=InputValidationResult(False, threats=[critical_threat])
            )
            mock_get_validator.return_value = mock_validator

            with patch(
                "src.infrastructure.security.input_validation.middleware.get_audit_integration"
            ) as mock_get_audit:
                mock_audit = Mock()
                mock_audit.log_security_event = AsyncMock()
                mock_get_audit.return_value = mock_audit

                middleware = InputValidationMiddleware(mock_app)

                # Create mock request
                mock_request = Mock(spec=Request)
                mock_request.method = "GET"
                mock_request.url = Mock()
                mock_request.url.path = "/api/test"
                mock_request.query_params = {"param": "'; DROP TABLE users; --"}
                mock_request.headers = {"user-agent": "test-agent"}
                mock_request.client = Mock()
                mock_request.client.host = "127.0.0.1"

                async def mock_call_next(request):
                    return Mock(spec=Response, headers={})

                response = await middleware.dispatch(mock_request, mock_call_next)

                assert response.status_code == 400
                assert "X-Security-Block" in response.headers
                assert mock_audit.log_security_event.called

    @pytest.mark.asyncio
    async def test_child_safety_workflow(self):
        """Test child safety workflow."""
        mock_app = Mock()

        with patch(
            "src.infrastructure.security.input_validation.middleware.get_input_validator"
        ) as mock_get_validator:
            mock_validator = Mock()

            # Mock validator to return child safety violation
            mock_validator.validate_input = AsyncMock(
                return_value=InputValidationResult(
                    False, child_safety_violations=["inappropriate_content"]
                )
            )
            mock_get_validator.return_value = mock_validator

            with patch(
                "src.infrastructure.security.input_validation.middleware.get_audit_integration"
            ) as mock_get_audit:
                mock_audit = Mock()
                mock_audit.log_security_event = AsyncMock()
                mock_get_audit.return_value = mock_audit

                middleware = InputValidationMiddleware(
                    mock_app, enable_child_safety=True
                )

                # Create mock request for child endpoint
                mock_request = Mock(spec=Request)
                mock_request.method = "POST"
                mock_request.url = Mock()
                mock_request.url.path = "/api/children/chat"
                mock_request.query_params = {"message": "inappropriate content"}
                mock_request.headers = {"user-agent": "test-agent"}
                mock_request.client = Mock()
                mock_request.client.host = "127.0.0.1"

                async def mock_call_next(request):
                    return Mock(spec=Response, headers={})

                response = await middleware.dispatch(mock_request, mock_call_next)

                assert response.status_code == 400
                response_data = json.loads(response.body.decode())
                assert "request_not_allowed" in response_data.get("error", "")
                assert mock_audit.log_security_event.called

    def test_validator_singleton_behavior(self):
        """Test validator singleton behavior across multiple calls."""
        # Clear global instance
        import src.infrastructure.security.input_validation.validator as validator_module

        validator_module._global_validator = None

        # Create multiple instances
        validator1 = get_input_validator()
        validator2 = get_input_validator()
        validator3 = get_input_validator()

        # All should be the same instance
        assert validator1 is validator2
        assert validator2 is validator3
        assert isinstance(validator1, ComprehensiveInputValidator)

    @pytest.mark.asyncio
    async def test_convenience_functions_integration(self):
        """Test convenience functions integration."""
        with patch(
            "src.infrastructure.security.input_validation.validator.get_input_validator"
        ) as mock_get_validator:
            mock_validator = Mock()
            mock_validator.validate_input = AsyncMock(
                return_value=InputValidationResult(True)
            )
            mock_get_validator.return_value = mock_validator

            # Test validate_user_input
            result1 = await validate_user_input("test input", "field")
            assert result1.is_valid is True

            # Test validate_child_message
            result2 = await validate_child_message("Hello, world!")
            assert result2.is_valid is True

            # Both should use the same validator instance
            assert mock_validator.validate_input.call_count == 2
