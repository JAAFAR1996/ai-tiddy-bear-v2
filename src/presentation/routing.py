"""Configures FastAPI routing for the AI Teddy Bear application.

This module sets up the main application routes, including API endpoints
for ESP32 devices, parental dashboard, health checks, ChatGPT interactions,
and authentication. It implements graceful degradation for missing router
modules, ensuring the application can still start even if some components
are unavailable.
"""

from fastapi import FastAPI

from src.common.constants import (  # Import new constants
    API_PREFIX_AUTH,
    API_PREFIX_CHATGPT,
    API_PREFIX_DASHBOARD,
    API_PREFIX_ESP32,
    API_PREFIX_HEALTH,
    API_TAG_AUTH,
    API_TAG_CHATGPT,
    API_TAG_DASHBOARD,
    API_TAG_ESP32,
    API_TAG_HEALTH,
)
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="presentation")

# Import routers with proper error handling
try:
    from src.presentation.api.endpoints.auth import router as auth_router
    from src.presentation.api.endpoints.chatgpt import router as chatgpt_router
    from src.presentation.api.esp32_endpoints import router as esp32_router
    from src.presentation.api.health_endpoints import router as health_router
    from src.presentation.api.parental_dashboard import router as parental_router
except ImportError as e:
    logger.error(f"Failed to import API routers: {e}")
    # Set routers to None for graceful degradation
    esp32_router = parental_router = health_router = chatgpt_router = auth_router = None


def setup_routing(app: FastAPI) -> None:
    """Set up application routing with graceful degradation for missing modules.

    Args:
        app: The FastAPI application instance.

    """
    router_configs = [
        (esp32_router, API_PREFIX_ESP32, API_TAG_ESP32, "ESP32"),
        (
            parental_router,
            API_PREFIX_DASHBOARD,
            API_TAG_DASHBOARD,
            "Dashboard",
        ),
        (health_router, API_PREFIX_HEALTH, API_TAG_HEALTH, "Health"),
        (chatgpt_router, API_PREFIX_CHATGPT, API_TAG_CHATGPT, "ChatGPT"),
        (auth_router, API_PREFIX_AUTH, API_TAG_AUTH, "Auth"),
    ]

    for router, prefix, tag, name in router_configs:
        if router:
            app.include_router(router, prefix=prefix, tags=[tag])
            logger.info(f"{name} endpoints included")
        else:
            logger.warning(f"{name} endpoints not available")
