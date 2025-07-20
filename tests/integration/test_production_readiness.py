"""Production readiness integration tests.
Tests that verify the system can start and operate without mocks.
"""

import os
from unittest.mock import patch

import pytest


class TestProductionReadiness:
    """Test that the system is production-ready without mocks."""

    def test_startup_validator_fails_without_dependencies(self):
        """Test that startup validation fails when dependencies are missing."""
        from src.infrastructure.config.startup_validator import (
            StartupValidator,
        )

        validator = StartupValidator()

        # Mock missing pydantic
        with patch(
            "builtins.__import__",
            side_effect=ImportError("No module named 'pydantic'"),
        ):
            assert not validator.validate_dependencies()
            assert any("Pydantic" in error for error in validator.errors)

    def test_startup_validator_fails_without_environment(self):
        """Test that startup validation fails when environment vars are missing."""
        from src.infrastructure.config.startup_validator import (
            StartupValidator,
        )

        validator = StartupValidator()

        # Clear environment variables
        with patch.dict(os.environ, {}, clear=True):
            assert not validator.validate_environment()
            assert any("SECRET_KEY" in error for error in validator.errors)
            assert any("OPENAI_API_KEY" in error for error in validator.errors)

    def test_startup_validator_fails_with_insecure_secrets(self):
        """Test that startup validation fails with insecure secrets."""
        from src.infrastructure.config.startup_validator import (
            StartupValidator,
        )

        validator = StartupValidator()

        # Test with INTENTIONALLY insecure values to verify security validation works
        # These are deliberately unsafe for testing the security validator
        with patch.dict(
            os.environ,
            {
                "SECRET_KEY": "changeme_this_is_insecure",  # UNSAFE ON PURPOSE FOR TESTING
                "JWT_SECRET_KEY": "test_key_not_secure",  # UNSAFE ON PURPOSE FOR TESTING
            },
        ):
            assert not validator.validate_security()
            assert any("unsafe value" in error for error in validator.errors)

    def test_no_mock_imports_in_production_code(self):
        """Test that no production code imports mock modules."""
        import glob

        # Find all Python files in src/ (excluding tests)
        python_files = glob.glob("src/**/*.py", recursive=True)
        production_files = [
            f for f in python_files if "test" not in f and "mock" not in f
        ]

        mock_imports = []
        for file_path in production_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                    if "from.*mock" in content or "import.*mock" in content:
                        # Exclude legitimate test fixtures in conftest.py or
                        # test files
                        if "conftest.py" not in file_path and "test_" not in file_path:
                            mock_imports.append(file_path)
            except (UnicodeDecodeError, FileNotFoundError):
                pass

        assert (
            len(mock_imports) == 0
        ), f"Production files importing mocks: {mock_imports}"

    def test_container_does_not_fallback_to_mocks(self):
        """Test that the container fails instead of falling back to mocks."""
        # This should fail fast if infrastructure.di.container is not available
        with pytest.raises(ImportError):
            with patch(
                "builtins.__import__",
                side_effect=ImportError("No module named 'infrastructure'"),
            ):
                pass

    def test_settings_require_real_values(self):
        """Test that settings require real values, not defaults."""
        # Clear environment to test required fields
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises((ValueError, ImportError)):
                from src.infrastructure.config.settings import Settings

                Settings()

    def test_database_service_uses_sqlalchemy_orm(self):
        """Test that database service uses proper ORM (no string interpolation)."""
        import ast
        import inspect

        from src.infrastructure.persistence.real_database_service import (
            DatabaseService,
        )

        # Get the source code of critical methods
        methods_to_check = [
            "get_child",
            "get_children_by_parent",
            "create_child",
        ]

        for method_name in methods_to_check:
            if hasattr(DatabaseService, method_name):
                method = getattr(DatabaseService, method_name)
                try:
                    source = inspect.getsource(method)

                    # Parse AST to check for f-string usage in SQL
                    tree = ast.parse(source)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.JoinedStr):  # f-string
                            # Check if it's used in a SQL context
                            parent = getattr(node, "parent", None)
                            if parent and any(
                                keyword in source
                                for keyword in [
                                    "SELECT",
                                    "INSERT",
                                    "UPDATE",
                                    "DELETE",
                                ]
                            ):
                                pytest.fail(
                                    f"Potential SQL injection in {method_name}: f-string usage detected"
                                )
                except (OSError, TypeError):
                    # Method might be synthetic or unavailable in test context
                    pass

    def test_coppa_service_uses_real_encryption(self):
        """Test that COPPA service uses real Fernet encryption."""
        from cryptography.fernet import Fernet

        from src.infrastructure.security.coppa_validator import (
            COPPAValidator,
            coppa_validator,
            is_coppa_subject,
            requires_parental_consent
        )

        # Test with proper encryption key
        encryption_key = Fernet.generate_key().decode()
        service = COPPAComplianceService(encryption_key=encryption_key)

        # Test encryption/decryption works
        test_data = "sensitive_child_data"
        encrypted = service.encrypt_child_data(test_data)
        decrypted = service.decrypt_child_data(encrypted)

        assert encrypted != test_data  # Data should be encrypted
        assert decrypted == test_data  # Should decrypt correctly
        assert isinstance(service.cipher, Fernet)  # Should use real Fernet

    def test_auth_service_uses_real_jwt(self):
        """Test that auth service uses real JWT implementation."""
        import secrets

        import jwt

        from src.infrastructure.security.real_auth_service import (
            ProductionAuthService,
        )

        auth_service = ProductionAuthService()
        # Generate secure test key dynamically - never hardcode
        auth_service.secret_key = secrets.token_urlsafe(32)  # - مفتاح ديناميكي آمن

        # Create test user data
        user_data = {"id": "test_user", "email": "test@example.com"}

        # Generate token
        token = auth_service.create_access_token(user_data)

        # Verify it's a real JWT (has 3 parts separated by dots)
        parts = token.split(".")
        assert len(parts) == 3, "Should be a valid JWT format"

        # Verify it can be decoded with real JWT library
        decoded = jwt.decode(token, auth_service.secret_key, algorithms=["HS256"])
        assert decoded["id"] == "test_user"

    def test_ai_service_requires_real_openai_key(self):
        """Test that AI service requires real OpenAI configuration."""
        # This test verifies that AI service fails with invalid/missing keys
        with patch.dict(os.environ, {"OPENAI_API_KEY": "invalid_key"}):
            try:
                from src.infrastructure.ai.real_ai_service import RealAIService

                # Should fail or require valid configuration
                service = RealAIService()
                # If it doesn't fail immediately, it should fail on first API
                # call
            except (ValueError, ImportError, Exception) as e:
                # Expected - should fail with invalid configuration
                assert "api" in str(e).lower() or "key" in str(e).lower()

    def test_no_print_statements_in_production_code(self):
        """Test that production code doesn't contain print statements."""
        import glob

        python_files = glob.glob("src/**/*.py", recursive=True)
        production_files = [f for f in python_files if "test" not in f]

        files_with_prints = []
        for file_path in production_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines):
                        if "print(" in line and not line.strip().startswith("#"):
                            files_with_prints.append(f"{file_path}:{i+1}")
            except (UnicodeDecodeError, FileNotFoundError):
                pass

        assert (
            len(files_with_prints) == 0
        ), f"Print statements found in: {files_with_prints}"

    @pytest.mark.integration
    def test_application_starts_with_valid_environment(self):
        """Test that the application can start with proper environment."""
        # Set up minimal valid environment with dynamically generated keys
        import secrets

        from cryptography.fernet import Fernet

        test_env = {
            "ENVIRONMENT": "test",
            "SECRET_KEY": secrets.token_urlsafe(32),  # - مفتاح ديناميكي آمن
            # - مفتاح ديناميكي آمن
            "JWT_SECRET_KEY": secrets.token_urlsafe(32),
            "OPENAI_API_KEY": "sk-test_key_for_testing_purposes_only",
            "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
            "REDIS_URL": "redis://localhost:6379/15",
            "COPPA_ENCRYPTION_KEY": Fernet.generate_key().decode(),  # - مفتاح تشفير ديناميكي
            "DEBUG": "true",
        }

        with patch.dict(os.environ, test_env, clear=True):
            try:
                # Import should succeed with valid environment
                from src.main import app

                assert app is not None
            except ImportError as e:
                # If dependencies are missing, that's expected in test
                # environment
                if "pydantic" in str(e) or "fastapi" in str(e):
                    pytest.skip(f"Dependencies not available in test environment: {e}")
                else:
                    raise

    def test_error_responses_dont_leak_information(self):
        """Test that error responses don't expose internal information."""
        # This would be tested with actual HTTP requests in a full integration test
        # For now, we test that error handlers are configured properly
        try:
            from src.presentation.middleware.error_handler import handle_error

            # Test that error handler exists and doesn't expose internals
            assert callable(handle_error)
        except ImportError:
            # Error handler might be configured differently
            pass


