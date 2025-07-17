# Dependency Injection Migration Guide
 Created simplified DI container to reduce complexity

## Overview

The dependency injection system has been simplified to reduce complexity while maintaining all necessary functionality. The new `SimplifiedContainer` replaces the complex `dependency-injector` based system.

## Key Improvements

1. **No External Dependencies**: Removed requirement for `dependency-injector` library
2. **Clearer Service Registration**: Simple API for registering services
3. **Better Error Messages**: Clear errors when services are missing or misconfigured
4. **Type Safety**: Built-in type checking with `get_typed_service`
5. **Easier Testing**: Simple `reset_container()` for test isolation

## Migration Steps

### 1. Update Imports

**Old:**
```python
from src.infrastructure.di.container import container
```

**New:**
```python
from src.infrastructure.di.simplified_container import get_service, get_typed_service
```

### 2. Getting Services

**Old (Complex):**
```python
# Complex provider resolution
auth_service = container.auth_service()
ai_service = container.openai_client()
```

**New (Simple):**
```python
# Simple service retrieval
auth_service = get_service("auth_service")
ai_service = get_service("ai_service")

# With type checking
from src.infrastructure.security.real_auth_service import RealAuthService
auth_service = get_typed_service("auth_service", RealAuthService)
```

### 3. Registering Custom Services

**Old (Complex):**
```python
# Required complex provider syntax
custom_service = providers.Factory(
    CustomService,
    dependency1=container.service1,
    dependency2=container.service2
)
```

**New (Simple):**
```python
register_service(
    "custom_service",
    lambda dep1, dep2: CustomService(dep1, dep2),
    dependencies={"dep1": "service1", "dep2": "service2"},
    singleton=True
)
```

### 4. Testing

**Old:**
```python
# Complex container override
with container.auth_service.override(mock_auth):
    # test code
```

**New:**
```python
# Simple reset and re-register
reset_container()
register_service("auth_service", lambda: mock_auth)
# test code
reset_container()  # Clean up
```

## Service Names Reference

Core services available in the simplified container:

- `settings` - Application settings
- `security_service` - Unified security service
- `database` - Database connection
- `cache` - Cache service (Redis or Memory)
- `ai_service` - AI service (OpenAI or Mock)
- `auth_service` - Authentication service
- `audio_processing_service` - Audio processing
- `conversation_service` - Conversation management

## Advanced Usage

### Custom Service Registration

```python
# Register a singleton service
register_service(
    "email_service",
    lambda settings: EmailService(settings.smtp_config),
    dependencies={"settings": "settings"},
    singleton=True
)

# Register a factory service (new instance each time)
register_service(
    "request_handler",
    lambda security: RequestHandler(security),
    dependencies={"security": "security_service"},
    singleton=False
)
```

### Debugging Container State

```python
# Get information about all registered services
info = get_container_info()
print(info)
# Output: {
#   "settings": {"singleton": True, "has_instance": True, "dependencies": []},
#   "database": {"singleton": True, "has_instance": False, "dependencies": ["settings"]},
#   ...
# }
```

## Benefits

1. **Reduced Complexity**: ~80% less code for same functionality
2. **No External Dependencies**: Works without `dependency-injector`
3. **Better Performance**: Direct function calls instead of provider resolution
4. **Easier Debugging**: Simple Python code, no magic
5. **Gradual Migration**: Can coexist with old container during transition

## Deprecation Timeline

- **Current**: Both containers available
- **Next Release**: Old container marked as deprecated
- **Future Release**: Old container removed