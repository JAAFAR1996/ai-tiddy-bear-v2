"""Provides a base class for all application services.

This module defines the `BaseService` abstract class, which provides a common
foundation for all application services. It includes functionalities for logging,
input validation, and lifecycle management (initialization and cleanup).
Services inheriting from `BaseService` are expected to implement the abstract
methods `initialize` and `cleanup` to manage their resources.
"""

from abc import ABC, abstractmethod
from typing import Any

from src.infrastructure.logging_config import get_logger


class BaseService(ABC):
    """Base class for application services."""

    def __init__(self) -> None:
        """Initializes the base service with a logger."""
        self.logger = get_logger(self.__class__.__name__, component="services")

    @abstractmethod
    async def initialize(self) -> None:
        """Initializes the service with required resources.

        This method should be implemented by each service to set up
        connections, load configurations, and prepare for operation.
        """

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleans up service resources and connections.

        This method should be implemented by each service to properly
        close connections, release resources, and clean up state.
        """

    def log_info(self, message: str, **kwargs: Any) -> None:
        """Logs an informational message with optional context.

        Args:
            message: The log message.
            **kwargs: Additional context data.

        """
        self.logger.info(message, extra=kwargs)

    def log_error(self, message: str, **kwargs: Any) -> None:
        """Logs an error message with optional context.

        Args:
            message: The error message.
            **kwargs: Additional context data.

        """
        self.logger.error(message, extra=kwargs)

    def validate_input(self, data: dict[str, Any], required_fields: list[str]) -> bool:
        """Validates that required fields are present in input data.

        Args:
            data: Input data to validate.
            required_fields: List of field names that must be present.

        Returns:
            True if all required fields are present and not None, False otherwise.

        Example:
            >>> service = BaseService()
            >>> service.validate_input({"name": "test", "age": 10}, ["name", "age"])
            True
            >>> service.validate_input({"name": "test"}, ["name", "age"])
            False

        """
        for field_name in required_fields:
            if field_name not in data or data[field_name] is None:
                self.log_error(f"Missing or null required field: {field_name}")
                return False
        return True
