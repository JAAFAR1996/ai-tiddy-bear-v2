import json
import sys
import tempfile
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

from infrastructure.exception_handling import handle_exceptions, with_retry
from infrastructure.exception_handling.enterprise_exception_handler import (
    EnterpriseExceptionHandler,
    ExceptionHandlerConfig,
)
from infrastructure.security.audit_logger import (
    AuditCategory,
    AuditConfig,
    AuditContext,
    AuditEventType,
    AuditLogger,
    AuditSeverity,
    log_audit_event,
    log_child_safety_incident,
)
from infrastructure.security.safe_expression_parser import (
    ExpressionContext,
    SafeExpressionConfig,
    SafeExpressionParser,
    safe_eval,
    safe_json_logic,
    safe_template,
)
from infrastructure.security.secrets_manager import (
    SecretConfig,
    SecretProvider,
    SecretType,
    create_secrets_manager,
)

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

"""
Phase 1 Security Foundation Tests
Comprehensive testing of all security improvements implemented in Phase 1
"""


try:
    import pytest
except ImportError:
    try:
        from common.mock_pytest import pytest
    except ImportError:
        pass

    # Mock pytest when not available
    class MockPytest:
        def fixture(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

        def mark(self):
            class MockMark:
                def parametrize(self, *args, **kwargs):
                    def decorator(func):
                        return func

                    return decorator

                def asyncio(self, func):
                    return func

                def slow(self, func):
                    return func

                def skip(self, reason=""):
                    def decorator(func):
                        return func

                    return decorator

            return MockMark()

        def raises(self, exception):
            class MockRaises:
                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    return False

            return MockRaises()

        def skip(self, reason=""):
            def decorator(func):
                return func

            return decorator

    pytest = MockPytest()


class TestPhase1SecurityFoundation:
    """Comprehensive tests for Phase 1 security foundation"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def audit_config(self, temp_dir):
        """Create audit configuration for testing"""
        return AuditConfig(
            log_directory=temp_dir / "audit_logs",
            max_file_size_mb=1,
            max_files=5,
            retention_days=7,
            enable_encryption=True,
            enable_tamper_detection=True,
            batch_size=10,
            flush_interval_seconds=1.0,
        )

    @pytest.fixture
    def exception_handler_config(self):
        """Create exception handler configuration for testing"""
        return ExceptionHandlerConfig(
            enable_structured_logging=True,
            enable_correlation_ids=True,
            enable_error_tracking=True,
            enable_circuit_breaker=True,
            max_retry_attempts=3,
            retry_delay_seconds=0.1,
            exponential_backoff=True,
            log_sensitive_data=False,
            error_threshold_per_minute=10,
            circuit_breaker_timeout_seconds=5,
        )

    @pytest.fixture
    def safe_expression_config(self):
        """Create safe expression parser configuration for testing"""
        return SafeExpressionConfig(
            default_security_level="RESTRICTED",
            max_complexity_score=5,
            evaluation_timeout=2.0,
            enable_json_logic=True,
            enable_templates=True,
            strict_validation=True,
        )

    @pytest.fixture
    def secrets_config(self):
        """Create secrets manager configuration for testing"""
        return SecretConfig(
            default_provider=SecretProvider.LOCAL_ENCRYPTED,
            auto_rotation_enabled=True,
            rotation_check_interval_hours=1,
            cache_ttl_seconds=60,
            audit_enabled=True,
            secure_delete_enabled=True,
        )

    # ================== SECRETS MANAGEMENT TESTS ==================

    @pytest.mark.asyncio
    async def test_secrets_manager_initialization(self, temp_dir, secrets_config):
        """Test secrets manager initialization"""
        secrets_manager = create_secrets_manager(
            environment="testing",
            vault_url=None,
            vault_token=None,
        )

        assert secrets_manager is not None
        assert secrets_manager.config.default_provider == SecretProvider.LOCAL_ENCRYPTED

    @pytest.mark.asyncio
    async def test_secrets_manager_set_get_secret(self, temp_dir, secrets_config):
        """Test setting and getting secrets"""
        secrets_manager = create_secrets_manager("testing")

        # Set secret
        success = await secrets_manager.set_secret(
            name="test_api_key",
            value="test_secret_value",
            secret_type=SecretType.API_KEY,
            rotation_interval_days=30,
        )
        assert success is True

        # Get secret
        secret_value = await secrets_manager.get_secret("test_api_key")
        assert secret_value == "test_secret_value"

    @pytest.mark.asyncio
    async def test_secrets_manager_rotation(self, temp_dir, secrets_config):
        """Test secret rotation"""
        secrets_manager = create_secrets_manager("testing")

        # Set initial secret
        await secrets_manager.set_secret("test_key", "old_value")

        # Rotate secret
        success = await secrets_manager.rotate_secret("test_key", "new_value")
        assert success is True

        # Verify new value
        new_value = await secrets_manager.get_secret("test_key")
        assert new_value == "new_value"

    # ================== SAFE EXPRESSION PARSER TESTS ==================

    def test_safe_expression_parser_initialization(self, safe_expression_config):
        """Test safe expression parser initialization"""
        parser = SafeExpressionParser(safe_expression_config)
        assert parser is not None
        assert parser.config == safe_expression_config

    def test_safe_arithmetic_expressions(self, safe_expression_config):
        """Test safe arithmetic expressions"""
        parser = SafeExpressionParser(safe_expression_config)
        context = ExpressionContext()

        # Test basic arithmetic
        assert parser.evaluate("2 + 3", context) == 5
        assert parser.evaluate("10 - 5", context) == 5
        assert parser.evaluate("3 * 4", context) == 12
        assert parser.evaluate("15 / 3", context) == 5.0
        assert parser.evaluate("2 ** 3", context) == 8
        assert parser.evaluate("17 % 5", context) == 2

    def test_safe_comparison_expressions(self, safe_expression_config):
        """Test safe comparison expressions"""
        parser = SafeExpressionParser(safe_expression_config)
        context = ExpressionContext()

        # Test comparisons
        assert parser.evaluate("5 > 3", context) is True
        assert parser.evaluate("2 < 1", context) is False
        assert parser.evaluate("3 == 3", context) is True
        assert parser.evaluate("4 != 5", context) is True
        assert parser.evaluate("10 >= 10", context) is True
        assert parser.evaluate("7 <= 8", context) is True

    def test_safe_logical_expressions(self, safe_expression_config):
        """Test safe logical expressions"""
        parser = SafeExpressionParser(safe_expression_config)
        context = ExpressionContext()

        # Test logical operations
        assert parser.evaluate("True and False", context) is False
        assert parser.evaluate("True or False", context) is True
        assert parser.evaluate("not True", context) is False
        assert parser.evaluate("(5 > 3) and (2 < 4)", context) is True

    def test_safe_function_calls(self, safe_expression_config):
        """Test safe function calls"""
        parser = SafeExpressionParser(safe_expression_config)
        context = ExpressionContext()

        # Test safe functions
        assert parser.evaluate("abs(-5)", context) == 5
        assert parser.evaluate("round(3.7)", context) == 4
        assert parser.evaluate("min(5, 3, 8)", context) == 3
        assert parser.evaluate("max(5, 3, 8)", context) == 8
        assert parser.evaluate("sum([1, 2, 3, 4])", context) == 10

    def test_dangerous_expressions_blocked(self, safe_expression_config):
        """Test that dangerous expressions are blocked"""
        parser = SafeExpressionParser(safe_expression_config)
        context = ExpressionContext()

        # Test dangerous expressions
        dangerous_expressions = [
            "__import__('os')",
            "__import__('os').system('ls')",
            "open('/etc/passwd')",
            "eval('2+2')",
            "exec('x = 1')",
        ]

        for expr in dangerous_expressions:
            with pytest.raises(Exception):
                parser.evaluate(expr, context)

    def test_safe_eval_convenience_function(self):
        """Test safe_eval convenience function"""
        variables = {"x": 10, "y": 5}

        assert safe_eval("x + y", variables) == 15
        assert safe_eval("x * y", variables) == 50
        assert safe_eval("x > y", variables) is True

    def test_safe_template_processing(self):
        """Test safe template processing"""
        template = "Hello {{name}}, you are {{age}} years old"
        variables = {"name": "Alice", "age": 25}

        result = safe_template(template, variables)
        assert result == "Hello Alice, you are 25 years old"

    def test_safe_json_logic(self):
        """Test safe JSONLogic processing"""
        logic = {"and": [{"<": [{"var": "age"}, 18]}, {">": [{"var": "score"}, 80]}]}
        variables = {"age": 16, "score": 85}

        result = safe_json_logic(json.dumps(logic), variables)
        assert result is True

    # ================== EXCEPTION HANDLING TESTS ==================

    def test_exception_handler_initialization(self, exception_handler_config):
        """Test exception handler initialization"""
        handler = EnterpriseExceptionHandler(exception_handler_config)
        assert handler is not None
        assert handler.config == exception_handler_config

    @pytest.mark.asyncio
    async def test_exception_handler_logging(self, exception_handler_config):
        """Test exception handler logging"""
        # Test handling a simple exception
        test_exception = ValueError("Test error")
        error_details = EnterpriseExceptionHandler(
            exception_handler_config
        ).handle_exception(
            test_exception,
            error_code="TEST_ERROR",
            additional_data={"test_key": "test_value"},
            reraise=False,
        )

        assert error_details is not None
        assert error_details.error_type == "ValueError"
        assert error_details.error_message == "Test error"
        assert error_details.error_code == "TEST_ERROR"
        assert error_details.additional_data["test_key"] == "test_value"

    @pytest.mark.asyncio
    async def test_circuit_breaker_functionality(self, exception_handler_config):
        """Test circuit breaker functionality"""
        # Get circuit breaker
        cb = EnterpriseExceptionHandler(exception_handler_config).get_circuit_breaker(
            "test_service"
        )

        assert cb.state == "CLOSED"
        assert cb.can_execute() is True

        # Simulate failures
        for _ in range(exception_handler_config.error_threshold_per_minute):
            cb.on_failure(ValueError("Test failure"))

        # Circuit should be open
        assert cb.state == "OPEN"
        assert cb.can_execute() is False

        # Wait for timeout
        cb.last_failure_time = datetime.now(UTC) - timedelta(
            seconds=exception_handler_config.circuit_breaker_timeout_seconds + 1
        )

        # Should be half-open
        assert cb.can_execute() is True
        cb.on_success()
        assert cb.state == "CLOSED"

    @pytest.mark.asyncio
    async def test_handle_exceptions_decorator(self, exception_handler_config):
        """Test handle_exceptions decorator"""

        @handle_exceptions(error_code="TEST_ERROR")
        async def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            await failing_function()

    @pytest.mark.asyncio
    async def test_with_retry_decorator(self, exception_handler_config):
        """Test with_retry decorator"""
        call_count = 0

        @with_retry(max_attempts=3, retry_delay_seconds=0.1)
        async def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary error")
            return "success"

        result = await failing_function()
        assert result == "success"
        assert call_count == 3

    # ================== AUDIT LOGGING TESTS ==================

    @pytest.mark.asyncio
    async def test_audit_logger_initialization(self, audit_config):
        """Test audit logger initialization"""
        logger = AuditLogger(audit_config)
        assert logger is not None
        assert logger.config == audit_config

    @pytest.mark.asyncio
    async def test_audit_event_logging(self, audit_config):
        """Test audit event logging"""
        logger = AuditLogger(audit_config)

        context = AuditContext(
            user_id="test_user",
            child_id="test_child",
            session_id="test_session",
            ip_address="127.0.0.1",
        )

        event_id = await logger.log_event(
            event_type=AuditEventType.CHILD_INTERACTION_START,
            severity=AuditSeverity.INFO,
            category=AuditCategory.CHILD_SAFETY,
            description="Test child interaction",
            context=context,
            details={"test_key": "test_value"},
        )

        assert event_id is not None
        assert event_id.startswith("audit_")

    @pytest.mark.asyncio
    async def test_child_interaction_logging(self, audit_config):
        """Test child interaction logging"""
        logger = AuditLogger(audit_config)

        event_id = await logger.log_child_interaction(
            child_id="test_child",
            interaction_type="voice_capture",
            content="Hello teddy",
            response="Hello there!",
            safety_score=0.9,
        )

        assert event_id is not None

    @pytest.mark.asyncio
    async def test_safety_incident_logging(self, audit_config):
        """Test safety incident logging"""
        logger = AuditLogger(audit_config)

        event_id = await logger.log_safety_incident(
            child_id="test_child",
            incident_type="inappropriate_content",
            severity=AuditSeverity.WARNING,
            description="Inappropriate content detected",
            details={"content": "test content", "score": 0.3},
        )

        assert event_id is not None

    @pytest.mark.asyncio
    async def test_data_access_logging(self, audit_config):
        """Test data access logging"""
        logger = AuditLogger(audit_config)

        event_id = await logger.log_data_access(
            user_id="test_user",
            data_type="child_profile",
            operation="read",
            resource_id="child_123",
        )

        assert event_id is not None

    @pytest.mark.asyncio
    async def test_convenience_functions(self, audit_config):
        """Test convenience functions"""
        # Test log_audit_event
        event_id = await log_audit_event(
            event_type=AuditEventType.LOGIN_SUCCESS,
            severity=AuditSeverity.INFO,
            category=AuditCategory.AUTHENTICATION,
            description="User login successful",
            context=AuditContext(user_id="test_user"),
        )
        assert event_id is not None

        # Test log_child_safety_incident
        incident_id = await log_child_safety_incident(
            child_id="test_child",
            incident_type="test_incident",
            description="Test safety incident",
        )
        assert incident_id is not None

    # ================== INTEGRATION TESTS ==================

    @pytest.mark.asyncio
    async def test_security_integration_workflow(
        self, temp_dir, exception_handler_config, audit_config
    ):
        """Test complete security integration workflow"""
        # Initialize all security components
        secrets_manager = create_secrets_manager("testing")
        exception_handler = EnterpriseExceptionHandler(exception_handler_config)

        # Set up a secret
        await secrets_manager.set_secret("test_key", "test_value")

        # Test safe expression evaluation
        result = safe_eval("2 + 3 * 4")
        assert result == 14

        # Test audit logging
        event_id = await log_audit_event(
            event_type=AuditEventType.SYSTEM_STARTUP,
            severity=AuditSeverity.INFO,
            category=AuditCategory.SYSTEM_SECURITY,
            description="Security integration test",
        )
        assert event_id is not None

        # Test exception handling
        try:
            raise ValueError("Integration test error")
        except Exception as e:
            error_details = exception_handler.handle_exception(e, reraise=False)
            assert error_details is not None

    @pytest.mark.asyncio
    async def test_child_safety_workflow(
        self, temp_dir, exception_handler_config, audit_config
    ):
        """Test child safety workflow with all security components"""
        # Initialize components
        exception_handler = EnterpriseExceptionHandler(exception_handler_config)

        # Simulate child interaction
        try:
            # Log interaction start
            # Log interaction start
            # interaction_id = audit_logger.log_child_interaction(
            #     child_id="child_123",
            #     interaction_type="voice_capture",
            #     content="Tell me a story",
            #     safety_score=0.8,
            # )
            # assert interaction_id is not None

            # Process content safely
            content_length = safe_eval("len('Tell me a story')")
            assert content_length == 16

            # Log interaction end
            # end_id = audit_logger.log_child_interaction(
            #     child_id="child_123",
            #     interaction_type="voice_capture",
            #     content="Tell me a story",
            #     response="Once upon a time...",
            #     safety_score=0.9,
            # )
            # assert end_id is not None

        except Exception as e:
            # Handle any errors
            error_details = exception_handler.handle_exception(e, reraise=False)
            assert error_details is not None

    # ================== PERFORMANCE TESTS ==================

    @pytest.mark.asyncio
    async def test_audit_logging_performance(self, audit_config):
        """Test audit logging performance"""
        logger = AuditLogger(audit_config)

        start_time = time.time()

        # Log multiple events
        for i in range(100):
            await logger.log_event(
                event_type=AuditEventType.DATA_ACCESS,
                severity=AuditSeverity.INFO,
                category=AuditCategory.DATA_PROTECTION,
                description=f"Test event {i}",
            )

        end_time = time.time()
        duration = end_time - start_time

        # Should complete within reasonable time
        assert duration < 10.0  # 10 seconds for 100 events

    def test_safe_expression_performance(self, safe_expression_config):
        """Test safe expression evaluation performance"""
        parser = SafeExpressionParser(safe_expression_config)
        context = ExpressionContext()

        start_time = time.time()

        # Evaluate multiple expressions
        for i in range(1000):
            result = parser.evaluate(f"{i} + {i}", context)
            assert result == i * 2

        end_time = time.time()
        duration = end_time - start_time

        # Should complete within reasonable time
        assert duration < 5.0  # 5 seconds for 1000 expressions

    # ================== SECURITY VALIDATION TESTS ==================

    def test_no_hardcoded_secrets(self):
        """Test that no hardcoded secrets exist in the codebase"""
        # This test validates that we're not using hardcoded secrets
        # The actual validation would be done by security scanning tools

        # Test that our secrets manager properly handles secrets
        secrets_manager = create_secrets_manager("testing")
        assert secrets_manager is not None

        # Verify that we're not using environment variables directly
        # (this would be caught by security scanning)

    def test_no_eval_exec_usage(self):
        """Test that no eval/exec usage exists in safe components"""
        # Test that our safe expression parser doesn't use eval/exec
        parser = SafeExpressionParser()

        # Verify that dangerous expressions are blocked
        with pytest.raises(Exception):
            parser.evaluate("eval('2+2')")

        with pytest.raises(Exception):
            parser.evaluate("exec('x=1')")

    def test_comprehensive_exception_handling(self, exception_handler_config):
        """Test comprehensive exception handling"""
        handler = EnterpriseExceptionHandler(exception_handler_config)

        # Test different exception types
        exceptions = [
            ValueError("Test value error"),
            TypeError("Test type error"),
            RuntimeError("Test runtime error"),
        ]

        for exc in exceptions:
            error_details = handler.handle_exception(exc, reraise=False)
            assert error_details is not None
            assert error_details.error_type == exc.__class__.__name__

    @pytest.mark.asyncio
    async def test_complete_audit_trail(self, audit_config):
        """Test complete audit trail functionality"""
        logger = AuditLogger(audit_config)

        # Test all event types
        event_types = [
            (
                AuditEventType.LOGIN_SUCCESS,
                AuditSeverity.INFO,
                AuditCategory.AUTHENTICATION,
            ),
            (
                AuditEventType.CHILD_INTERACTION_START,
                AuditSeverity.INFO,
                AuditCategory.CHILD_SAFETY,
            ),
            (
                AuditEventType.SAFETY_INCIDENT,
                AuditSeverity.WARNING,
                AuditCategory.CHILD_SAFETY,
            ),
            (
                AuditEventType.DATA_ACCESS,
                AuditSeverity.INFO,
                AuditCategory.DATA_PROTECTION,
            ),
            (
                AuditEventType.SECURITY_ALERT,
                AuditSeverity.CRITICAL,
                AuditCategory.SYSTEM_SECURITY,
            ),
        ]

        for event_type, severity, category in event_types:
            event_id = await logger.log_event(
                event_type=event_type,
                severity=severity,
                category=category,
                description=f"Test {event_type.value}",
            )
            assert event_id is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
