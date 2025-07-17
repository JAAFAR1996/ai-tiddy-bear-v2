"""Defines server-specific configuration settings for Uvicorn and FastAPI.

This module uses Pydantic to manage environment variables and provide
structured access to server parameters, including default ports, port ranges
for different environments, Uvicorn-specific settings (backlog, keep-alive
timeout, worker recycling), and worker counts. It ensures consistent and
optimized server configurations for both development and production.
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class ServerSettings(BaseSettings):
    """Server-specific settings for Uvicorn and FastAPI."""

    DEFAULT_PORT: int = Field(8000, description="Default application port.")
    DEV_PORT_MIN: int = Field(
        3000,
        description="Minimum port for development environment.",
    )
    DEV_PORT_MAX: int = Field(
        9999,
        description="Maximum port for development environment.",
    )
    PROD_PORT_MIN: int = Field(
        8000,
        description="Minimum port for production environment.",
    )
    PROD_PORT_MAX: int = Field(
        65535,
        description="Maximum port for production environment.",
    )
    UVICORN_BACKLOG: int = Field(
        2048, description="Uvicorn connection backlog."
    )
    UVICORN_KEEPALIVE_TIMEOUT: int = Field(
        60,
        description="Uvicorn keep-alive timeout in seconds.",
    )
    UVICORN_MAX_REQUESTS: int = Field(
        1000,
        description="Uvicorn worker recycling max requests.",
    )
    UVICORN_MAX_REQUESTS_JITTER: int = Field(
        50,
        description="Uvicorn worker recycling max requests jitter.",
    )
    UVICORN_DEV_WORKERS: int = Field(
        1,
        description="Number of Uvicorn workers in development mode.",
    )
    UVICORN_PROD_WORKERS_DEFAULT: int = Field(
        4,
        description="Default number of Uvicorn workers in production mode.",
    )

    class Config:
        env_prefix = "SERVER_"  # Optional: prefix for environment variables
        case_sensitive = True
