"""OpenAPI Configuration for AI Teddy Bear API"

This module defines the custom OpenAPI schema generation for the FastAPI application,
including detailed descriptions, server URLs, security schemes, and common error responses.
"""

from typing import Any, Dict
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from src.common.constants import (
    OPENAPI_TITLE,
    OPENAPI_VERSION,
    OPENAPI_DESCRIPTION,
    OPENAPI_SERVERS,
    OPENAPI_TAGS,
    OPENAPI_EXTERNAL_DOCS,
    OPENAPI_LICENSE_INFO,
    OPENAPI_CONTACT_INFO,
    OPENAPI_COMMON_RESPONSES,
    OPENAPI_BEARER_DESCRIPTION # Import the new constant
) # Import OpenAPI constants

def custom_openapi(app: FastAPI) -> Dict[str, Any]:
    """Generate custom OpenAPI schema with comprehensive documentation."""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=OPENAPI_TITLE,
        version=OPENAPI_VERSION,
        description=OPENAPI_DESCRIPTION,
        routes=app.routes,
        servers=OPENAPI_SERVERS,
        tags=OPENAPI_TAGS,
    )
    # Add security scheme
    openapi_schema.setdefault("components", {})["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": OPENAPI_BEARER_DESCRIPTION,
        }
    }
    # Add global security requirement
    openapi_schema["security"] = [{"bearerAuth": []}]
    # Add external documentation
    openapi_schema["externalDocs"] = OPENAPI_EXTERNAL_DOCS
    # Add license info
    openapi_schema["info"]["license"] = OPENAPI_LICENSE_INFO
    # Add contact info
    openapi_schema["info"]["contact"] = OPENAPI_CONTACT_INFO
    # Ensure components and responses exist before updating
    openapi_schema.setdefault("components", {})
    openapi_schema["components"].setdefault("responses", {})
    # Add common error responses
    openapi_schema["components"]["responses"].update(OPENAPI_COMMON_RESPONSES)
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def configure_openapi(app: FastAPI) -> None:
    """Configure OpenAPI for the FastAPI application."""
    app.openapi = lambda: custom_openapi(app)