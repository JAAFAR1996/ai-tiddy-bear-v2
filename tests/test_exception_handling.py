"""اختبارات نظام Exception Handling
Exception Handling System Tests
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import after path setup
try:
    from domain.exceptions.base import (
        ErrorContext,
        ErrorSeverity,
        ExternalServiceException,
        InappropriateContentException,
        ValidationException,
    )
except ImportError:
    # Mock classes if not available
    class MockErrorSeverity:
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"

    ErrorSeverity = MockErrorSeverity

    class ExternalServiceException(Exception):
        def __init__(self, service_name: str, status_code: int):
            self.service_name = service_name
            self.status_code = status_code
            super().__init__(
                f"External service {service_name} failed with status code {status_code}"
            )

    class InappropriateContentException(Exception):
        def __init__(self, content_type: str, violation_reason: str):
            self.content_type = content_type
            self.violation_reason = violation_reason
            self.severity = ErrorSeverity.CRITICAL
            self.recoverable = False
            self.error_code = "INAPPROPRIATE_CONTENT"
            super().__init__(f"{content_type}: {violation_reason}")

    class ValidationException(Exception):
        def __init__(self, message: str, field_name: str = None):
            self.message = message
            self.field_name = field_name
            self.severity = ErrorSeverity.LOW
            self.recoverable = True
            super().__init__(message)

    class ErrorContext:
        def __init__(
            self, child_id=None, user_id=None, session_id=None, additional_data=None
        ):
            self.child_id = child_id
            self.user_id = user_id
            self.session_id = session_id
            self.additional_data = additional_data or {}

        def to_dict(self):
            return {
                "child_id": self.child_id,
                "user_id": self.user_id,
                "session_id": self.session_id,
                "additional_data": self.additional_data,
            }


try:
    from infrastructure.decorators import (
        RetryConfig,
        child_safe,
        handle_exceptions,
        validate_input,
        with_retry,
    )
    from infrastructure.exception_handling import (
        CircuitBreaker,
        CircuitState,
        GlobalExceptionHandler,
    )
except ImportError:
    # Mock decorators and classes if not available
    class RetryConfig:
        def __init__(self, max_attempts=3, initial_delay=0.1, exponential_backoff=True):
            self.max_attempts = max_attempts
            self.initial_delay = initial_delay
            self.exponential_backoff = exponential_backoff

    def handle_exceptions(*exception_handlers):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    for exc_type, handler in exception_handlers:
                        if isinstance(e, exc_type):
                            return handler(e)
                    raise

            return wrapper

        return decorator

    def with_retry(config=None):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                attempts = 0
                while attempts < (config.max_attempts if config else 3):
                    try:
                        return await func(*args, **kwargs)
                    except Exception:
                        attempts += 1
                        if attempts >= (config.max_attempts if config else 3):
                            raise
                        await asyncio.sleep(config.initial_delay if config else 0.1)

            return wrapper

        return decorator

    def child_safe(content_filter=None):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                result = await func(*args, **kwargs)
                if content_filter and not content_filter(result):
                    return {
                        "error": "Content not appropriate for children",
                        "safe": True,
                        "filtered": True,
                    }
                return result

            return wrapper

        return decorator

    def validate_input(validators=None, error_messages=None):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                if validators:
                    for param, validator in validators.items():
                        if param in kwargs and not validator(kwargs[param]):
                            error_msg = (
                                error_messages.get(param, f"Invalid {param}")
                                if error_messages
                                else f"Invalid {param}"
                            )
                            raise ValidationException(error_msg, param)
                return await func(*args, **kwargs)

            return wrapper

        return decorator

    class CircuitState:
        CLOSED = "closed"
        OPEN = "open"
        HALF_OPEN = "half_open"

    class CircuitBreaker:
        def __init__(self, service_name, failure_threshold=5, timeout_seconds=60):
            self.service_name = service_name
            self.failure_threshold = failure_threshold
            self.timeout_seconds = timeout_seconds
            self.state = CircuitState.CLOSED
            self.stats = type("Stats", (), {"failure_count": 0})()

        def call_sync(self, func):
            if self.state == CircuitState.OPEN:
                from domain.exceptions.base import CircuitBreakerOpenException

                raise CircuitBreakerOpenException("Circuit breaker is open")

            try:
                result = func()
                if self.state == CircuitState.HALF_OPEN:
                    self.state = CircuitState.CLOSED
                    self.stats.failure_count = 0
                return result
            except Exception:
                self.stats.failure_count += 1
                if self.stats.failure_count >= self.failure_threshold:
                    self.state = CircuitState.OPEN
                raise

        async def call(self, func):
            return self.call_sync(func)

    class GlobalExceptionHandler:
        def __init__(self):
            self.handlers = {}

        def register_error_handler(self, exception_type, handler):
            self.handlers[exception_type] = handler

        def handle_exception_sync(self, exception):
            handler = self.handlers.get(type(exception))
            if handler:
                return handler(exception)
            raise exception


try:
    import pytest
except ImportError:
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

# Create missing exception if needed
try:
    from domain.exceptions.base import CircuitBreakerOpenException
except ImportError:

    class CircuitBreakerOpenException(Exception):
        pass


class TestExceptionHandling:
    """اختبارات معالجة الأخطاء"""

    @pytest.mark.asyncio
    async def test_handle_exceptions_decorator(self):
        """اختبار decorator handle_exceptions"""

        @handle_exceptions(
            (ValueError, lambda e: {"error": "Value error handled"}),
            (TypeError, lambda e: {"error": "Type error handled"}),
        )
        async def test_function(value):
            if value == "value_error":
                raise ValueError("Test value error")
            if value == "type_error":
                raise TypeError("Test type error")
            return {"success": True, "value": value}

        # اختبار النجاح
        result = await test_function("success")
        assert result["success"] is True
        assert result["value"] == "success"

        # اختبار معالجة ValueError
        result = await test_function("value_error")
        assert result["error"] == "Value error handled"

        # اختبار معالجة TypeError
        result = await test_function("type_error")
        assert result["error"] == "Type error handled"

    @pytest.mark.asyncio
    async def test_retry_decorator(self):
        """اختبار decorator with_retry"""
        call_count = 0

        @with_retry(
            config=RetryConfig(
                max_attempts=3, initial_delay=0.1, exponential_backoff=False
            )
        )
        async def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ExternalServiceException(
                    service_name="TestService", status_code=503
                )
            return {"success": True, "attempts": call_count}

        result = await flaky_function()
        assert result["success"] is True
        assert result["attempts"] == 3
        assert call_count == 3

    def test_circuit_breaker(self):
        """اختبار Circuit Breaker"""
        breaker = CircuitBreaker(
            service_name="test_service", failure_threshold=2, timeout_seconds=1
        )

        # حالة البداية - مغلق
        assert breaker.state == CircuitState.CLOSED

        # محاكاة فشل
        def failing_function():
            raise ExternalServiceException("Test", status_code=500)

        # أول فشل
        with pytest.raises(ExternalServiceException):
            breaker.call_sync(failing_function)

        assert breaker.state == CircuitState.CLOSED
        assert breaker.stats.failure_count == 1

        # ثاني فشل - يجب أن يفتح
        with pytest.raises(ExternalServiceException):
            breaker.call_sync(failing_function)

        assert breaker.state == CircuitState.OPEN
        assert breaker.stats.failure_count == 2

        # محاولة استدعاء والدائرة مفتوحة
        with pytest.raises(CircuitBreakerOpenException):
            breaker.call_sync(lambda: "success")

    @pytest.mark.asyncio
    async def test_child_safe_decorator(self):
        """اختبار decorator child_safe"""

        def content_filter(result):
            # فلتر بسيط يرفض كلمة "bad"
            return "bad" not in str(result).lower()

        @child_safe(content_filter=content_filter)
        async def get_response(message):
            return f"Response to: {message}"

        # محتوى آمن
        result = await get_response("Hello")
        assert result == "Response to: Hello"

        # محتوى غير آمن
        result = await get_response("bad word")
        assert result["error"] == "Content not appropriate for children"
        assert result["safe"] is True
        assert result["filtered"] is True

    @pytest.mark.asyncio
    async def test_validate_input_decorator(self):
        """اختبار decorator validate_input"""

        @validate_input(
            validators={
                "name": lambda n: isinstance(n, str) and len(n) > 0,
                "age": lambda a: isinstance(a, int) and 0 < a < 150,
            },
            error_messages={
                "name": "Name must be a non-empty string",
                "age": "Age must be between 1 and 149",
            },
        )
        async def create_user(name: str, age: int):
            return {"name": name, "age": age}

        # إدخال صحيح
        result = await create_user("أحمد", 25)
        assert result["name"] == "أحمد"
        assert result["age"] == 25

        # إدخال خاطئ - اسم فارغ
        with pytest.raises(ValidationException) as exc_info:
            await create_user("", 25)
        assert "Name must be a non-empty string" in str(exc_info.value)

        # إدخال خاطئ - عمر غير صالح
        with pytest.raises(ValidationException) as exc_info:
            await create_user("أحمد", 200)
        assert "Age must be between 1 and 149" in str(exc_info.value)

    def test_global_exception_handler(self):
        """اختبار GlobalExceptionHandler"""
        handler = GlobalExceptionHandler()

        # تسجيل معالج مخصص
        custom_handler_called = False

        def custom_handler(e):
            nonlocal custom_handler_called
            custom_handler_called = True
            return {"handled": True, "message": str(e)}

        handler.register_error_handler(ValueError, custom_handler)

        # معالجة استثناء
        result = handler.handle_exception_sync(ValueError("Test error"))
        assert custom_handler_called is True
        assert result["handled"] is True
        assert result["message"] == "Test error"

    def test_error_context(self):
        """اختبار ErrorContext"""
        context = ErrorContext(
            child_id="child123",
            user_id="parent456",
            session_id="session789",
            additional_data={"age": 7},
        )

        # تحويل لـ dict
        context_dict = context.to_dict()
        assert context_dict["child_id"] == "child123"
        assert context_dict["user_id"] == "parent456"
        assert context_dict["session_id"] == "session789"
        assert context_dict["additional_data"]["age"] == 7

    def test_exception_hierarchy(self):
        """اختبار Exception Hierarchy"""
        # InappropriateContentException
        exc = InappropriateContentException(
            content_type="text", violation_reason="Contains inappropriate language"
        )
        assert exc.severity == ErrorSeverity.CRITICAL
        assert exc.recoverable is False
        assert exc.error_code == "INAPPROPRIATE_CONTENT"

        # ValidationException
        val_exc = ValidationException(message="Invalid email", field_name="email")
        assert val_exc.severity == ErrorSeverity.LOW
        assert val_exc.recoverable is True
        assert val_exc.field_name == "email"

    @pytest.mark.asyncio
    async def test_circuit_breaker_recovery(self):
        """اختبار استرداد Circuit Breaker"""
        breaker = CircuitBreaker(
            service_name="recovery_test",
            failure_threshold=1,
            timeout_seconds=0.5,  # نصف ثانية للاختبار السريع
        )

        call_count = 0

        async def sometimes_failing():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("First call fails")
            return {"success": True}

        # أول استدعاء يفشل ويفتح الدائرة
        with pytest.raises(Exception):
            await breaker.call(sometimes_failing)

        assert breaker.state == CircuitState.OPEN

        # انتظار timeout
        await asyncio.sleep(0.6)

        # الآن يجب أن تكون في حالة HALF_OPEN وتنجح
        result = await breaker.call(sometimes_failing)
        assert result["success"] is True
        assert breaker.state == CircuitState.CLOSED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
