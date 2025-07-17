"""from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import logging
from fastapi import Request, Response, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware
from .core import SecurityThreat, InputValidationResult
from .validator import get_input_validator
from src.infrastructure.security.comprehensive_audit_integration import get_audit_integration.
"""

"""FastAPI middleware for automatic input validation on all requests."""

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Middleware that automatically validates all incoming requests for security threats."""

    def __init__(
        self,
        app,
        enable_child_safety: bool = True,
        strict_mode: bool = False,
    ):
        super().__init__(app)
        self.validator = get_input_validator()
        self.enable_child_safety = enable_child_safety
        self.strict_mode = strict_mode
        self.audit_integration = get_audit_integration()

        # Endpoints that require special handling
        self.child_endpoints = [
            "/api/children",
            "/api/conversations",
            "/api/interact",
        ]
        self.auth_endpoints = ["/api/auth", "/api/login", "/api/register"]
        self.skip_validation = ["/health", "/docs", "/openapi.json", "/static"]

    async def dispatch(self, request: Request, call_next) -> Response:
        """Validate incoming request data."""
        # Skip validation for certain endpoints
        if any(skip in str(request.url.path) for skip in self.skip_validation):
            return await call_next(request)

        try:
            # Get request context
            context = await self._extract_request_context(request)

            # Validate different parts of the request
            validation_results = []

            # Validate query parameters
            if request.query_params:
                for key, value in request.query_params.items():
                    result = await self.validator.validate_input(
                        value,
                        f"query.{key}",
                        context,
                    )
                    validation_results.append((f"query.{key}", result))

            # Validate path parameters
            if hasattr(request, "path_params") and request.path_params:
                for key, value in request.path_params.items():
                    result = await self.validator.validate_input(
                        value,
                        f"path.{key}",
                        context,
                    )
                    validation_results.append((f"path.{key}", result))

            # Validate headers (selective)
            suspicious_headers = [
                "x-forwarded-for",
                "user-agent",
                "referer",
                "authorization",
            ]
            for header in suspicious_headers:
                value = request.headers.get(header)
                if value:
                    result = await self.validator.validate_input(
                        value,
                        f"header.{header}",
                        context,
                    )
                    validation_results.append((f"header.{header}", result))

            # Validate request body (if present)
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    body = await self._get_request_body(request)
                    if body:
                        result = await self.validator.validate_input(
                            body,
                            "body",
                            context,
                        )
                        validation_results.append(("body", result))
                except Exception as e:
                    logger.warning(f"Could not validate request body: {e}")

            # Process validation results
            all_threats = []
            all_child_safety_violations = []
            for _field_name, result in validation_results:
                all_threats.extend(result.threats)
                all_child_safety_violations.extend(
                    result.child_safety_violations
                )

            # Check if request should be blocked
            should_block = await self._should_block_request(
                all_threats,
                all_child_safety_violations,
                context,
            )

            if should_block:
                # Log security incident
                await self._log_security_incident(
                    request,
                    all_threats,
                    all_child_safety_violations,
                )

                # Return appropriate error response
                return await self._create_security_error_response(
                    all_threats,
                    all_child_safety_violations,
                    context,
                )

            # Log non-blocking threats for monitoring
            if all_threats or all_child_safety_violations:
                await self._log_security_warning(
                    request,
                    all_threats,
                    all_child_safety_violations,
                )

            # Process the request
            response = await call_next(request)

            # Add security headers
            response.headers["X-Input-Validation"] = "passed"
            if all_threats:
                response.headers["X-Security-Warnings"] = str(len(all_threats))

            return response

        except Exception as e:
            logger.error(f"Input validation middleware error: {e}")
            # On error, allow request but log the issue
            response = await call_next(request)
            response.headers["X-Input-Validation"] = "error"
            return response

    async def _extract_request_context(
        self, request: Request
    ) -> Dict[str, Any]:
        """Extract context information from request."""
        return {
            "method": request.method,
            "path": str(request.url.path),
            "ip_address": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
            "is_child_endpoint": any(
                child_ep in str(request.url.path)
                for child_ep in self.child_endpoints
            ),
            "is_auth_endpoint": any(
                auth_ep in str(request.url.path)
                for auth_ep in self.auth_endpoints
            ),
        }

    async def _get_request_body(self, request: Request) -> Optional[Any]:
        """Safely extract request body."""
        try:
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                body_bytes = await request.body()
                if body_bytes:
                    return json.loads(body_bytes)
            elif "application/x-www-form-urlencoded" in content_type:
                form_data = await request.form()
                return dict(form_data)
            elif "multipart/form-data" in content_type:
                form_data = await request.form()
                return {
                    key: value
                    for key, value in form_data.items()
                    if not hasattr(value, "read")
                }
            return None
        except Exception as e:
            logger.warning(f"Could not parse request body: {e}")
            return None

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        if hasattr(request, "client") and request.client:
            return request.client.host
        return "unknown"

    async def _should_block_request(
        self,
        threats: List[SecurityThreat],
        child_safety_violations: List[str],
        context: Dict[str, Any],
    ) -> bool:
        """Determine if request should be blocked."""
        # Always block critical threats
        critical_threats = [t for t in threats if t.severity == "critical"]
        if critical_threats:
            return True

        # Block child safety violations on child endpoints
        if context.get("is_child_endpoint") and child_safety_violations:
            return True

        # In strict mode, block high severity threats
        if self.strict_mode:
            high_threats = [t for t in threats if t.severity == "high"]
            if high_threats:
                return True

        # Block multiple medium threats (possible coordinated attack)
        medium_threats = [t for t in threats if t.severity == "medium"]
        return len(medium_threats) >= 3

    async def _log_security_incident(
        self,
        request: Request,
        threats: List[SecurityThreat],
        child_safety_violations: List[str],
    ) -> None:
        """Log security incident for blocked request."""
        threat_summary = {
            "total_threats": len(threats),
            "critical_threats": len(
                [t for t in threats if t.severity == "critical"]
            ),
            "high_threats": len([t for t in threats if t.severity == "high"]),
            "child_safety_violations": len(child_safety_violations),
            "threat_types": list({t.threat_type for t in threats}),
        }

        await self.audit_integration.log_security_event(
            event_type="input_validation_blocked",
            severity="critical",
            description=f"Request blocked due to input validation failures: {threat_summary}",
            ip_address=self._get_client_ip(request),
            details={
                "path": str(request.url.path),
                "method": request.method,
                "threat_summary": threat_summary,
                "user_agent": request.headers.get("user-agent", ""),
            },
        )

    async def _log_security_warning(
        self,
        request: Request,
        threats: List[SecurityThreat],
        child_safety_violations: List[str],
    ) -> None:
        """Log security warning for non - blocking threats."""
        threat_summary = {
            "total_threats": len(threats),
            "medium_threats": len(
                [t for t in threats if t.severity == "medium"]
            ),
            "low_threats": len([t for t in threats if t.severity == "low"]),
            "child_safety_violations": len(child_safety_violations),
            "threat_types": list({t.threat_type for t in threats}),
        }

        await self.audit_integration.log_security_event(
            event_type="input_validation_warning",
            severity="warning",
            description=f"Request processed with security warnings: {threat_summary}",
            ip_address=self._get_client_ip(request),
            details={
                "path": str(request.url.path),
                "method": request.method,
                "threat_summary": threat_summary,
            },
        )

    async def _create_security_error_response(
        self,
        threats: List[SecurityThreat],
        child_safety_violations: List[str],
        context: Dict[str, Any],
    ) -> Response:
        """Create appropriate error response for security violations."""
        # Determine response based on violation type
        if child_safety_violations:
            status_code = status.HTTP_400_BAD_REQUEST
            error_message = "Request contains content that is not appropriate for children."
            error_type = "child_safety_violation"
        elif any(t.severity == "critical" for t in threats):
            status_code = status.HTTP_400_BAD_REQUEST
            error_message = "Request contains potentially malicious content."
            error_type = "security_threat_detected"
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            error_message = "Request validation failed."
            error_type = "validation_error"

        # Create sanitized error response (no specific threat details)
        error_response = {
            "error": error_type,
            "message": error_message,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # For child endpoints, use more generic messaging
        if context.get("is_child_endpoint"):
            error_response = {
                "error": "request_not_allowed",
                "message": "This request cannot be processed at this time.",
            }

        return Response(
            content=json.dumps(error_response),
            status_code=status_code,
            media_type="application/json",
            headers={
                "X-Security-Block": "input-validation",
                "X-Content-Type-Options": "nosniff",
            },
        )


# Factory function to create middleware
def create_input_validation_middleware(
    app,
    enable_child_safety: bool = True,
    strict_mode: bool = False,
) -> InputValidationMiddleware:
    """Create input validation middleware with specified configuration."""
    return InputValidationMiddleware(app, enable_child_safety, strict_mode)
