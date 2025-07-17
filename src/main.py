"""AI Teddy Bear - Modern FastAPI Application (2025 Standards)
Enterprise-grade child-safe AI interaction system with Hexagonal Architecture"""

# Standard library imports
import logging
import os
from pathlib import Path
from typing import (
    Any,
)  # Consolidated imports; Any covers the flexibility of Optional and Dict if types are not strictly constrained elsewhere.

# Third-party imports
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

# Third-party imports for rate limiting
from fastapi_limiter import FastAPILimiter
from redis.asyncio import Redis

# Local imports
from src.infrastructure.config.production_check import enforce_production_safety
from src.infrastructure.config.startup_validator import validate_startup
from src.infrastructure.di.container import container
from src.infrastructure.di.di_components.wiring_config import FullWiringConfig
from src.infrastructure.logging_config import configure_logging, get_logger
from src.infrastructure.middleware import setup_middleware
from src.presentation.api.openapi_config import configure_openapi
from src.presentation.routing import setup_routing
from src.infrastructure.health.health_manager import (
    HealthCheckManager,
    get_health_manager,
    HealthStatus,
)  # HealthCheckManager defines detailed health checks within src/infrastructure/health, ensuring transparency of monitoring.
from src.domain.exceptions.base import (
    StartupValidationException,
)  # Moved to central exceptions module

# Load environment variables (only once at the top-level)
load_dotenv()

# Define project root and custom exceptions
# project_root is now managed via container.settings() to avoid global variable issues and ensure deterministic path resolution.
# class StartupValidationException(Exception):
#     """Custom exception for security-related issues.
#     This exception is raised when a security-sensitive configuration
#     or operation fails validation, indicating a potential vulnerability
#     or misconfiguration that could compromise the system.
#     """
#     pass

logger = get_logger(__name__, component="application")


async def lifespan(app: FastAPI):
    try:
        # Initialize FastAPILimiter with Redis connection
        redis_url = container.settings().redis.REDIS_URL
        redis_client = Redis.from_url(
            redis_url,
            max_connections=container.settings().redis.MAX_CONNECTIONS,
            timeout=container.settings().redis.TIMEOUT,
        )
        await FastAPILimiter.init(redis_client)
        logger.info("FastAPILimiter initialized with Redis.")
    except Exception as e:
        logger.critical(
            f"Failed to initialize FastAPILimiter or connect to Redis: {e}",
            exc_info=True,
        )
        raise RuntimeError(
            "Failed to initialize FastAPILimiter due to Redis connection issue"
        ) from e

    # Yield control to the application startup
    yield

    # Perform cleanup actions on shutdown
    logger.info(
        "Application shutdown event triggered. Closing Redis connection.")
    if redis_client:
        await redis_client.close()
        logger.info("Redis client closed.")


def _setup_app_configurations() -> None:
    """Helper function to set up core application configurations."""
    # Environment variables are loaded globally, no need to re-load
    # load_dotenv()

    # Enforce production safety checks early
    enforce_production_safety()

    # Configure logging
    environment = container.settings().app.ENVIRONMENT
    configure_logging(environment=environment)


def _validate_system_startup() -> None:
    """Helper function to validate system configuration during startup."""
    try:
        container.wire(modules=FullWiringConfig.modules)
        startup_validator_instance = container.startup_validator()
        validate_startup(startup_validator_instance)
    except RuntimeError as e:
        logger.critical(
            "System validation failed during app creation",
            exc_info=True)
        raise StartupValidationException(
            "Application startup validation failed") from e


def _setup_app_middlewares_and_routes(fast_app: FastAPI) -> None:
    """Helper function to set up application middleware, routing, and OpenAPI."""
    setup_middleware(fast_app)
    setup_routing(fast_app)
    configure_openapi(fast_app)