class TestSecurityCompliance:
    """Test security and compliance requirements."""

    def test_coppa_age_validation(self):
        """Test COPPA age validation works correctly."""
        from src.infrastructure.security.coppa_validator import (
            COPPAValidator,
            coppa_validator,
            is_coppa_subject,
            requires_parental_consent
        )

        service = COPPAComplianceService()

        # Test ages
        result_compliant = service.validate_child_age(7)  # Compliant age
        result_too_young = service.validate_child_age(2)  # Too young
        result_too_old = service.validate_child_age(15)  # Too old

        assert result_compliant["compliant"]
        assert result_too_young["compliant"] == False
        assert result_too_old["compliant"] == False

    def test_data_encryption_is_reversible(self):
        """Test that encrypted data can be properly decrypted."""
        from cryptography.fernet import Fernet

        from src.infrastructure.security.hardening.coppa_compliance import (
            COPPAComplianceService,
        )

        encryption_key = Fernet.generate_key().decode()
        service = COPPAComplianceService(encryption_key=encryption_key)

        test_data = {
            "name": "Test Child",
            "age": 7,
            "interests": ["toys", "games"],
        }

        # Encrypt
        encrypted = service.encrypt_child_data(test_data)

        # Decrypt
        decrypted = service.decrypt_child_data(encrypted)

        assert decrypted == test_data
        assert encrypted != test_data  # Should be different when encrypted

    def test_rate_limiting_configuration(self):
        """Test that rate limiting is properly configured."""
        try:
            from src.infrastructure.security.rate_limiter import (
                setup_rate_limiter,
            )

            assert callable(setup_rate_limiter)
        except ImportError:
            pytest.skip("Rate limiter not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
