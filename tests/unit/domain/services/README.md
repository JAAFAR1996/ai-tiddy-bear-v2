# Domain Services Unit Tests

This directory contains comprehensive unit tests for all domain service components in the AI Teddy Bear backend.

## Test Coverage

The following domain services are tested:

1. **COPPA Age Validation Service** (`test_coppa_age_validation.py`)
   - Age validation for COPPA compliance
   - Birthdate validation and age calculation
   - Parental consent requirements
   - Safety level determination
   - Comprehensive edge case testing

2. **Data Retention Service** (`test_data_retention_service.py`)
   - COPPA-compliant data retention policies
   - Age-based retention rules
   - Deletion date calculations
   - Compliance validation
   - Policy consistency checks

3. **Parental Consent Enforcer** (`test_parental_consent_enforcer.py`)
   - Consent requirement validation
   - Age-based consent rules
   - Consent expiration handling
   - Multiple consent type validation
   - COPPA compliance enforcement

4. **Emotion Analyzer** (`test_emotion_analyzer.py`)
   - Text-based emotion detection
   - Voice-based emotion analysis
   - Child-appropriate emotion categorization
   - Safety monitoring (attention requirements)
   - Sentiment and arousal scoring

5. **Safety Validator Protocol** (`test_safety_validator.py`)
   - Protocol interface validation
   - Method signature verification
   - Implementation examples

6. **Age Filter Protocol** (`test_age_filter.py`)
   - Protocol interface validation
   - Method signature verification
   - Implementation examples

## Running the Tests

### Prerequisites

Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

### Run All Domain Service Tests

```bash
# Run all tests in this directory
pytest tests/unit/domain/services/ -v

# Run with coverage
pytest tests/unit/domain/services/ -v --cov=src/domain/services --cov-report=html

# Run in parallel for faster execution
pytest tests/unit/domain/services/ -v -n auto
```

### Run Individual Test Files

```bash
# Test COPPA age validation
pytest tests/unit/domain/services/test_coppa_age_validation.py -v

# Test data retention
pytest tests/unit/domain/services/test_data_retention_service.py -v

# Test parental consent
pytest tests/unit/domain/services/test_parental_consent_enforcer.py -v

# Test emotion analyzer
pytest tests/unit/domain/services/test_emotion_analyzer.py -v

# Test protocols
pytest tests/unit/domain/services/test_safety_validator.py -v
pytest tests/unit/domain/services/test_age_filter.py -v
```

### Run Specific Test Classes or Methods

```bash
# Run a specific test class
pytest tests/unit/domain/services/test_coppa_age_validation.py::TestCOPPAAgeValidator -v

# Run a specific test method
pytest tests/unit/domain/services/test_emotion_analyzer.py::TestEmotionAnalyzer::test_analyze_text_happy_emotions -v
```

### Test Output Options

```bash
# Verbose output with test names
pytest tests/unit/domain/services/ -v

# Show print statements
pytest tests/unit/domain/services/ -v -s

# Generate HTML coverage report
pytest tests/unit/domain/services/ --cov=src/domain/services --cov-report=html
# Open htmlcov/index.html in browser

# Generate terminal coverage report
pytest tests/unit/domain/services/ --cov=src/domain/services --cov-report=term-missing
```

## Test Organization

Each test file follows a consistent structure:

1. **Imports** - Required dependencies and modules under test
2. **Fixtures** - Reusable test data and service instances
3. **Test Classes** - Organized by functionality
4. **Edge Cases** - Comprehensive boundary and error testing

## Key Testing Patterns

### Time-based Testing
Tests use `freezegun` for consistent time-based testing:
```python
@freeze_time("2025-01-15")
def test_time_sensitive_feature():
    # Test with fixed time
```

### Parametrized Testing
Some tests use parametrization for comprehensive coverage:
```python
@pytest.mark.parametrize("age,expected", [
    (5, AgeValidationResult.VALID_CHILD),
    (15, AgeValidationResult.VALID_TEEN),
])
def test_age_validation(age, expected):
    # Test multiple cases
```

### Async Testing
Protocol tests include async method validation:
```python
@pytest.mark.asyncio
async def test_async_protocol_method():
    # Test async functionality
```

## Coverage Goals

- Minimum 80% code coverage for all domain services
- 100% coverage for critical safety and compliance features
- Edge case coverage for all boundary conditions
- Error handling validation

## Contributing

When adding new domain services:

1. Create corresponding test file with `test_` prefix
2. Include comprehensive test cases covering:
   - Normal operation
   - Edge cases
   - Error conditions
   - Integration scenarios
3. Ensure tests are deterministic and repeatable
4. Document any special testing requirements
