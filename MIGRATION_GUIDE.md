# Migration Guide - Exception System Refactoring

## Overview
We have consolidated all exceptions into a centralized location at `src/common/exceptions/`.

## Old Structure → New Structure

### Application Exceptions
- `src/application/exceptions.py` → `src/common/exceptions/application_exceptions.py`
- `src/infrastructure/error_handling/exceptions.py` → Merged into common exceptions
- `src/infrastructure/exceptions.py` → `src/common/exceptions/infrastructure_exceptions.py`

### Import Changes
```python
# Old
from src.application.exceptions import AITeddyError
from src.infrastructure.exceptions import BaseApplicationException

# New
from src.common.exceptions import AITeddyBaseError, ApplicationException
Exception Hierarchy
AITeddyBaseError (base for all exceptions)
├── DomainException
│   ├── ChildSafetyException
│   ├── ConsentException
│   └── AgeRestrictionException
├── ApplicationException
│   ├── ServiceUnavailableError
│   ├── InvalidInputError
│   ├── TimeoutError
│   └── ResourceNotFoundError
└── InfrastructureException
    ├── DatabaseConnectionError
    ├── ConfigurationError
    ├── ExternalServiceError
    ├── SecurityError
    └── RateLimitExceededError
Benefits

Single source of truth for all exceptions
Clear hierarchy based on architectural layers
Consistent error handling across the application
Easier maintenance and extension
