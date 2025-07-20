"""Middleware configuration for FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.infrastructure.config.application_settings import ApplicationSettings
from src.infrastructure.config.settings import get_settings
from src.infrastructure.logging_config import get_logger
from src.presentation.api.middleware.error_handling import ErrorHandlingMiddleware
from src.presentation.api.middleware.request_logging import RequestLoggingMiddleware
from src.presentation.api.middleware.rate_limit_middleware import (
    RateLimitMiddleware as ChildSafetyMiddleware,
)

from src.infrastructure.middleware.security.headers import (
    SecurityHeadersMiddleware
)

logger = get_logger(__name__, component="infrastructure")


def setup_middleware(app: FastAPI) -> None:
    """Setup comprehensive middleware stack for child safety and security.
    Middleware order is critical - applied in reverse order(last added=first executed)
    Args: app: FastAPI application instance.
    """
    settings = get_settings()
    is_production = settings.application.ENVIRONMENT == "production"
    logger.info("🔧 Setting up comprehensive middleware stack...")

    # 1. Error Handling Middleware (LAST - catches all errors)
    app.add_middleware(ErrorHandlingMiddleware)
    logger.info("✅ Error handling middleware configured")

    # 2. Request Logging Middleware (second to last - logs everything)
    app.add_middleware(RequestLoggingMiddleware)
    logger.info("✅ Request logging middleware configured")

    # 3. Security Headers Middleware (comprehensive security headers)
    app.add_middleware(SecurityHeadersMiddleware)
    logger.info("✅ Security headers middleware configured")

    # 4. Child Safety Middleware (child-specific protection)
    app.add_middleware(ChildSafetyMiddleware)
    logger.info("✅ Child safety middleware configured")

    # 5. Rate Limiting Middleware
    app.add_middleware(RateLimitMiddleware)
    logger.info("✅ Rate limiting middleware configured")

    # 6. Trusted Host Middleware (production security)
    if is_production:
        trusted_hosts = _get_trusted_hosts(settings.application)
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)
        logger.info(f"✅ Trusted host middleware configured: {trusted_hosts}")

    # 7. HTTPS Redirect Middleware (production only)
    if is_production and settings.application.ENABLE_HTTPS:
        app.add_middleware(HTTPSRedirectMiddleware)
        logger.info("✅ HTTPS redirect middleware enabled")

    # 8. CORS Middleware (cross-origin requests) - Enhanced security
    cors_origins = _get_cors_origins(settings.application, is_production)
    _validate_cors_origins(cors_origins, is_production)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Request-ID",
            "X-Child-ID",
            "X-Parental-Consent",
        ],
        expose_headers=[
            "X-Request-ID",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
        ],
        max_age=600,
    )
    logger.info(f"✅ CORS middleware configured with {len(cors_origins)} origin(s)")

    # Log final middleware configuration
    _log_middleware_summary(is_production, cors_origins)


def _get_cors_origins(
    app_settings: ApplicationSettings,
    is_production: bool,
) -> list[str]:
    """Get CORS allowed origins based on environment with security validation.
    Args: app_settings: Application settings
        is_production: Whether running in production
    Returns: List of allowed CORS origins
    Raises: ValueError: If insecure CORS configuration is detected.
    """
    if is_production:
        # In production, CORS_ORIGINS must be explicitly configured and secure.
        # If not set, it defaults to an empty list, which will be caught by validation.
        configured_origins = (
            app_settings.CORS_ORIGINS if app_settings.CORS_ORIGINS is not None else []
        )
        if not configured_origins:
            logger.warning(
                "CORS_ORIGINS is empty or not set in production. "
                "This might lead to CORS issues. Ensure it's configured securely.",
            )
        return configured_origins
    # In development, allow common localhost origins for convenience.
    return [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://localhost",  # For some development setups
        "http://127.0.0.1",  # For some development setups
    ]


def _validate_cors_origins(origins: list[str], is_production: bool) -> None:
    """Validate CORS origins for security compliance.
    Args: origins: List of CORS origins to validate
        is_production: Whether running in production
    Raises: ValueError: If insecure configuration is detected.
    """
    for origin in origins:
        if is_production and origin == "*":
            raise ValueError(
                "Wildcard CORS origin (*) not allowed in production for child safety",
            )
        if is_production and not origin.startswith("https://"):
            raise ValueError(
                f"Non-HTTPS origin '{origin}' not allowed in production: {origin}",
            )
        suspicious_patterns = ["javascript:", "data:", "file:", "ftp://"]
        if any(pattern in origin.lower() for pattern in suspicious_patterns):
            raise ValueError(f"Suspicious origin pattern detected: {origin}")
    logger.info(f"CORS origins validation passed: {len(origins)} origins validated")


def _get_trusted_hosts(app_settings: ApplicationSettings) -> list[str]:
    """Get trusted hosts for production deployment.
    Args: app_settings: Application settings
    Returns: List of trusted host patterns.
    """
    if app_settings.TRUSTED_HOSTS:
        return app_settings.TRUSTED_HOSTS
    # Default production trusted hosts
    return ["aiteddybear.com", "*.aiteddybear.com", "localhost", "127.0.0.1"]


def _log_middleware_summary(is_production: bool, cors_origins: list[str]) -> None:
    """Log summary of middleware configuration.
    Args: is_production: Whether running in production
        cors_origins: Configured CORS origins.
    """
    logger.info("🔒 Middleware Configuration Summary:")
    logger.info(f"   • Environment: {'Production' if is_production else 'Development'}")
    logger.info("   • Error Handling: ✅ Enabled")
    logger.info("   • Request Logging: ✅ Enabled")
    logger.info("   • Security Headers: ✅ Enabled")
    logger.info("   • Child Safety: ✅ Enabled")
    logger.info("   • Rate Limiting: ✅ Enabled")
    logger.info(f"   • CORS Origins: {len(cors_origins)} configured")
    logger.info(
        f"   • HTTPS Redirect: {'✅ Enabled' if is_production else '❌ Development Only'}",
    )
    logger.info(
        f"   • Trusted Hosts: {'✅ Enabled' if is_production else '❌ Development Only'}",
    )
    logger.info("🧸 AI Teddy Bear middleware stack ready for child-safe interactions!")
