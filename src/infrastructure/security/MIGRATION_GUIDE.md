# Security Service Migration Guide
 Created migration guide for consolidating duplicate security services

## Overview

The security module has been refactored to eliminate duplicate services. Three separate services have been consolidated into a single `UnifiedSecurityService`:

- `ComprehensiveSecurityService` → `UnifiedSecurityService`
- `EnhancedSecurityService` → `UnifiedSecurityService`  
- `SecurityManager` → `UnifiedSecurityService`

## Migration Steps

### 1. Update Imports

**Old:**
```python
from src.infrastructure.security.comprehensive_security_service import ComprehensiveSecurityService
from src.infrastructure.security.enhanced_security import EnhancedSecurityService
from src.infrastructure.security.security_manager import SecurityManager
```

**New:**
```python
from src.infrastructure.security import UnifiedSecurityService, SecurityConfig
```

### 2. Update Service Initialization

**Old:**
```python
# Multiple services
comprehensive_security = ComprehensiveSecurityService()
enhanced_security = EnhancedSecurityService(SecurityConfig())
security_manager = SecurityManager()
```

**New:**
```python
# Single unified service
security_service = UnifiedSecurityService(SecurityConfig())
```

### 3. Update Method Calls

The `UnifiedSecurityService` combines all functionality:

#### Threat Detection (from ComprehensiveSecurityService)
```python
# Old
result = await comprehensive_security.analyze_threat(content, ip)

# New
result = await security_service.analyze_threat(content, ip)
```

#### Access Control (from EnhancedSecurityService)
```python
# Old
result = await enhanced_security.validate_login_attempt(user_id, ip)

# New
result = await security_service.validate_login_attempt(user_id, ip)
```

#### File Validation (from SecurityManager)
```python
# Old
result = security_manager.validate_audio_file(filename, content)

# New
result = security_service.validate_audio_file(filename, content)
```

## Benefits

1. **Reduced Complexity**: Single service instead of three
2. **Consistent Interface**: All security operations in one place
3. **Better Performance**: No duplicate tracking data structures
4. **Easier Testing**: One service to mock/test
5. **Clearer Dependencies**: Single import for all security needs

## Deprecation Timeline

- **Current**: All three old services are deprecated with warnings
- **Next Release**: Old services will be moved to legacy folder
- **Future Release**: Old services will be removed completely

## Configuration

The new `SecurityConfig` dataclass combines all configuration options:

```python
config = SecurityConfig(
    # Password policies
    password_min_length=12,
    max_login_attempts=5,
    
    # File security
    allowed_audio_types=["wav", "mp3"],
    max_file_size=10 * 1024 * 1024,
    
    # Threat detection
    dangerous_patterns=["script>", "drop table"]
)

security_service = UnifiedSecurityService(config)
```