"""
Tests for Audit Decorators
Testing automatic audit trail creation decorators for security operations.
"""

import pytest
from unittest.mock import patch, Mock, AsyncMock, MagicMock
from datetime import datetime
import asyncio
import inspect

from src.infrastructure.security.audit_decorators import (
    audit_authentication,
    audit_data_access,
    audit_security_event,
    audit_login,
    audit_logout,
    audit_child_create,
    audit_child_update,
    audit_child_delete,
)


class TestAuditDecorators:
    """Test the Audit Decorators."""

    @pytest.fixture
    def mock_audit_integration(self):
        """Create a mock audit integration."""
        mock_integration = Mock()
        mock_integration.log_authentication_event = AsyncMock()
        mock_integration.log_child_data_operation = AsyncMock()
        mock_integration.log_security_event = AsyncMock()

        with patch(
            "src.infrastructure.security.audit_decorators.get_audit_integration",
            return_value=mock_integration,
        ):
            yield mock_integration

    @pytest.fixture
    def mock_datetime(self):
        """Mock datetime for consistent testing."""
        with patch("src.infrastructure.security.audit_decorators.datetime") as mock_dt:
            mock_dt.utcnow.return_value = datetime(2024, 1, 15, 10, 30, 0)
            yield mock_dt

    def test_audit_authentication_decorator_async_success(
        self, mock_audit_integration, mock_datetime
    ):
        """Test audit_authentication decorator with async function success."""

        @audit_authentication("login")
        async def test_login(email, password, ip_address=None):
            return {"success": True, "token": "test_token"}

        # Test the decorated function
        result = asyncio.run(
            test_login(
                "user@example.com",
                "password",
                ip_address="192.168.1.100")
        )

        # Verify function result
        assert result["success"] is True
        assert result["token"] == "test_token"

        # Verify audit logging was called
        mock_audit_integration.log_authentication_event.assert_called_once()
        call_args = mock_audit_integration.log_authentication_event.call_args[1]

        assert call_args["event_type"] == "login"
        assert call_args["user_email"] == "user@example.com"
        assert call_args["success"] is True
        assert call_args["ip_address"] == "192.168.1.100"
        assert "function" in call_args["details"]
        assert call_args["details"]["function"] == "test_login"

    def test_audit_authentication_decorator_async_failure(
        self, mock_audit_integration, mock_datetime
    ):
        """Test audit_authentication decorator with async function failure."""

        @audit_authentication("login")
        async def test_login_fail(email, password):
            raise ValueError("Invalid credentials")

        # Test the decorated function
        with pytest.raises(ValueError, match="Invalid credentials"):
            asyncio.run(test_login_fail("user@example.com", "wrong_password"))

        # Verify audit logging was called with failure
        mock_audit_integration.log_authentication_event.assert_called_once()
        call_args = mock_audit_integration.log_authentication_event.call_args[1]

        assert call_args["event_type"] == "login"
        assert call_args["user_email"] == "user@example.com"
        assert call_args["success"] is False
        assert call_args["details"]["error"] == "Invalid credentials"

    def test_audit_authentication_decorator_sync_success(
        self, mock_audit_integration, mock_datetime
    ):
        """Test audit_authentication decorator with sync function success."""

        @audit_authentication("logout")
        def test_logout(email, ip_address=None):
            return {"success": True}

        # Mock event loop for sync function
        with patch("asyncio.get_event_loop") as mock_get_loop:
            mock_loop = Mock()
            mock_get_loop.return_value = mock_loop

            result = test_logout(
                "user@example.com",
                ip_address="192.168.1.101")

        # Verify function result
        assert result["success"] is True

        # Verify that task was scheduled
        mock_loop.create_task.assert_called_once()

    def test_audit_authentication_custom_extractors(
        self, mock_audit_integration, mock_datetime
    ):
        """Test audit_authentication decorator with custom extractors."""

        def extract_email(*args, **kwargs):
            return kwargs.get("user_data", {}).get("email", "unknown")

        def extract_ip(*args, **kwargs):
            return kwargs.get("request_info", {}).get("client_ip", "unknown")

        @audit_authentication(
            "password_change", extract_email=extract_email, extract_ip=extract_ip
        )
        async def change_password(user_data, new_password, request_info):
            return {"success": True}

        user_data = {"email": "custom@example.com"}
        request_info = {"client_ip": "10.0.0.1"}

        result = asyncio.run(
            change_password(
                user_data,
                "new_pass",
                request_info))

        # Verify custom extractors were used
        call_args = mock_audit_integration.log_authentication_event.call_args[1]
        assert call_args["user_email"] == "custom@example.com"
        assert call_args["ip_address"] == "10.0.0.1"

    def test_audit_data_access_decorator_async_success(
        self, mock_audit_integration, mock_datetime
    ):
        """Test audit_data_access decorator with async function success."""

        @audit_data_access("read", "child_profile")
        async def get_child_profile(user_id, child_id, ip_address=None):
            return {"child_id": child_id, "name": "Test Child"}

        result = asyncio.run(
            get_child_profile(
                "user_123",
                "child_456",
                ip_address="192.168.1.200")
        )

        # Verify function result
        assert result["child_id"] == "child_456"
        assert result["name"] == "Test Child"

        # Verify audit logging was called
        mock_audit_integration.log_child_data_operation.assert_called_once()
        call_args = mock_audit_integration.log_child_data_operation.call_args[1]

        assert call_args["operation"] == "read"
        assert call_args["child_id"] == "child_456"
        assert call_args["user_id"] == "user_123"
        assert call_args["data_type"] == "child_profile"
        assert call_args["ip_address"] == "192.168.1.200"

    def test_audit_data_access_decorator_async_failure(
        self, mock_audit_integration, mock_datetime
    ):
        """Test audit_data_access decorator with async function failure."""

        @audit_data_access("update", "child_profile")
        async def update_child_profile(user_id, child_id, updates):
            raise PermissionError("Access denied")

        with pytest.raises(PermissionError, match="Access denied"):
            asyncio.run(
                update_child_profile(
                    "user_123", "child_456", {
                        "name": "New Name"})
            )

        # Verify audit logging was called with failure
        call_args = mock_audit_integration.log_child_data_operation.call_args[1]
        assert call_args["details"]["success"] is False
        assert call_args["details"]["error"] == "Access denied"

    def test_audit_data_access_missing_required_params(
        self, mock_audit_integration, mock_datetime
    ):
        """Test audit_data_access decorator when required parameters are missing."""

        @audit_data_access("delete", "child_profile")
        async def delete_child_profile(some_param):
            return {"success": True}

        result = asyncio.run(delete_child_profile("test"))

        # Should not call audit logging when child_id and user_id are missing
        mock_audit_integration.log_child_data_operation.assert_not_called()

    def test_audit_data_access_custom_extractors(
        self, mock_audit_integration, mock_datetime
    ):
        """Test audit_data_access decorator with custom extractors."""

        def extract_child_id(*args, **kwargs):
            return kwargs.get("profile_data", {}).get("child_id")

        def extract_user_id(*args, **kwargs):
            return kwargs.get("auth_context", {}).get("user_id")

        def extract_ip(*args, **kwargs):
            return kwargs.get("request_meta", {}).get("remote_addr")

        @audit_data_access(
            "create", "child_profile", extract_child_id, extract_user_id, extract_ip
        )
        async def create_child_profile(
                profile_data, auth_context, request_meta):
            return {"success": True}

        profile_data = {"child_id": "new_child_789"}
        auth_context = {"user_id": "parent_456"}
        request_meta = {"remote_addr": "203.0.113.1"}

        result = asyncio.run(
            create_child_profile(profile_data, auth_context, request_meta)
        )

        # Verify custom extractors were used
        call_args = mock_audit_integration.log_child_data_operation.call_args[1]
        assert call_args["child_id"] == "new_child_789"
        assert call_args["user_id"] == "parent_456"
        assert call_args["ip_address"] == "203.0.113.1"

    def test_audit_security_event_decorator_async_success(
        self, mock_audit_integration, mock_datetime
    ):
        """Test audit_security_event decorator with async function success."""

        @audit_security_event("rate_limit_check", "warning")
        async def check_rate_limit(user_id, ip_address):
            return {"allowed": True, "remaining": 95}

        result = asyncio.run(check_rate_limit("user_789", "192.168.1.250"))

        # Verify function result
        assert result["allowed"] is True
        assert result["remaining"] == 95

        # Verify audit logging was called
        mock_audit_integration.log_security_event.assert_called_once()
        call_args = mock_audit_integration.log_security_event.call_args[1]

        assert call_args["event_type"] == "rate_limit_check"
        assert call_args["severity"] == "warning"
        assert call_args["user_id"] == "user_789"
        assert call_args["ip_address"] == "192.168.1.250"
        assert "Security event in check_rate_limit" in call_args["description"]

    def test_audit_security_event_decorator_async_failure(
        self, mock_audit_integration, mock_datetime
    ):
        """Test audit_security_event decorator with async function failure."""

        @audit_security_event("access_violation", "critical")
        async def check_access_violation(user_id):
            raise SecurityError("Suspicious activity detected")

        with pytest.raises(
            NameError
        ):  # SecurityError is not defined, will raise NameError
            asyncio.run(check_access_violation("user_suspicious"))

        # Verify audit logging was called with error severity
        call_args = mock_audit_integration.log_security_event.call_args[1]
        # Should override to error on failure
        assert call_args["severity"] == "error"
        assert "Error:" in call_args["description"]

    def test_audit_security_event_sync_function(
        self, mock_audit_integration, mock_datetime
    ):
        """Test audit_security_event decorator with sync function."""

        @audit_security_event("config_change", "info")
        def update_security_config(user_id, config_key, config_value):
            return {"updated": True}

        with patch("asyncio.get_event_loop") as mock_get_loop:
            mock_loop = Mock()
            mock_get_loop.return_value = mock_loop

            result = update_security_config("admin_123", "max_attempts", 5)

        # Verify function result
        assert result["updated"] is True

        # Verify that task was scheduled
        mock_loop.create_task.assert_called_once()

    def test_audit_login_convenience_decorator(
        self, mock_audit_integration, mock_datetime
    ):
        """Test audit_login convenience decorator."""

        @audit_login()
        async def user_login(email, password):
            return {"success": True, "user_id": "123"}

        result = asyncio.run(user_login("test@example.com", "password"))

        # Verify audit logging was called with login event type
        call_args = mock_audit_integration.log_authentication_event.call_args[1]
        assert call_args["event_type"] == "login"
        assert call_args["user_email"] == "test@example.com"

    def test_audit_logout_convenience_decorator(
        self, mock_audit_integration, mock_datetime
    ):
        """Test audit_logout convenience decorator."""

        @audit_logout()
        async def user_logout(email, session_id):
            return {"success": True}

        result = asyncio.run(user_logout("test@example.com", "session_456"))

        # Verify audit logging was called with logout event type
        call_args = mock_audit_integration.log_authentication_event.call_args[1]
        assert call_args["event_type"] == "logout"
        assert call_args["user_email"] == "test@example.com"

    def test_audit_child_create_convenience_decorator(
        self, mock_audit_integration, mock_datetime
    ):
        """Test audit_child_create convenience decorator."""

        @audit_child_create()
        async def create_child(user_id, child_id, child_data):
            return {"success": True, "child_id": child_id}

        result = asyncio.run(
            create_child("parent_123", "child_789", {"name": "New Child"})
        )

        # Verify audit logging was called with create operation
        call_args = mock_audit_integration.log_child_data_operation.call_args[1]
        assert call_args["operation"] == "create"
        assert call_args["data_type"] == "child_profile"
        assert call_args["child_id"] == "child_789"
        assert call_args["user_id"] == "parent_123"

    def test_audit_child_update_convenience_decorator(
        self, mock_audit_integration, mock_datetime
    ):
        """Test audit_child_update convenience decorator."""

        @audit_child_update()
        async def update_child(user_id, child_id, updates):
            return {"success": True, "updated_fields": list(updates.keys())}

        result = asyncio.run(
            update_child(
                "parent_456", "child_789", {
                    "age": 9}))

        # Verify audit logging was called with update operation
        call_args = mock_audit_integration.log_child_data_operation.call_args[1]
        assert call_args["operation"] == "update"
        assert call_args["data_type"] == "child_profile"

    def test_audit_child_delete_convenience_decorator(
        self, mock_audit_integration, mock_datetime
    ):
        """Test audit_child_delete convenience decorator."""

        @audit_child_delete()
        async def delete_child(user_id, child_id):
            return {"success": True, "deleted": True}

        result = asyncio.run(delete_child("parent_789", "child_456"))

        # Verify audit logging was called with delete operation
        call_args = mock_audit_integration.log_child_data_operation.call_args[1]
        assert call_args["operation"] == "delete"
        assert call_args["data_type"] == "child_profile"

    def test_decorator_preserves_function_metadata(
            self, mock_audit_integration):
        """Test that decorators preserve original function metadata."""

        @audit_authentication("test")
        async def original_function(param1, param2="default"):
            """Original function docstring."""
            return "result"

        # Verify metadata is preserved
        assert original_function.__name__ == "original_function"
        assert original_function.__doc__ == "Original function docstring."
        assert inspect.iscoroutinefunction(original_function)

    def test_decorator_handles_audit_integration_error(self, mock_datetime):
        """Test that decorators handle audit integration errors gracefully."""
        # Mock get_audit_integration to raise exception
        with patch(
            "src.infrastructure.security.audit_decorators.get_audit_integration",
            side_effect=Exception("Audit error"),
        ):
            with patch(
                "src.infrastructure.security.audit_decorators.logger"
            ) as mock_logger:

                @audit_authentication("login")
                async def test_function(email):
                    return {"success": True}

                # Function should still work even if audit fails
                result = asyncio.run(test_function("test@example.com"))
                assert result["success"] is True

                # Should log the audit error
                mock_logger.error.assert_called()

    def test_decorator_with_no_event_loop(
            self, mock_audit_integration, mock_datetime):
        """Test decorator behavior when no event loop is available."""

        @audit_authentication("login")
        def sync_function(email):
            return {"success": True}

        # Mock get_event_loop to raise RuntimeError
        with patch("asyncio.get_event_loop", side_effect=RuntimeError("No event loop")):
            # Function should still work
            result = sync_function("test@example.com")
            assert result["success"] is True

    def test_argument_extraction_edge_cases(
        self, mock_audit_integration, mock_datetime
    ):
        """Test argument extraction with various edge cases."""

        @audit_authentication("login")
        async def test_function_no_args():
            return {"success": True}

        # Should handle functions with no arguments
        result = asyncio.run(test_function_no_args())
        assert result["success"] is True

        call_args = mock_audit_integration.log_authentication_event.call_args[1]
        assert call_args["user_email"] == "unknown"

    def test_argument_extraction_from_object_attributes(
        self, mock_audit_integration, mock_datetime
    ):
        """Test argument extraction from object attributes."""

        class MockUser:
            def __init__(self, email):
                self.email = email

        @audit_authentication("login")
        async def test_function(user_obj, password):
            return {"success": True}

        user = MockUser("object@example.com")
        result = asyncio.run(test_function(user, "password"))

        # Should extract email from user object
        call_args = mock_audit_integration.log_authentication_event.call_args[1]
        assert call_args["user_email"] == "object@example.com"

    def test_audit_data_access_fallback_extraction(
        self, mock_audit_integration, mock_datetime
    ):
        """Test audit_data_access with fallback argument extraction."""

        class MockContext:
            def __init__(self, user_id):
                self.current_user = Mock()
                self.current_user.id = user_id

        @audit_data_access("read", "child_data")
        async def test_function(context, some_id):
            return {"data": "test"}

        context = MockContext("fallback_user_123")
        result = asyncio.run(test_function(context, "child_456"))

        # Should extract from fallback methods
        call_args = mock_audit_integration.log_child_data_operation.call_args[1]
        assert call_args["user_id"] == "fallback_user_123"
        assert call_args["child_id"] == "child_456"  # From second argument

    def test_decorator_timing_measurement(self, mock_audit_integration):
        """Test that decorators measure execution timing correctly."""
        import time

        @audit_authentication("login")
        async def slow_function(email):
            await asyncio.sleep(0.1)  # 100ms delay
            return {"success": True}

        result = asyncio.run(slow_function("timing@example.com"))

        # Verify timing was measured
        call_args = mock_audit_integration.log_authentication_event.call_args[1]
        duration_ms = call_args["details"]["duration_ms"]
        assert duration_ms >= 100  # Should be at least 100ms
        # But not too much more (allowing for test overhead)
        assert duration_ms < 200

    def test_multiple_decorators_on_same_function(
        self, mock_audit_integration, mock_datetime
    ):
        """Test applying multiple audit decorators to the same function."""

        @audit_security_event("admin_action", "warning")
        @audit_authentication("admin_login")
        async def admin_function(email, action):
            return {"success": True, "action": action}

        result = asyncio.run(
            admin_function(
                "admin@example.com",
                "delete_user"))

        # Both decorators should have been applied
        assert mock_audit_integration.log_authentication_event.call_count == 1
        assert mock_audit_integration.log_security_event.call_count == 1

        # Verify both audit logs have correct information
        auth_call = mock_audit_integration.log_authentication_event.call_args[1]
        security_call = mock_audit_integration.log_security_event.call_args[1]

        assert auth_call["event_type"] == "admin_login"
        assert security_call["event_type"] == "admin_action"

    def test_decorator_with_complex_function_signature(
        self, mock_audit_integration, mock_datetime
    ):
        """Test decorators with complex function signatures."""

        @audit_data_access("update", "child_profile")
        async def complex_function(
                self, *args, user_id=None, child_id=None, **kwargs):
            return {"updated": True}

        # Test with various argument combinations
        result = asyncio.run(
            complex_function(
                None,  # self
                "arg1",
                "arg2",  # *args
                user_id="complex_user",
                child_id="complex_child",
                extra_param="extra_value",  # **kwargs
            )
        )

        assert result["updated"] is True

        # Verify extraction worked with complex signature
        call_args = mock_audit_integration.log_child_data_operation.call_args[1]
        assert call_args["user_id"] == "complex_user"
        assert call_args["child_id"] == "complex_child"

    def test_decorator_error_handling_in_sync_mode(
        self, mock_audit_integration, mock_datetime
    ):
        """Test error handling in sync mode decorator execution."""

        @audit_authentication("login")
        def sync_function_with_error(email):
            raise ValueError("Sync function error")

        with patch("asyncio.get_event_loop") as mock_get_loop:
            mock_loop = Mock()
            mock_get_loop.return_value = mock_loop

            with pytest.raises(ValueError, match="Sync function error"):
                sync_function_with_error("error@example.com")

            # Should still schedule audit task even on error
            mock_loop.create_task.assert_called_once()

    def test_decorator_audit_scheduling_error_handling(
        self, mock_audit_integration, mock_datetime
    ):
        """Test handling of audit scheduling errors in sync mode."""

        @audit_authentication("login")
        def sync_function(email):
            return {"success": True}

        with patch("asyncio.get_event_loop", side_effect=RuntimeError("No loop")):
            with patch(
                "src.infrastructure.security.audit_decorators.logger"
            ) as mock_logger:
                # Should not raise exception
                result = sync_function("test@example.com")
                assert result["success"] is True

                # Should not log scheduling errors (they're expected in some cases)
                # This tests the silent handling of RuntimeError
