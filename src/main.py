"""AI Teddy Bear - Modern FastAPI Application (2025 Standards)
Enterprise-grade child-safe AI interaction system with Hexagonal Architecture.
"""

# Standard library imports
import os
from pathlib import Path

# Third-party imports
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Third-party imports for rate limiting
# from fastapi_limiter import FastAPILimiter  # Temporarily disabled for STEP 7
# from redis.asyncio import Redis  # Temporarily disabled for STEP 7

from src.common.exceptions import (  # Moved to central exceptions module
    StartupValidationException,
)

# Local imports
from src.infrastructure.config.core.production_check import (
    enforce_production_safety,
)
from src.infrastructure.di.container import container
from src.infrastructure.di.di_components.wiring_config import FullWiringConfig
from src.infrastructure.logging_config import configure_logging, get_logger
from src.infrastructure.middleware import setup_middleware
from src.infrastructure.persistence.database_manager import Database
from src.presentation.api.openapi_config import configure_openapi
from src.presentation.routing import setup_routing

# Load environment variables (only once at the top-level)
load_dotenv()

logger = get_logger(__name__, component="application")


async def lifespan(app: FastAPI):
    # Temporarily disable rate limiting for STEP 7 fixes
    logger.info("Rate limiting disabled for STEP 7 - focusing on DI fixes")

    # Initialize database with validation - re-enabled for Phase 1
    try:
        logger.info("Initializing database during application startup...")
        # Create database instance directly
        db = Database()
        await db.init_db()
        logger.info("✅ Database initialization completed successfully")
    except Exception as e:
        logger.critical(f"❌ Database initialization failed: {e}")
        # Don't crash the application, but log the error
        # In production, you might want to fail fast here

    # Yield control to the application startup
    yield

    # Perform cleanup actions on shutdown
    logger.info("Application shutdown event triggered.")


def _setup_app_configurations() -> None:
    """Helper function to set up core application configurations."""
    # Enforce production safety checks early
    enforce_production_safety()

    # Configure logging
    environment = container.settings().ENVIRONMENT
    configure_logging(environment=environment)


def _validate_system_startup() -> None:
    """Helper function to validate system configuration during startup."""
    try:
        container.wire(modules=FullWiringConfig.modules)
        # Startup validation temporarily disabled for STEP 7
    except RuntimeError as e:
        logger.critical(
            "System validation failed during app creation",
            exc_info=True,
        )
        raise StartupValidationException(
            "Application startup validation failed"
        ) from e


def _setup_app_middlewares_and_routes(fast_app: FastAPI) -> None:
    """Helper function to set up application middleware, routing, and OpenAPI."""
    setup_middleware(fast_app)
    setup_routing(fast_app)
    configure_openapi(fast_app)


def _mount_static_files(fast_app: FastAPI, project_root: Path) -> None:
    """Helper function to mount static files with security best practices."""
    environment = container.settings().ENVIRONMENT
    if environment == "production":
        logger.info(
            "Skipping static file serving in production environment. "
            "Use Nginx or a CDN.",
        )
        return

    static_files_path = container.settings().STATIC_FILES_DIR
    static_dir = (project_root / static_files_path).resolve()

    if not static_dir.is_dir():
        logger.warning(
            f"Static files directory not found at '{static_dir}'. "
            "Static file serving will be disabled.",
        )
    else:
        try:
            static_dir.relative_to(project_root)
        except ValueError:
            logger.critical(
                "SECURITY ALERT: Invalid STATIC_FILES_DIR. Path traversal "
                f"attempt detected. Directory '{static_dir}' is outside "
                f"of project root '{project_root}'.",
            )
            raise ValueError(
                "Invalid static files directory configuration: Path traversal "
                "detected.",
            )
        fast_app.mount(
            "/static", StaticFiles(directory=static_dir), name="static"
        )
        logger.info(f"Static files mounted from: {static_dir}")


def create_app() -> FastAPI:
    """Application factory function to create and configure the FastAPI app."""
    _setup_app_configurations()
    _validate_system_startup()

    fast_app = FastAPI(
        # Configured via settings for flexibility.
        title=container.settings().APP_NAME,
        # Configured via settings for flexibility.
        description=container.settings().APP_NAME,
        # Configured via settings for flexibility.
        version=container.settings().APP_VERSION,
        # Configured via settings for flexibility.
        docs_url="/docs",
        # Configured via settings for flexibility.
        redoc_url="/redoc",
        generate_unique_id_function=lambda route: (
            f"{route.tags[0]}_{route.name}" if route.tags else route.name
        ),
        lifespan=lifespan,  # Assign lifespan explicitly here in the factory.
    )

    _setup_app_middlewares_and_routes(fast_app)

    # Mount static files with security best practices
    project_root = (
        container.settings().PROJECT_ROOT
    )  # Now directly a Path object
    _mount_static_files(fast_app, project_root)

    return fast_app


# Create the app instance at module level for uvicorn
app = create_app()


if __name__ == "__main__":
    fast_app = app  # Use the already created app instance

    # Retrieve server settings for Uvicorn execution
    server_settings = container.settings()
    is_development = container.settings().ENVIRONMENT == "development"
    host = server_settings.HOST if not is_development else "127.0.0.1"
    port = (
        server_settings.PORT
        if not is_development
        else server_settings.DEFAULT_PORT
    )

    # Ensure SSL is configured for production or offloaded
    ssl_keyfile = os.getenv("SSL_KEYFILE")
    ssl_certfile = os.getenv("SSL_CERTFILE")
    ssl_offloaded = os.getenv("SSL_OFFLOADED", "false").lower() in (
        "true",
        "1",
        "yes",
    )

    uvicorn_ssl_args = {}
    if (
        not is_development
        and not (ssl_keyfile and ssl_certfile)
        and not ssl_offloaded
    ):
        logger.critical(
            "SECURITY ERROR: Production deployment requires SSL certificates "
            "or SSL offloading. Set SSL_KEYFILE and SSL_CERTFILE environment "
            "variables for Uvicorn SSL, or set SSL_OFFLOADED=true if an "
            "external proxy handles SSL.",
        )
        raise RuntimeError(
            "SSL configuration required for production deployment"
        )
    elif ssl_keyfile and ssl_certfile and not ssl_offloaded:
        uvicorn_ssl_args["ssl_keyfile"] = ssl_keyfile
        uvicorn_ssl_args["ssl_certfile"] = ssl_certfile
        logger.info("SSL configured for uvicorn.")
    elif ssl_offloaded:
        logger.info(
            "SSL is handled by an upstream proxy (SSL_OFFLOADED=true)."
        )
    else:
        logger.info("SSL not configured for uvicorn (development mode).")

    uvicorn.run(
        fast_app,
        host=host,
        port=port,
        log_level="info",
    )
