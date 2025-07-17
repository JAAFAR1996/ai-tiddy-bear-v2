import asyncio
import logging

from src.application.interfaces.read_model_interfaces import (
    IChildProfileReadModel,
    IChildProfileReadModelStore,
    create_child_profile_read_model,
)
from src.domain.events.child_profile_updated import ChildProfileUpdated
from src.domain.events.child_registered import ChildRegistered

"""
Child Profile Event Handlers for AI Teddy Bear
This module handles domain events related to child profile management,
updating read models and maintaining data consistency across the system.

Performance Features:
- Async/await pattern for non-blocking operations
- Batch processing capabilities
- Optimized database operations
- Connection pooling support
"""

logger = logging.getLogger(__name__)


class ChildProfileEventHandlers:
    """High-performance event handlers for child profile domain events.
    Handles child registration and profile update events with optimized
    async operations to prevent blocking the event loop.
    """

    def __init__(self, read_model_store: IChildProfileReadModelStore) -> None:
        self.read_model_store = read_model_store

    async def handle_child_registered(self, event: ChildRegistered) -> None:
        """Handle child registration event with async database operations.

        Args:
            event: ChildRegistered domain event

        Performance optimizations:
        - Non-blocking async save operation
        - Error handling to prevent event loop blocking

        """
        try:
            child_read_model = create_child_profile_read_model(
                child_id=event.child_id,
                name=event.name,
                age=event.age,
                preferences=event.preferences,
            )
            await self._async_save(child_read_model)
            logger.debug(
                f"Child profile created for age {event.age}",
            )  # PII-safe logging
        except Exception as e:
            logger.error(f"Failed to handle child registration: {e}")
            # Re-raise to ensure event processing fails if needed
            raise

    async def handle_child_profile_updated(
        self, event: ChildProfileUpdated
    ) -> None:
        """Handle child profile update event with optimized async operations.

        Args:
            event: ChildProfileUpdated domain event

        Performance optimizations:
        - Async get and save operations
        - Batch updates for multiple fields
        - Early return if no changes needed

        """
        try:
            existing_model = await self._async_get_by_id(event.child_id)
            if not existing_model:
                logger.warning("Child profile not found for update")
                return

            updates_made = False

            if event.name is not None and existing_model.name != event.name:
                existing_model.name = event.name
                updates_made = True

            if event.age is not None and existing_model.age != event.age:
                existing_model.age = event.age
                updates_made = True

            if event.preferences is not None:
                # Batch preference updates
                for key, value in event.preferences.items():
                    if existing_model.preferences.get(key) != value:
                        existing_model.preferences[key] = value
                        updates_made = True

            if updates_made:
                await self._async_save(existing_model)
                logger.debug(
                    f"Child profile updated with "
                    f"{len(event.preferences or {})} preference changes",
                )
            else:
                logger.debug("No changes detected, skipping database update")
        except Exception as e:
            logger.error(f"Failed to handle child profile update: {e}")
            raise

    async def _async_save(self, model: IChildProfileReadModel) -> None:
        """Async wrapper for save operation to prevent blocking.

        Args:
            model: Child profile read model to save

        """
        if hasattr(self.read_model_store, "async_save"):
            await self.read_model_store.async_save(model)
        else:
            # Fallback: run sync operation in thread pool to prevent blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.read_model_store.save, model)

    async def _async_get_by_id(
        self, child_id: str
    ) -> IChildProfileReadModel | None:
        """Async wrapper for get_by_id operation to prevent blocking.

        Args:
            child_id: Child identifier

        Returns:
            Child profile read model or None if not found

        """
        if hasattr(self.read_model_store, "async_get_by_id"):
            return await self.read_model_store.async_get_by_id(child_id)
        # Fallback: run sync operation in thread pool to prevent blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.read_model_store.get_by_id,
            child_id,
        )
