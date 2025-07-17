"""from .standard_responses import (
    StandardAPIResponse,
    SuccessResponse,
    ErrorResponse,
    ChildSafetyResponse,
    AuthenticationResponse,
    PaginatedResponse,
    HealthCheckResponse,
    ValidationErrorResponse,
    ValidationErrorDetail,
    ResponseStatus,
    ResponseCode,
    create_success_response,
    create_error_response,
    create_child_safety_response,
    create_paginated_response,
    NAMING_CONVENTIONS
).
"""

"""🔄 API Models Package
Standardized API response models and naming conventions
"""

"""API Response Naming Convention Guidelines
===========================================
1. Field Names:
   - Use snake_case: user_id, created_at, is_active
   - Be descriptive: email_address not email, total_count not total
   - Avoid abbreviations: response_time_ms not resp_time

2. Boolean Fields:
   - Use positive names: is_active not is_inactive
   - Prefix appropriately: is_valid, has_permission, can_access

3. Standard Response Keys:
   - status: "success" | "error" | "warning" | "partial"
   - message: Human - readable description
   - data: Response payload
   - errors: Array of error objects
   - metadata: Additional context information
   - timestamp: ISO 8601 formatted datetime

4. ID Fields:
   - Suffix with _id: user_id, child_id, session_id
   - Use consistent format: UUID strings preferred

5. Time Fields:
   - Use ISO 8601 format: 2025 - 07 - 11T10: 30: 00Z
   - Suffix appropriately: created_at, updated_at, expires_at

6. Arrays vs Objects:
   - Use plural for arrays: children, devices, permissions
   - Use singular for objects: child, device, permission

Example Usage:
--------------
```python
from src.presentation.api.models import create_success_response
return create_success_response(data={"user_id": "123", "is_active": True}, message="User retrieved successfully")
```

Child Safety Specific:
---------------------
Always include safety metadata for child - related responses:
 - safety_validated: bool
 - coppa_compliant: bool
 - age_appropriate: bool
 - content_rating: str
"""

__all__ = [
    "NAMING_CONVENTIONS",
    "AuthenticationResponse",
    "ChildSafetyResponse",
    "ErrorResponse",
    "HealthCheckResponse",
    "PaginatedResponse",
    "ResponseCode",
    "ResponseStatus",
    "StandardAPIResponse",
    "SuccessResponse",
    "ValidationErrorDetail",
    "ValidationErrorResponse",
    "create_child_safety_response",
    "create_error_response",
    "create_paginated_response",
    "create_success_response",
]
