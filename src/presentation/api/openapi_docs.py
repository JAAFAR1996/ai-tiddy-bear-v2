"""from typing import Dict, Any."""

"""OpenAPI Documentation Configuration"""

API_TITLE = "AI Teddy Bear API"
API_VERSION = "1.0.0"
API_DESCRIPTION = """
# 🧸 AI Teddy Bear - Child-Safe AI Interaction Platform

### Overview
The AI Teddy Bear API provides secure, COPPA-compliant endpoints for:
- Child-AI interactions with content moderation
- Parental controls and monitoring
- Voice and text communication
- Educational content generation

### Security
- 🔐 JWT-based authentication required for all endpoints
- 🛡️ Rate limiting enforced (see individual endpoints)
- 👶 Child safety filters on all content
- 📊 Full audit logging

### Base URL
- Production: `https://api.aiteddybear.com/v1`
- Development: `http://localhost:8000/api/v1`
"""

# Tags for endpoint grouping
TAGS_METADATA = [
    {
        "name": "auth",
        "description": "Authentication and authorization endpoints",
    },
    {
        "name": "children",
        "description": "Child profile management (parental access only)",
    },
    {
        "name": "interactions",
        "description": "AI interactions and conversations",
    },
    {
        "name": "voice",
        "description": "Voice processing and text-to-speech",
    },
    {
        "name": "parental",
        "description": "Parental dashboard and controls",
    },
    {
        "name": "health",
        "description": "System health and monitoring",
    },
]

# Security schemes
SECURITY_SCHEMES = {
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "JWT token obtained from /auth/login endpoint",
    },
}

# Common response schemas
COMMON_RESPONSES = {
    "400": {
        "description": "Bad Request",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string"},
                        "message": {"type": "string"},
                        "details": {"type": "object"},
                    },
                },
            },
        },
    },
    "401": {
        "description": "Unauthorized - Invalid or missing authentication",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "example": "Unauthorized"},
                        "message": {
                            "type": "string",
                            "example": "Invalid authentication credentials",
                        },
                    },
                },
            },
        },
    },
    "403": {
        "description": "Forbidden - Insufficient permissions",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "example": "Forbidden"},
                        "message": {
                            "type": "string",
                            "example": "You don't have permission to access this resource",
                        },
                    },
                },
            },
        },
    },
    "429": {
        "description": "Too Many Requests - Rate limit exceeded",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "RateLimitExceeded",
                        },
                        "message": {
                            "type": "string",
                            "example": "Too many requests. Please try again later.",
                        },
                        "retry_after": {"type": "integer", "example": 60},
                    },
                },
            },
        },
    },
    "500": {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "InternalServerError",
                        },
                        "message": {
                            "type": "string",
                            "example": "An unexpected error occurred",
                        },
                        "request_id": {
                            "type": "string",
                            "example": "550e8400-e29b-41d4-a716-446655440000",
                        },
                    },
                },
            },
        },
    },
}


