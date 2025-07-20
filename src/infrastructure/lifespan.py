"""Application lifespan manager for Hexagonal Architecture."""

import asyncio
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, suppress

import sentry_sdk
from fastapi import FastAPI
from prometheus_client import Gauge, start_http_server

from src.infrastructure.config.settings import get_settings
from src.infrastructure.di.container import container
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="infrastructure")

# Prometheus metrics
APP_UPTIME = Gauge("app_uptime_seconds", "Uptime of the application in seconds")
UPTIME_TASK_INTERVAL_SECONDS = 5


async def _update_app_uptime(start_time: float) -> None:
    """Periodically updates a Prometheus gauge with the application's uptime."""
    logger.info("Starting application uptime monitor.")
    while True:
        try:
            APP_UPTIME.set(time.time() - start_time)
            await asyncio.sleep(UPTIME_TASK_INTERVAL_SECONDS)
        except asyncio.CancelledError:
            logger.info("Application uptime monitor has been stopped.")
            break
        except Exception as e:
            logger.error(f"Error in uptime monitor task: {e}", exc_info=True)
            # Avoid fast-spinning loop on unexpected errors
            await asyncio.sleep(UPTIME_TASK_INTERVAL_SECONDS * 5)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager with Hexagonal Architecture and production configuration."""
    settings = get_settings()

    # Initialize Sentry
    if settings.sentry.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.sentry.SENTRY_DSN,
            traces_sample_rate=1.0,
            environment=settings.application.ENVIRONMENT,
        )
        logger.info("Sentry initialized successfully")

    # Initialize Prometheus
    if settings.prometheus.PROMETHEUS_ENABLED:
        # Prometheus metrics server runs on a separate port
        # This is typically handled by a sidecar or separate process in production
        # For demonstration, we start a simple server here.
        try:
            start_http_server(8001)  # Expose metrics on port 8001
            logger.info("Prometheus metrics server started on port 8001")
        except OSError as e:
            logger.warning(
                f"Could not start Prometheus metrics server: {e}. Port might be in use.",
            )

    # Initialize dependency injection container
    app.state.container = container
    container.init_resources()

    # Initialize event subscriptions
    container.init_event_subscriptions()
    logger.info("Event subscriptions initialized successfully")

    # Start Kafka consumer in a background task
    kafka_enabled = settings.kafka.KAFKA_ENABLED
    if kafka_enabled:
        event_bus = container.event_bus()
        kafka_connected = await event_bus.connect()
        if kafka_connected:
            app.state.kafka_consumer_task = asyncio.create_task(
                event_bus.start_consuming(),
            )
            logger.info("Kafka consumer started successfully")
        else:
            logger.error("Kafka connection failed")
            raise RuntimeError("Failed to connect to Kafka")
    else:
        logger.info("Kafka disabled in this environment")

    # Initialize database
    database_enabled = settings.database.DATABASE_ENABLED
    if database_enabled:
        db = container.database_manager()
        await db.init_db()
        logger.info("Database initialized successfully")
    else:
        logger.info("Database disabled in this environment")

    logger.info("🧸 AI Teddy Bear System initialized successfully")

    # Start uptime monitoring task
    app.state.uptime_task = asyncio.create_task(_update_app_uptime(time.time()))

    yield

    # Cleanup
    logger.info("Shutting down AI Teddy Bear System...")
    container.shutdown_resources()

    # Stop uptime monitoring task
    if hasattr(app.state, "uptime_task"):
        app.state.uptime_task.cancel()
        with suppress(asyncio.CancelledError):
            await app.state.uptime_task

    # Stop Kafka consumer
    if hasattr(app.state, "kafka_consumer_task"):
        app.state.kafka_consumer_task.cancel()
        with suppress(asyncio.CancelledError):
            await app.state.kafka_consumer_task

    logger.info("AI Teddy Bear System shutdown complete")
