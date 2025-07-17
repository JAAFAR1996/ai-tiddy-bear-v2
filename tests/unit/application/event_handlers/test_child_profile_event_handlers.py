"""
Comprehensive test suite for application/event_handlers/child_profile_event_handlers.py

This test file validates all aspects of the child profile event handlers
including event processing, async operations, error handling, and data consistency.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from src.application.event_handlers.child_profile_event_handlers import (
    ChildProfileEventHandlers,
)
from src.application.interfaces.read_model_interfaces import (
    IChildProfileReadModel,
    IChildProfileReadModelStore,
)
from src.domain.events.child_registered import ChildRegistered
from src.domain.events.child_profile_updated import ChildProfileUpdated


class MockChildProfileReadModel(IChildProfileReadModel):
    """Mock implementation of IChildProfileReadModel for testing."""

    def __init__(
        self, id: str, name: str, age: int, preferences: Dict[str, Any]
    ):
        self._id = id
        self._name = name
        self._age = age
        self._preferences = preferences or {}

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int):
        self._age = value

    @property
    def preferences(self) -> Dict[str, Any]:
        return self._preferences

    @preferences.setter
    def preferences(self, value: Dict[str, Any]):
        self._preferences = value


class MockReadModelStore(IChildProfileReadModelStore):
    """Mock implementation of IChildProfileReadModelStore for testing."""

    def __init__(self):
        self.models = {}
        self.save_called = False
        self.get_by_id_called = False
        self.delete_by_id_called = False
        self.update_called = False

    async def save(self, model: IChildProfileReadModel) -> None:
        self.save_called = True
        self.models[model.id] = model

    async def get_by_id(
        self, child_id: str
    ) -> Optional[IChildProfileReadModel]:
        self.get_by_id_called = True
        return self.models.get(child_id)

    async def delete_by_id(self, child_id: str) -> bool:
        self.delete_by_id_called = True
        return self.models.pop(child_id, None) is not None

    async def update(self, child_id: str, updates: Dict[str, Any]) -> bool:
        self.update_called = True
        model = self.models.get(child_id)
        if model:
            for key, value in updates.items():
                setattr(model, key, value)
            return True
        return False


@pytest.fixture
def mock_read_model_store():
    """Create a mock read model store for testing."""
    return MockReadModelStore()


@pytest.fixture
def child_profile_event_handlers(mock_read_model_store):
    """Create ChildProfileEventHandlers instance for testing."""
    return ChildProfileEventHandlers(mock_read_model_store)


@pytest.fixture
def sample_child_registered_event():
    """Create a sample ChildRegistered event."""
    return ChildRegistered(
        event_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        child_id=uuid4(),
        name="Test Child",
        age=8,
        preferences={"favorite_color": "blue", "favorite_animal": "dog"},
    )


@pytest.fixture
def sample_child_profile_updated_event():
    """Create a sample ChildProfileUpdated event."""
    return ChildProfileUpdated(
        child_id=uuid4(),
        name="Updated Child",
        age=9,
        preferences={"favorite_color": "red", "favorite_game": "puzzle"},
    )


class TestChildProfileEventHandlers:
    """Test suite for ChildProfileEventHandlers."""

    @pytest.mark.asyncio
    async def test_init_sets_read_model_store(self, mock_read_model_store):
        """Test that constructor properly sets the read model store."""
        handler = ChildProfileEventHandlers(mock_read_model_store)
        assert handler.read_model_store is mock_read_model_store

    @pytest.mark.asyncio
    @patch(
        "src.application.event_handlers.child_profile_event_handlers.create_child_profile_read_model"
    )
    async def test_handle_child_registered_success(
        self,
        mock_create_model,
        child_profile_event_handlers,
        sample_child_registered_event,
    ):
        """Test successful handling of child registered event."""
        # Arrange
        mock_model = MockChildProfileReadModel(
            id=str(sample_child_registered_event.child_id),
            name=sample_child_registered_event.name,
            age=sample_child_registered_event.age,
            preferences=sample_child_registered_event.preferences,
        )
        mock_create_model.return_value = mock_model

        # Act
        await child_profile_event_handlers.handle_child_registered(
            sample_child_registered_event
        )

        # Assert
        mock_create_model.assert_called_once_with(
            child_id=sample_child_registered_event.child_id,
            name=sample_child_registered_event.name,
            age=sample_child_registered_event.age,
            preferences=sample_child_registered_event.preferences,
        )
        assert child_profile_event_handlers.read_model_store.save_called

    @pytest.mark.asyncio
    @patch(
        "src.application.event_handlers.child_profile_event_handlers.create_child_profile_read_model"
    )
    @patch(
        "src.application.event_handlers.child_profile_event_handlers.logger"
    )
    async def test_handle_child_registered_logs_success(
        self,
        mock_logger,
        mock_create_model,
        child_profile_event_handlers,
        sample_child_registered_event,
    ):
        """Test that successful child registration is logged."""
        # Arrange
        mock_model = MockChildProfileReadModel(
            id=str(sample_child_registered_event.child_id),
            name=sample_child_registered_event.name,
            age=sample_child_registered_event.age,
            preferences=sample_child_registered_event.preferences,
        )
        mock_create_model.return_value = mock_model

        # Act
        await child_profile_event_handlers.handle_child_registered(
            sample_child_registered_event
        )

        # Assert
        mock_logger.debug.assert_called_once()
        debug_call_args = mock_logger.debug.call_args[0][0]
        assert "Child profile created" in debug_call_args
        assert str(sample_child_registered_event.age) in debug_call_args

    @pytest.mark.asyncio
    @patch(
        "src.application.event_handlers.child_profile_event_handlers.create_child_profile_read_model"
    )
    @patch(
        "src.application.event_handlers.child_profile_event_handlers.logger"
    )
    async def test_handle_child_registered_error_handling(
        self,
        mock_logger,
        mock_create_model,
        child_profile_event_handlers,
        sample_child_registered_event,
    ):
        """Test error handling in child registration."""
        # Arrange
        mock_create_model.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await child_profile_event_handlers.handle_child_registered(
                sample_child_registered_event
            )

        assert "Database error" in str(exc_info.value)
        mock_logger.error.assert_called_once()
        error_call_args = mock_logger.error.call_args[0][0]
        assert "Failed to handle child registration" in error_call_args

    @pytest.mark.asyncio
    async def test_handle_child_profile_updated_success(
        self, child_profile_event_handlers, sample_child_profile_updated_event
    ):
        """Test successful handling of child profile updated event."""
        # Arrange
        existing_model = MockChildProfileReadModel(
            id=str(sample_child_profile_updated_event.child_id),
            name="Original Name",
            age=7,
            preferences={"favorite_color": "green"},
        )
        child_profile_event_handlers.read_model_store.models[
            str(sample_child_profile_updated_event.child_id)
        ] = existing_model

        # Act
        await child_profile_event_handlers.handle_child_profile_updated(
            sample_child_profile_updated_event
        )

        # Assert
        assert existing_model.name == "Updated Child"
        assert existing_model.age == 9
        assert existing_model.preferences["favorite_color"] == "red"
        assert existing_model.preferences["favorite_game"] == "puzzle"
        assert child_profile_event_handlers.read_model_store.save_called

    @pytest.mark.asyncio
    @patch(
        "src.application.event_handlers.child_profile_event_handlers.logger"
    )
    async def test_handle_child_profile_updated_not_found(
        self,
        mock_logger,
        child_profile_event_handlers,
        sample_child_profile_updated_event,
    ):
        """Test handling of profile update when child not found."""
        # Act
        await child_profile_event_handlers.handle_child_profile_updated(
            sample_child_profile_updated_event
        )

        # Assert
        mock_logger.warning.assert_called_once_with(
            "Child profile not found for update"
        )
        assert not child_profile_event_handlers.read_model_store.save_called

    @pytest.mark.asyncio
    @patch(
        "src.application.event_handlers.child_profile_event_handlers.logger"
    )
    async def test_handle_child_profile_updated_no_changes(
        self, mock_logger, child_profile_event_handlers
    ):
        """Test handling of profile update when no changes are made."""
        # Arrange
        child_id = uuid4()
        existing_model = MockChildProfileReadModel(
            id=str(child_id),
            name="Same Name",
            age=8,
            preferences={"favorite_color": "blue"},
        )
        child_profile_event_handlers.read_model_store.models[str(child_id)] = (
            existing_model
        )

        # Create event with same values
        event = ChildProfileUpdated(
            child_id=child_id,
            name="Same Name",
            age=8,
            preferences={"favorite_color": "blue"},
        )

        # Act
        await child_profile_event_handlers.handle_child_profile_updated(event)

        # Assert
        mock_logger.debug.assert_called_with(
            "No changes detected, skipping database update"
        )
        assert not child_profile_event_handlers.read_model_store.save_called

    @pytest.mark.asyncio
    @patch(
        "src.application.event_handlers.child_profile_event_handlers.logger"
    )
    async def test_handle_child_profile_updated_partial_changes(
        self, mock_logger, child_profile_event_handlers
    ):
        """Test handling of profile update with partial changes."""
        # Arrange
        child_id = uuid4()
        existing_model = MockChildProfileReadModel(
            id=str(child_id),
            name="Original Name",
            age=7,
            preferences={"favorite_color": "green", "favorite_food": "pizza"},
        )
        child_profile_event_handlers.read_model_store.models[str(child_id)] = (
            existing_model
        )

        # Create event with only name change
        event = ChildProfileUpdated(
            child_id=child_id, name="New Name", age=None, preferences=None
        )

        # Act
        await child_profile_event_handlers.handle_child_profile_updated(event)

        # Assert
        assert existing_model.name == "New Name"
        assert existing_model.age == 7  # Unchanged
        # Unchanged
        assert existing_model.preferences["favorite_color"] == "green"
        assert child_profile_event_handlers.read_model_store.save_called

    @pytest.mark.asyncio
    @patch(
        "src.application.event_handlers.child_profile_event_handlers.logger"
    )
    async def test_handle_child_profile_updated_preference_changes(
        self, mock_logger, child_profile_event_handlers
    ):
        """Test handling of preference changes in profile update."""
        # Arrange
        child_id = uuid4()
        existing_model = MockChildProfileReadModel(
            id=str(child_id),
            name="Test Child",
            age=8,
            preferences={"favorite_color": "blue", "favorite_animal": "cat"},
        )
        child_profile_event_handlers.read_model_store.models[str(child_id)] = (
            existing_model
        )

        # Create event with preference changes
        event = ChildProfileUpdated(
            child_id=child_id,
            name=None,
            age=None,
            preferences={"favorite_color": "red", "favorite_game": "chess"},
        )

        # Act
        await child_profile_event_handlers.handle_child_profile_updated(event)

        # Assert
        assert existing_model.preferences["favorite_color"] == "red"
        assert existing_model.preferences["favorite_game"] == "chess"
        # Unchanged
        assert existing_model.preferences["favorite_animal"] == "cat"
        assert child_profile_event_handlers.read_model_store.save_called

    @pytest.mark.asyncio
    @patch(
        "src.application.event_handlers.child_profile_event_handlers.logger"
    )
    async def test_handle_child_profile_updated_logs_changes(
        self, mock_logger, child_profile_event_handlers
    ):
        """Test that profile updates are logged with change count."""
        # Arrange
        child_id = uuid4()
        existing_model = MockChildProfileReadModel(
            id=str(child_id),
            name="Test Child",
            age=8,
            preferences={"favorite_color": "blue"},
        )
        child_profile_event_handlers.read_model_store.models[str(child_id)] = (
            existing_model
        )

        # Create event with preference changes
        event = ChildProfileUpdated(
            child_id=child_id,
            name=None,
            age=None,
            preferences={"favorite_color": "red", "favorite_game": "chess"},
        )

        # Act
        await child_profile_event_handlers.handle_child_profile_updated(event)

        # Assert
        mock_logger.debug.assert_called()
        debug_call_args = mock_logger.debug.call_args[0][0]
        assert "Child profile updated" in debug_call_args
        assert "2 preference changes" in debug_call_args

    @pytest.mark.asyncio
    @patch(
        "src.application.event_handlers.child_profile_event_handlers.logger"
    )
    async def test_handle_child_profile_updated_error_handling(
        self,
        mock_logger,
        child_profile_event_handlers,
        sample_child_profile_updated_event,
    ):
        """Test error handling in child profile update."""
        # Arrange
        child_profile_event_handlers.read_model_store.get_by_id = AsyncMock(
            side_effect=Exception("Database error")
        )

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await child_profile_event_handlers.handle_child_profile_updated(
                sample_child_profile_updated_event
            )

        assert "Database error" in str(exc_info.value)
        mock_logger.error.assert_called_once()
        error_call_args = mock_logger.error.call_args[0][0]
        assert "Failed to handle child profile update" in error_call_args

    @pytest.mark.asyncio
    async def test_async_save_with_async_store(
        self, child_profile_event_handlers
    ):
        """Test _async_save method with async-capable store."""
        # Arrange
        mock_model = MockChildProfileReadModel("test_id", "Test", 8, {})
        child_profile_event_handlers.read_model_store.async_save = AsyncMock()

        # Act
        await child_profile_event_handlers._async_save(mock_model)

        # Assert
        child_profile_event_handlers.read_model_store.async_save.assert_called_once_with(
            mock_model
        )

    @pytest.mark.asyncio
    @patch("asyncio.get_event_loop")
    async def test_async_save_fallback_to_sync(
        self, mock_get_loop, child_profile_event_handlers
    ):
        """Test _async_save method fallback to sync operation."""
        # Arrange
        mock_model = MockChildProfileReadModel("test_id", "Test", 8, {})
        mock_loop = Mock()
        mock_get_loop.return_value = mock_loop
        mock_loop.run_in_executor = AsyncMock()

        # Remove async_save to test fallback
        if hasattr(
            child_profile_event_handlers.read_model_store, "async_save"
        ):
            delattr(
                child_profile_event_handlers.read_model_store, "async_save"
            )

        # Act
        await child_profile_event_handlers._async_save(mock_model)

        # Assert
        mock_loop.run_in_executor.assert_called_once_with(
            None,
            child_profile_event_handlers.read_model_store.save,
            mock_model,
        )

    @pytest.mark.asyncio
    async def test_async_get_by_id_with_async_store(
        self, child_profile_event_handlers
    ):
        """Test _async_get_by_id method with async-capable store."""
        # Arrange
        child_id = "test_id"
        mock_model = MockChildProfileReadModel(child_id, "Test", 8, {})
        child_profile_event_handlers.read_model_store.async_get_by_id = (
            AsyncMock(return_value=mock_model)
        )

        # Act
        result = await child_profile_event_handlers._async_get_by_id(child_id)

        # Assert
        child_profile_event_handlers.read_model_store.async_get_by_id.assert_called_once_with(
            child_id
        )
        assert result is mock_model

    @pytest.mark.asyncio
    @patch("asyncio.get_event_loop")
    async def test_async_get_by_id_fallback_to_sync(
        self, mock_get_loop, child_profile_event_handlers
    ):
        """Test _async_get_by_id method fallback to sync operation."""
        # Arrange
        child_id = "test_id"
        mock_model = MockChildProfileReadModel(child_id, "Test", 8, {})
        mock_loop = Mock()
        mock_get_loop.return_value = mock_loop
        mock_loop.run_in_executor = AsyncMock(return_value=mock_model)

        # Remove async_get_by_id to test fallback
        if hasattr(
            child_profile_event_handlers.read_model_store, "async_get_by_id"
        ):
            delattr(
                child_profile_event_handlers.read_model_store,
                "async_get_by_id",
            )

        # Act
        result = await child_profile_event_handlers._async_get_by_id(child_id)

        # Assert
        mock_loop.run_in_executor.assert_called_once_with(
            None,
            child_profile_event_handlers.read_model_store.get_by_id,
            child_id,
        )
        assert result is mock_model

    @pytest.mark.asyncio
    async def test_async_get_by_id_returns_none_when_not_found(
        self, child_profile_event_handlers
    ):
        """Test _async_get_by_id returns None when child not found."""
        # Arrange
        child_id = "nonexistent_id"
        child_profile_event_handlers.read_model_store.async_get_by_id = (
            AsyncMock(return_value=None)
        )

        # Act
        result = await child_profile_event_handlers._async_get_by_id(child_id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_concurrent_event_handling(
        self, child_profile_event_handlers
    ):
        """Test handling multiple events concurrently."""
        # Arrange
        events = []
        for i in range(5):
            event = ChildRegistered(
                event_id=uuid4(),
                timestamp=datetime.now(timezone.utc),
                child_id=uuid4(),
                name=f"Child {i}",
                age=5 + i,
                preferences={"favorite_number": i},
            )
            events.append(event)

        # Act
        with patch(
            "src.application.event_handlers.child_profile_event_handlers.create_child_profile_read_model"
        ) as mock_create:
            # Mock the create function to return different models
            mock_create.side_effect = [
                MockChildProfileReadModel(
                    str(event.child_id),
                    event.name,
                    event.age,
                    event.preferences,
                )
                for event in events
            ]

            tasks = [
                child_profile_event_handlers.handle_child_registered(event)
                for event in events
            ]

            await asyncio.gather(*tasks)

        # Assert
        assert len(child_profile_event_handlers.read_model_store.models) == 5
        assert mock_create.call_count == 5

    @pytest.mark.asyncio
    async def test_event_handling_with_empty_preferences(
        self, child_profile_event_handlers
    ):
        """Test handling events with empty preferences."""
        # Arrange
        event = ChildRegistered(
            event_id=uuid4(),
            timestamp=datetime.now(timezone.utc),
            child_id=uuid4(),
            name="Test Child",
            age=6,
            preferences={},
        )

        # Act
        with patch(
            "src.application.event_handlers.child_profile_event_handlers.create_child_profile_read_model"
        ) as mock_create:
            mock_create.return_value = MockChildProfileReadModel(
                str(event.child_id), event.name, event.age, event.preferences
            )

            await child_profile_event_handlers.handle_child_registered(event)

        # Assert
        mock_create.assert_called_once_with(
            child_id=event.child_id,
            name=event.name,
            age=event.age,
            preferences={},
        )

    @pytest.mark.asyncio
    async def test_event_handling_with_none_preferences(
        self, child_profile_event_handlers
    ):
        """Test handling profile update with None preferences."""
        # Arrange
        child_id = uuid4()
        existing_model = MockChildProfileReadModel(
            id=str(child_id),
            name="Test Child",
            age=8,
            preferences={"favorite_color": "blue"},
        )
        child_profile_event_handlers.read_model_store.models[str(child_id)] = (
            existing_model
        )

        event = ChildProfileUpdated(
            child_id=child_id, name="Updated Name", age=None, preferences=None
        )

        # Act
        await child_profile_event_handlers.handle_child_profile_updated(event)

        # Assert
        assert existing_model.name == "Updated Name"
        assert existing_model.age == 8  # Unchanged
        # Unchanged
        assert existing_model.preferences["favorite_color"] == "blue"

    @pytest.mark.asyncio
    async def test_event_handling_performance(
        self, child_profile_event_handlers
    ):
        """Test that event handling completes within reasonable time."""
        import time

        # Arrange
        event = ChildRegistered(
            event_id=uuid4(),
            timestamp=datetime.now(timezone.utc),
            child_id=uuid4(),
            name="Performance Test",
            age=7,
            preferences={"test": "value"},
        )

        # Act
        start_time = time.time()

        with patch(
            "src.application.event_handlers.child_profile_event_handlers.create_child_profile_read_model"
        ) as mock_create:
            mock_create.return_value = MockChildProfileReadModel(
                str(event.child_id), event.name, event.age, event.preferences
            )

            await child_profile_event_handlers.handle_child_registered(event)

        end_time = time.time()

        # Assert
        execution_time = end_time - start_time
        assert execution_time < 0.1  # Should complete within 100ms

    @pytest.mark.asyncio
    async def test_error_propagation(
        self, child_profile_event_handlers, sample_child_registered_event
    ):
        """Test that errors are properly propagated from async operations."""
        # Arrange
        child_profile_event_handlers.read_model_store.save = AsyncMock(
            side_effect=Exception("Save failed")
        )

        # Act & Assert
        with patch(
            "src.application.event_handlers.child_profile_event_handlers.create_child_profile_read_model"
        ) as mock_create:
            mock_create.return_value = MockChildProfileReadModel(
                str(sample_child_registered_event.child_id),
                sample_child_registered_event.name,
                sample_child_registered_event.age,
                sample_child_registered_event.preferences,
            )

            with pytest.raises(Exception) as exc_info:
                await child_profile_event_handlers.handle_child_registered(
                    sample_child_registered_event
                )

            assert "Save failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_logging_does_not_expose_pii(
        self, child_profile_event_handlers, sample_child_registered_event
    ):
        """Test that logging does not expose personally identifiable information."""
        # Act
        with patch(
            "src.application.event_handlers.child_profile_event_handlers.create_child_profile_read_model"
        ) as mock_create:
            with patch(
                "src.application.event_handlers.child_profile_event_handlers.logger"
            ) as mock_logger:
                mock_create.return_value = MockChildProfileReadModel(
                    str(sample_child_registered_event.child_id),
                    sample_child_registered_event.name,
                    sample_child_registered_event.age,
                    sample_child_registered_event.preferences,
                )

                await child_profile_event_handlers.handle_child_registered(
                    sample_child_registered_event
                )

        # Assert
        mock_logger.debug.assert_called_once()
        debug_call_args = mock_logger.debug.call_args[0][0]

        # Should not contain child's name or other PII
        assert sample_child_registered_event.name not in debug_call_args
        assert (
            str(sample_child_registered_event.child_id) not in debug_call_args
        )

        # Should contain age as it's not PII in context
        assert str(sample_child_registered_event.age) in debug_call_args