# Example endpoint documentation
def document_auth_endpoints():
    """Documentation for authentication endpoints."""
    return {
        "/auth/login": {
            "post": {
                "tags": ["auth"],
                "summary": "User login",
                "description": """
                Authenticate user and receive JWT tokens.
                **Rate Limit:** 5 requests per minute per IP
                """,
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["email", "password"],
                                "properties": {
                                    "email": {
                                        "type": "string",
                                        "format": "email",
                                        "example": "parent@example.com",
                                    },
                                    "password": {
                                        "type": "string",
                                        "format": "password",
                                        "minLength": 8,
                                        "example": "SecurePass123!",
                                    },
                                },
                            },
                        },
                    },
                },
                "responses": {
                    "200": {
                        "description": "Successful authentication",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "access_token": {
                                            "type": "string",
                                            "description": "JWT access token (expires in 15 minutes)",
                                        },
                                        "refresh_token": {
                                            "type": "string",
                                            "description": "JWT refresh token (expires in 7 days)",
                                        },
                                        "token_type": {
                                            "type": "string",
                                            "example": "bearer",
                                        },
                                        "user": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "string"},
                                                "email": {"type": "string"},
                                                "role": {
                                                    "type": "string",
                                                    "enum": [
                                                        "parent",
                                                        "admin",
                                                    ],
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                    **COMMON_RESPONSES,
                },
            },
        },
        "/auth/register": {
            "post": {
                "tags": ["auth"],
                "summary": "Register new parent account",
                "description": """
                Create a new parent account with COPPA compliance.
                **Rate Limit:** 3 requests per minute per IP
                **Requirements:**
                - Must be 18+ years old
                - Valid email required for verification
                - Strong password policy enforced
                """,
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": [
                                    "email",
                                    "password",
                                    "confirm_password",
                                    "parental_consent",
                                ],
                                "properties": {
                                    "email": {
                                        "type": "string",
                                        "format": "email",
                                    },
                                    "password": {
                                        "type": "string",
                                        "format": "password",
                                        "minLength": 8,
                                        "pattern": "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$",
                                    },
                                    "confirm_password": {
                                        "type": "string",
                                        "format": "password",
                                    },
                                    "parental_consent": {
                                        "type": "boolean",
                                        "description": "Must be true to proceed",
                                    },
                                },
                            },
                        },
                    },
                },
                "responses": {
                    "201": {
                        "description": "Account created successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "message": {
                                            "type": "string",
                                            "example": "Account created. Please check your email for verification.",
                                        },
                                        "user_id": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                    **COMMON_RESPONSES,
                },
            },
        },
    }


def document_child_endpoints():
    """Documentation for child management endpoints."""
    return {
        "/children": {
            "get": {
                "tags": ["children"],
                "summary": "List parent's children",
                "description": "Get all children associated with the authenticated parent",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "List of children",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "string"},
                                            "name": {"type": "string"},
                                            "age": {
                                                "type": "integer",
                                                "minimum": 3,
                                                "maximum": 13,
                                            },
                                            "avatar_url": {"type": "string"},
                                            "interaction_limits": {
                                                "type": "object",
                                                "properties": {
                                                    "daily_minutes": {
                                                        "type": "integer",
                                                    },
                                                    "session_minutes": {
                                                        "type": "integer",
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                    **COMMON_RESPONSES,
                },
            },
            "post": {
                "tags": ["children"],
                "summary": "Add a new child",
                "description": """
                Register a new child under parental supervision.
                **COPPA Requirements:**
                - Parental consent required
                - Minimal data collection
                - Age verification (3-13 years)
                """,
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": [
                                    "name",
                                    "birth_date",
                                    "parental_consent",
                                ],
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "maxLength": 50,
                                        "example": "Emma",
                                    },
                                    "birth_date": {
                                        "type": "string",
                                        "format": "date",
                                        "example": "2018-05-15",
                                    },
                                    "parental_consent": {
                                        "type": "boolean",
                                        "description": "Must be true",
                                    },
                                },
                            },
                        },
                    },
                },
                "responses": {
                    "201": {"description": "Child created successfully"},
                    **COMMON_RESPONSES,
                },
            },
        },
    }


def configure_openapi(app) -> None:
    """Configure OpenAPI documentation for the FastAPI app."""
    app.title = API_TITLE
    app.version = API_VERSION
    app.description = API_DESCRIPTION

    # Add tags
    if not hasattr(app, "openapi_tags"):
        app.openapi_tags = []
    app.openapi_tags.extend(TAGS_METADATA)

    # Update OpenAPI schema
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        from fastapi.openapi.utils import get_openapi

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            tags=TAGS_METADATA,
        )

        # Add security schemes
        openapi_schema["components"]["securitySchemes"] = SECURITY_SCHEMES

        # Add common responses
        if "components" not in openapi_schema:
            openapi_schema["components"] = {}
        openapi_schema["components"]["responses"] = COMMON_RESPONSES

        # Add custom endpoint documentation
        paths = openapi_schema.get("paths", {})
        paths.update(document_auth_endpoints())
        paths.update(document_child_endpoints())

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi


__all__ = [
    "API_DESCRIPTION",
    "API_TITLE",
    "API_VERSION",
    "COMMON_RESPONSES",
    "SECURITY_SCHEMES",
    "TAGS_METADATA",
    "configure_openapi",
]
