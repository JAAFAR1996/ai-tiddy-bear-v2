"""from typing import List, Type, Optional
import logging
from sqlalchemy.orm import DeclarativeBase.
"""

"""Model Registry to avoid circular imports.
This module handles model registration and discovery to prevent circular dependencies
between database.py and model files.
"""

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="persistence")


class ModelRegistry:
    """Registry for SQLAlchemy models to prevent circular imports."""

    def __init__(self) -> None:
        self._models: List[Type[DeclarativeBase]] = []
        self._registered = False

    def register_model(self, model_class: Type[DeclarativeBase]) -> None:
        """Register a model class."""
        if model_class not in self._models:
            self._models.append(model_class)
            logger.debug(f"Registered model: {model_class.__name__}")

    def get_all_models(self) -> List[Type[DeclarativeBase]]:
        """Get all registered models."""
        if not self._registered:
            self._discover_models()
        return self._models.copy()

    def _discover_models(self) -> None:
        """Discover and register all models."""
        try:
            # Import models to trigger registration
            from src.infrastructure.persistence.models.child_model import ChildModel
            from src.infrastructure.persistence.models.conversation_model import (
                ConversationModel,
            )
            from src.infrastructure.persistence.models.user_model import UserModel

            # Models should auto-register themselves when imported
            self._registered = True
            logger.info(f"Discovered {len(self._models)} database models")
        except ImportError as e:
            logger.warning(f"Could not import some models: {e}")
            self._registered = True


# Global model registry instance
_model_registry: Optional[ModelRegistry] = None


def get_model_registry() -> ModelRegistry:
    """Get the global model registry instance."""
    global _model_registry
    if _model_registry is None:
        _model_registry = ModelRegistry()
    return _model_registry


def register_model(model_class: Type[DeclarativeBase]) -> Type[DeclarativeBase]:
    """Decorator to register a model class.
    Usage: @register_model class MyModel(Base): pass.
    """
    registry = get_model_registry()
    registry.register_model(model_class)
    return model_class
