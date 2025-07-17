# Error Handling Strategy Guide
 Created comprehensive error handling framework

## Overview

The error handling framework provides:
- Consistent error types with severity and categories
- Automatic error logging and tracking
- Child safety-specific error handling
- Retry logic for transient failures
- User-friendly error messages

## Error Type Hierarchy

```
BaseApplicationError
├── ValidationError
│   └── ChildSafetyValidationError
├── AuthenticationError
├── AuthorizationError
│   └── ParentalConsentError
├── BusinessLogicError
│   ├── ChildProfileNotFoundError
│   └── ConversationLimitExceededError
├── ExternalServiceError
│   ├── AIServiceError
│   └── TTSServiceError
├── DatabaseError
│   └── DatabaseConnectionError
└── SystemError
    └── ConfigurationError
```

## Usage Examples

### 1. Raising Custom Errors

```python
from src.infrastructure.error_handling import (
    ValidationError,
    ChildSafetyValidationError,
    BusinessLogicError
)

# Basic validation error
if not user_input:
    raise ValidationError("Input is required", field="message")

# Child safety violation
if contains_inappropriate_content(message):
    raise ChildSafetyValidationError(
        "Message contains inappropriate content",
        details={"detected_words": ["bad_word"]}
    )

# Business logic error
if child_age > 13:
    raise BusinessLogicError(
        "Child age exceeds COPPA limit",
        rule="COPPA_AGE_LIMIT",
        user_message="This service is for children 13 and under."
    )
```

### 2. Using Error Decorators

```python
from src.infrastructure.error_handling import (
    handle_errors,
    retry_on_error,
    safe_execution,
    validate_result
)

# Map exceptions to application errors
@handle_errors(
    (ValueError, ValidationError),
    (KeyError, BusinessLogicError),
    default_error=SystemError
)
async def process_input(data: dict):
    # ValueError will be mapped to ValidationError
    # KeyError will be mapped to BusinessLogicError
    # Other errors will be mapped to SystemError
    pass

# Retry on external service errors
@retry_on_error(
    max_retries=3,
    retry_exceptions=(ExternalServiceError,),
    delay=1.0,
    backoff=2.0
)
async def call_openai_api():
    # Will retry up to 3 times on ExternalServiceError
    pass

# Safe execution with fallback
@safe_execution(fallback_value=[], log_errors=True)
async def get_optional_data():
    # Returns [] if any error occurs
    pass

# Validate result
@validate_result(
    validator=lambda x: x is not None and len(x) > 0,
    error_class=BusinessLogicError,
    error_message="No results found"
)
async def get_required_data():
    # Raises BusinessLogicError if result is empty
    pass
```

### 3. FastAPI Integration

```python
from fastapi import FastAPI
from src.infrastructure.error_handling import global_exception_handler

app = FastAPI()

# Register global exception handler
app.add_exception_handler(Exception, global_exception_handler)

# Errors will automatically be converted to appropriate HTTP responses:
# - ValidationError → 400 Bad Request
# - AuthenticationError → 401 Unauthorized
# - AuthorizationError → 403 Forbidden
# - Not Found errors → 404 Not Found
# - ExternalServiceError → 502 Bad Gateway
# - DatabaseError → 503 Service Unavailable
# - Others → 500 Internal Server Error
```

### 4. Child Safety Error Handling

```python
from src.infrastructure.error_handling import child_safety_error_handler

# Register callback for child safety violations
async def handle_safety_violation(error, context):
    # Send alert to parents
    await notify_parents(error.details)
    
    # Log to compliance system
    await log_coppa_violation(error)

child_safety_error_handler.register_callback(
    ErrorCategory.CHILD_SAFETY,
    handle_safety_violation
)
```

## Error Response Format

All errors return consistent JSON responses:

```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input provided.",
        "category": "validation",
        "severity": "low",
        "details": {
            "field": "email",
            "reason": "Invalid email format"
        }
    }
}
```

## Best Practices

1. **Always use specific error types** instead of generic exceptions
2. **Provide user-friendly messages** that don't expose internals
3. **Include relevant details** in the error for debugging
4. **Use appropriate severity levels**:
   - LOW: User errors, validation issues
   - MEDIUM: Business logic violations, auth failures
   - HIGH: External service failures, child safety issues
   - CRITICAL: System failures, data integrity issues

5. **Handle errors at appropriate levels**:
   - Use decorators for consistent handling
   - Let errors bubble up to global handlers
   - Don't catch and suppress errors silently

## Testing Error Handling

```python
import pytest
from src.infrastructure.error_handling import ValidationError

async def test_validation_error():
    with pytest.raises(ValidationError) as exc_info:
        raise ValidationError("Test error", field="test_field")
    
    error = exc_info.value
    assert error.error_code == "VALIDATION_ERROR"
    assert error.details["field"] == "test_field"
    assert error.to_dict()["error"]["message"] == "Invalid input provided."
```

## Monitoring and Alerts

The error handlers automatically:
- Log errors with appropriate levels
- Track error counts and patterns
- Alert on critical child safety violations
- Provide error statistics via `get_error_stats()`

## Migration from Old Error Handling

Replace generic exception handling:

```python
# Old
try:
    result = process_data()
except Exception as e:
    logger.error(f"Error: {e}")
    return {"error": "Something went wrong"}

# New
from src.infrastructure.error_handling import handle_errors, SystemError

@handle_errors(default_error=SystemError)
async def process_data():
    # Errors are automatically logged and formatted
    pass
```