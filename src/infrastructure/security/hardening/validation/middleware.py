"""
Input Validation ASGI Middleware
Extracted from input_validation.py to reduce file size
"""

import json
from fastapi import HTTPException, Request
from .sanitizer import InputSanitizer
from .validation_config import InputValidationConfig
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


class InputValidationMiddleware:
    """
    ASGI middleware for input validation and sanitization
    """

    def __init__(self, app, config: InputValidationConfig = None) -> None:
        self.app = app
        self.config = config or InputValidationConfig()
        self.sanitizer = InputSanitizer(self.config)
        logger.info("Input validation middleware initialized")

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            # Skip validation for safe methods or specific paths
            if request.method in ["GET", "HEAD", "OPTIONS"]:
                await self.app(scope, receive, send)
                return
            # Validate request body
            try:
                body = await request.body()
                if body:
                    validated_body = await self._validate_request_body(
                        body, request
                    )
                    # Replace request body with validated version
                    scope["body"] = validated_body
            except HTTPException:
                # Forward validation errors
                raise
            except Exception as e:
                logger.error(f"Input validation error: {e}")
                raise HTTPException(
                    status_code=400, detail="Request validation failed"
                )
        await self.app(scope, receive, send)

    async def _validate_request_body(
        self, body: bytes, request: Request
    ) -> bytes:
        """Validate and sanitize request body"""
        try:
            # Determine if this is child input
            is_child_input = self._is_child_request(request)
            # Check body size
            max_size = self.config.max_json_size
            if len(body) > max_size:
                raise HTTPException(
                    status_code=413,
                    detail=f"Request body too large (max {max_size} bytes)",
                )
            # Try to parse as JSON
            try:
                data = json.loads(body.decode("utf-8"))
                # Sanitize JSON data
                result = self.sanitizer.sanitize_json(data, is_child_input)
                # Check if sanitization was successful
                if not result["is_safe"]:
                    critical_violations = [
                        v
                        for v in result["violations"]
                        if v["severity"] == "critical"
                    ]
                    if critical_violations:
                        logger.error(
                            f"Critical input validation violations: "
                            f"{[v['message'] for v in critical_violations]}"
                        )
                        raise HTTPException(
                            status_code=400,
                            detail="Input contains unsafe content",
                        )
                # Return sanitized data
                return json.dumps(result["sanitized"]).encode("utf-8")
            except json.JSONDecodeError:
                # Not JSON, treat as plain text
                text = body.decode("utf-8")
                result = self.sanitizer.sanitize_string(
                    text, is_child_input, "request_body"
                )
                if not result["is_safe"]:
                    critical_violations = [
                        v
                        for v in result["violations"]
                        if v["severity"] == "critical"
                    ]
                    if critical_violations:
                        raise HTTPException(
                            status_code=400,
                            detail="Input contains unsafe content",
                        )
                return result["sanitized"].encode("utf-8")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error validating request body: {e}")
            raise HTTPException(
                status_code=400, detail="Request validation failed"
            )

    def _is_child_request(self, request: Request) -> bool:
        """Determine if request comes from child user"""
        try:
            # Check user role from authentication
            user = getattr(request.state, "user", None)
            if user and isinstance(user, dict):
                return user.get("role") == "child"
            # Check for child-specific endpoints
            child_endpoints = ["/process-audio", "/children/", "/story/"]
            return any(
                endpoint in request.url.path for endpoint in child_endpoints
            )
        except (AttributeError, ValueError) as e:
            logger.warning(
                f"Error determining if request is child-related: {e}"
            )
            # Default to child input for safety
            return True
        except Exception as e:
            logger.error(f"Unexpected error in child endpoint detection: {e}")
            # Default to child input for safety
            return True


# Factory function
def create_input_validation_middleware(
    child_safety_mode: bool = True, **kwargs
) -> InputValidationMiddleware:
    """Create input validation middleware with custom configuration"""
    config = InputValidationConfig(**kwargs)
    if child_safety_mode:
        # More restrictive settings for child safety
        config.max_string_length = min(config.max_string_length, 5000)
        config.max_array_length = min(config.max_array_length, 500)
        config.enable_profanity_filter = True
        config.enable_personal_info_detection = True
    return InputValidationMiddleware(None, config)