def _mount_static_files(fast_app: FastAPI, project_root: Path) -> None:
    """Helper function to mount static files with security best practices."""
    environment = container.settings().app.ENVIRONMENT
    if environment == "production":
        logger.info(
            "Skipping static file serving in production environment. Use Nginx or a CDN."
        )
        return

    static_files_path = container.settings().application.STATIC_FILES_DIR
    static_dir = (project_root / static_files_path).resolve()

    if not static_dir.is_dir():
        logger.warning(
            f"Static files directory not found at '{static_dir}'. Static file serving will be disabled."
        )
    else:
        try:
            static_dir.relative_to(project_root)
        except ValueError:
            logger.critical(
                f"SECURITY ALERT: Invalid STATIC_FILES_DIR. Path traversal attempt detected."
                f"Directory '{static_dir}' is outside of project root '{project_root}'."
            )
            raise ValueError(
                "Invalid static files directory configuration: Path traversal detected."
            )
        fast_app.mount(
            "/static",
            StaticFiles(
                directory=static_dir),
            name="static")
        logger.info(f"Static files mounted from: {static_dir}")


def create_app() -> FastAPI:
    """Application factory function to create and configure the FastAPI app."""
    _setup_app_configurations()
    _validate_system_startup()

    fast_app = FastAPI(
        # Configured via settings for flexibility.
        title=container.settings().application.APP_NAME,
        # Configured via settings for flexibility.
        description=container.settings().application.APP_NAME,
        # Configured via settings for flexibility.
        version=container.settings().application.APP_VERSION,
        # Configured via settings for flexibility.
        docs_url=container.settings().application.DOCS_URL,
        # Configured via settings for flexibility.
        redoc_url=container.settings().application.REDOC_URL,
        generate_unique_id_function=lambda route: (
            f"{route.tags[0]}_{route.name}" if route.tags else route.name
        ),
        lifespan=lifespan,  # Assign lifespan explicitly here in the factory.
    )

    _setup_app_middlewares_and_routes(fast_app)

    # Mount static files with security best practices
    project_root = (
        container.settings().application.PROJECT_ROOT
    )  # Now directly a Path object
    _mount_static_files(fast_app, project_root)

    return fast_app


if __name__ == "__main__":
    app = create_app()

    # Retrieve server settings for Uvicorn execution
    server_settings = container.settings().server
    is_development = container.settings().app.ENVIRONMENT == "development"
    host = server_settings.HOST if not is_development else "127.0.0.1"
    port = server_settings.PORT if not is_development else server_settings.DEFAULT_PORT

    # Ensure SSL is configured for production or offloaded
    ssl_keyfile = os.getenv("SSL_KEYFILE")
    ssl_certfile = os.getenv("SSL_CERTFILE")
    ssl_offloaded = os.getenv(
        "SSL_OFFLOADED",
        "false").lower() in (
        "true",
        "1",
        "yes")

    uvicorn_ssl_args = {}
    if not is_development and not (
            ssl_keyfile and ssl_certfile) and not ssl_offloaded:
        logger.critical(
            "SECURITY ERROR: Production deployment requires SSL certificates or SSL offloading. "
            "Set SSL_KEYFILE and SSL_CERTFILE environment variables for Uvicorn SSL, "
            "or set SSL_OFFLOADED=true if an external proxy handles SSL."
        )
        raise RuntimeError(
            "SSL configuration required for production deployment")
    elif ssl_keyfile and ssl_certfile and not ssl_offloaded:
        uvicorn_ssl_args["ssl_keyfile"] = ssl_keyfile
        uvicorn_ssl_args["ssl_certfile"] = ssl_certfile
        logger.info("SSL configured for uvicorn.")
    elif ssl_offloaded:
        logger.info("SSL is handled by an upstream proxy (SSL_OFFLOADED=true).")
    else:
        logger.info("SSL not configured for uvicorn (development mode).")

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=is_development,
        access_log=is_development,
        log_level="info" if is_development else "warning",
        server_header=False,
        date_header=False,
        **uvicorn_ssl_args,
        workers=(
            server_settings.UVICORN_DEV_WORKERS
            if is_development
            else int(
                os.getenv(
                    "WORKERS", str(
                        server_settings.UVICORN_PROD_WORKERS_DEFAULT))
            )
        ),
        backlog=server_settings.UVICORN_BACKLOG,
        keepalive_timeout=server_settings.UVICORN_KEEPALIVE_TIMEOUT,
        max_requests=(
            server_settings.UVICORN_MAX_REQUESTS if not is_development else None
        ),
        max_requests_jitter=(
            server_settings.UVICORN_MAX_REQUESTS_JITTER if not is_development else None
        ),
    )
