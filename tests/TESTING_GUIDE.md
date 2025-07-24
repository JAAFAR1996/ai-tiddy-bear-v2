# Testing Guide for AI Teddy Bear
 Created comprehensive test infrastructure

## Overview

The test infrastructure provides:
- Multiple test suites (unit, integration, e2e, security, child safety)
- Comprehensive fixtures for all components
- Test runner with advanced features
- Coverage reporting with minimum thresholds
- Security and COPPA compliance validation

## Running Tests

### Basic Commands

```bash
# Run all tests
python tests/run_tests.py

# Run specific test suite
python tests/run_tests.py unit
python tests/run_tests.py integration
python tests/run_tests.py security
python tests/run_tests.py child_safety

# Run with options
python tests/run_tests.py unit -v          # Verbose
python tests/run_tests.py unit -x          # Stop on first failure
python tests/run_tests.py unit -n 4        # Run in parallel

# Run specific tests by keyword
python tests/run_tests.py -k "security"

# Generate coverage report
python tests/run_tests.py coverage
```

### Special Test Commands

```bash
# Run comprehensive security scan
python tests/run_tests.py security-scan

# Validate child safety compliance
python tests/run_tests.py child-safety-validation
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── run_tests.py            # Test runner
├── unit/                   # Unit tests
│   ├── test_domain/       # Domain layer tests
│   ├── test_application/  # Application layer tests
│   └── test_infrastructure/ # Infrastructure tests
├── integration/           # Integration tests
├── e2e/                  # End-to-end tests
├── security/             # Security tests
└── performance/          # Performance tests
```

## Writing Tests

### 1. Unit Tests

```python
import pytest
from src.domain.entities.child import Child

@pytest.mark.unit
class TestChild:
    def test_create_child(self, sample_child_data):
        child = Child(**sample_child_data)
        assert child.name == sample_child_data["name"]
        assert child.age == sample_child_data["age"]

    def test_child_age_validation(self):
        with pytest.raises(ValueError):
            Child(name="Test", age=14)  # Over COPPA limit
```

### 2. Integration Tests

```python
@pytest.mark.integration
class TestAudioProcessing:
    @pytest.mark.asyncio
    async def test_process_audio_flow(
        self,
        test_client,
        auth_headers,
        audio_file_data,
        mock_ai_service
    ):
        response = await test_client.post(
            "/api/v1/process-audio",
            files={"audio": audio_file_data},
            headers=auth_headers
        )
        assert response.status_code == 200
        assert "response" in response.json()
```

### 3. Security Tests

```python
@pytest.mark.security
class TestSQLInjectionPrevention:
    @pytest.mark.asyncio
    async def test_sql_injection_blocked(self, security_service):
        malicious_input = "'; DROP TABLE users; --"
        result = await security_service.analyze_threat(malicious_input)
        assert result["threat_detected"] is True
        assert result["severity"] == "critical"
```

### 4. Child Safety Tests

```python
@pytest.mark.child_safety
class TestContentModeration:
    def test_inappropriate_content_blocked(self, assert_helpers):
        content = "This contains violence and scary content"
        with pytest.raises(ChildSafetyValidationError):
            validate_child_content(content)
```

## Available Fixtures

### Core Fixtures

- `test_settings` - Test environment settings
- `test_container` - Dependency injection container
- `test_database` - Test database with automatic cleanup
- `db_session` - Database session for tests

### Domain Fixtures

- `sample_child` - Sample child entity
- `sample_child_data` - Sample child data dict
- `sample_parent` - Sample parent data

### Mock Service Fixtures

- `mock_ai_service` - Mock AI service
- `mock_auth_service` - Mock authentication service
- `mock_security_service` - Mock security service
- `mock_cache_service` - Mock cache service
- `mock_coppa_service` - Mock COPPA compliance service

### API Testing Fixtures

- `test_client` - FastAPI test client
- `auth_headers` - Authentication headers
- `audio_file_data` - Sample audio file
- `conversation_data` - Sample conversation

### Utility Fixtures

- `assert_helpers` - Custom assertion helpers
- `benchmark_async` - Async performance benchmarking
- `cleanup_tasks` - Async task cleanup

## Test Markers

Use markers to categorize and filter tests:

```python
# Mark test categories
@pytest.mark.unit
@pytest.mark.security
@pytest.mark.child_safety
@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.e2e

# Skip tests conditionally
@pytest.mark.skipif(not has_redis(), reason="Redis not available")

# Expected failures
@pytest.mark.xfail(reason="Feature not implemented yet")
```

## Coverage Requirements

Each test suite has minimum coverage requirements:

- Unit Tests: 80%
- Integration Tests: 70%
- Security Tests: 90%
- Child Safety Tests: 95%

Run coverage report:

```bash
# Generate HTML coverage report
python tests/run_tests.py coverage

# View report
open htmlcov/index.html
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Use Fixtures**: Don't repeat setup code
3. **Clear Naming**: Test names should describe what they test
4. **Arrange-Act-Assert**: Follow AAA pattern
5. **Mock External Services**: Don't make real API calls
6. **Test Edge Cases**: Include boundary and error conditions
7. **Child Safety First**: Always test child safety implications

## Testing Child Safety Features

Child safety is critical. Always test:

1. **Content Filtering**: Inappropriate content is blocked
2. **Age Verification**: Age limits are enforced
3. **Parental Consent**: Consent is required and validated
4. **Data Encryption**: Child data is properly encrypted
5. **Audit Logging**: All child interactions are logged

Example:

```python
@pytest.mark.child_safety
async def test_child_data_encryption(child_safety_service):
    sensitive_data = {"name": "Child", "age": 8}
    encrypted = await child_safety_service.encrypt_child_data(sensitive_data)

    # Verify encryption
    assert encrypted != sensitive_data
    assert "name" not in str(encrypted)

    # Verify decryption
    decrypted = await child_safety_service.decrypt_child_data(encrypted)
    assert decrypted == sensitive_data
```

## Continuous Integration

The test suite is designed for CI/CD:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    python tests/run_tests.py unit
    python tests/run_tests.py integration
    python tests/run_tests.py security-scan
    python tests/run_tests.py child-safety-validation

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
    fail_ci_if_error: true
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure PYTHONPATH includes project root
2. **Database Errors**: Check test database is accessible
3. **Async Warnings**: Use `pytest-asyncio` markers
4. **Fixture Not Found**: Check fixture scope and imports

### Debug Mode

Run tests with debugging:

```bash
# Run with pdb on failure
pytest --pdb

# Run with detailed output
pytest -vvs

# Run specific test with print statements
pytest -s -k "test_name"
```
