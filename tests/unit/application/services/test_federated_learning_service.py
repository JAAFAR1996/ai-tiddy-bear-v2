"""Tests for Federated Learning Service
Testing federated learning operations functionality.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.application.interfaces.read_model_interfaces import IEventBus
from src.application.services.federated_learning_service import FederatedLearningService


class TestFederatedLearningService:
    """Test the Federated Learning Service."""

    @pytest.fixture
    def mock_event_bus(self):
        """Create a mock event bus."""
        bus = Mock(spec=IEventBus)
        bus.publish = AsyncMock()
        return bus

    @pytest.fixture
    def service(self, mock_event_bus):
        """Create a federated learning service instance."""
        return FederatedLearningService(event_bus=mock_event_bus)

    @pytest.fixture
    def service_no_event_bus(self):
        """Create a federated learning service instance without event bus."""
        with patch(
            "src.application.services.federated_learning_service.get_event_bus"
        ) as mock_get_bus:
            mock_bus = Mock(spec=IEventBus)
            mock_bus.publish = AsyncMock()
            mock_get_bus.return_value = mock_bus
            return FederatedLearningService()

    def test_initialization_with_event_bus(self, mock_event_bus):
        """Test service initialization with provided event bus."""
        with patch.object(
            FederatedLearningService, "_initialize_global_model"
        ) as mock_init:
            mock_init.return_value = {"test": "model"}

            service = FederatedLearningService(event_bus=mock_event_bus)

            assert service.event_bus == mock_event_bus
            assert service.global_model == {"test": "model"}
            mock_init.assert_called_once()

    def test_initialization_without_event_bus(self):
        """Test service initialization without event bus."""
        with patch(
            "src.application.services.federated_learning_service.get_event_bus"
        ) as mock_get_bus:
            mock_bus = Mock()
            mock_get_bus.return_value = mock_bus

            service = FederatedLearningService()

            mock_get_bus.assert_called_once()
            assert service.event_bus == mock_bus

    def test_initialize_global_model(self, service):
        """Test global model initialization."""
        # Reset the model to test initialization
        with patch(
            "src.application.services.federated_learning_service.logger"
        ) as mock_logger:
            model = service._initialize_global_model()

            assert isinstance(model, dict)
            assert "weights" in model
            assert "bias" in model
            assert model["weights"] == [0.1, 0.2, 0.3]
            assert model["bias"] == 0.05

            mock_logger.info.assert_called_once_with("Initializing global model...")

    @pytest.mark.asyncio
    async def test_process_local_model_update_success(self, service):
        """Test successful processing of local model update."""
        # Arrange
        device_id = "device_123"
        local_update = {"weights": [0.15, 0.25, 0.35], "bias": 0.07}

        original_weights = service.global_model["weights"].copy()
        original_bias = service.global_model["bias"]

        with patch(
            "src.application.services.federated_learning_service.logger"
        ) as mock_logger:
            # Act
            await service.process_local_model_update(device_id, local_update)

            # Assert
            mock_logger.info.assert_called()
            log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            assert any("Received local model update" in log for log in log_calls)
            assert any("Aggregating model update" in log for log in log_calls)

            # Check that global model was updated
            for i, original_weight in enumerate(original_weights):
                expected_weight = (original_weight + local_update["weights"][i]) / 2
                assert service.global_model["weights"][i] == expected_weight

            expected_bias = (original_bias + local_update["bias"]) / 2
            assert service.global_model["bias"] == expected_bias

    @pytest.mark.asyncio
    async def test_process_multiple_local_updates(self, service):
        """Test processing multiple local model updates."""
        device_updates = [
            ("device_1", {"weights": [0.2, 0.3, 0.4], "bias": 0.1}),
            ("device_2", {"weights": [0.3, 0.4, 0.5], "bias": 0.2}),
            ("device_3", {"weights": [0.1, 0.1, 0.1], "bias": 0.0}),
        ]

        for device_id, update in device_updates:
            await service.process_local_model_update(device_id, update)

        # Verify model has been updated (exact values depend on aggregation
        # order)
        assert isinstance(service.global_model["weights"], list)
        assert len(service.global_model["weights"]) == 3
        assert isinstance(service.global_model["bias"], float)

    def test_aggregate_model_update_simple_averaging(self, service):
        """Test model aggregation with simple averaging."""
        # Setup initial state
        service.global_model = {"weights": [0.1, 0.2, 0.3], "bias": 0.05}

        local_update = {"weights": [0.3, 0.4, 0.5], "bias": 0.15}

        with patch("src.application.services.federated_learning_service.logger"):
            service._aggregate_model_update(local_update)

        # Check simple averaging: (global + local) / 2
        # [(0.1+0.3)/2, (0.2+0.4)/2, (0.3+0.5)/2]
        expected_weights = [0.2, 0.3, 0.4]
        expected_bias = 0.1  # (0.05 + 0.15) / 2

        assert service.global_model["weights"] == expected_weights
        assert service.global_model["bias"] == expected_bias

    def test_aggregate_model_update_edge_cases(self, service):
        """Test model aggregation with edge case values."""
        test_cases = [
            # Zero update
            {"weights": [0.0, 0.0, 0.0], "bias": 0.0},
            # Negative values
            {"weights": [-0.1, -0.2, -0.3], "bias": -0.05},
            # Large values
            {"weights": [1.0, 2.0, 3.0], "bias": 1.0},
            # Very small values
            {"weights": [0.001, 0.002, 0.003], "bias": 0.001},
        ]

        for update in test_cases:
            # Reset to known state
            service.global_model = {"weights": [0.1, 0.2, 0.3], "bias": 0.05}

            with patch("src.application.services.federated_learning_service.logger"):
                service._aggregate_model_update(update)

            # Verify aggregation completed without errors
            assert len(service.global_model["weights"]) == 3
            assert isinstance(service.global_model["bias"], (int, float))

    def test_get_global_model(self, service):
        """Test retrieving the global model."""
        model = service.get_global_model()

        assert isinstance(model, dict)
        assert "weights" in model
        assert "bias" in model
        assert model == service.global_model

        # Verify it returns the same reference (not a copy)
        assert model is service.global_model

    def test_get_global_model_after_updates(self, service):
        """Test getting global model after processing updates."""
        # Process some updates
        local_update = {"weights": [0.2, 0.3, 0.4], "bias": 0.1}

        with patch("src.application.services.federated_learning_service.logger"):
            service._aggregate_model_update(local_update)

        model = service.get_global_model()

        # Should reflect the updated state
        assert model["weights"] != [0.1, 0.2, 0.3]  # Original values
        assert model["bias"] != 0.05  # Original value

        # But should still be a valid model structure
        assert len(model["weights"]) == 3
        assert isinstance(model["bias"], (int, float))

    @pytest.mark.asyncio
    async def test_concurrent_model_updates(self, service):
        """Test concurrent processing of model updates."""
        import asyncio

        # Create multiple concurrent updates
        updates = [
            ("device_1", {"weights": [0.1, 0.2, 0.3], "bias": 0.05}),
            ("device_2", {"weights": [0.2, 0.3, 0.4], "bias": 0.10}),
            ("device_3", {"weights": [0.3, 0.4, 0.5], "bias": 0.15}),
            ("device_4", {"weights": [0.0, 0.1, 0.2], "bias": 0.02}),
        ]

        # Process all updates concurrently
        tasks = [
            service.process_local_model_update(device_id, update)
            for device_id, update in updates
        ]

        await asyncio.gather(*tasks)

        # Verify final model state is valid
        model = service.get_global_model()
        assert len(model["weights"]) == 3
        assert isinstance(model["bias"], (int, float))

    @pytest.mark.asyncio
    async def test_model_update_logging(self, service):
        """Test that model updates are properly logged."""
        device_id = "logging_test_device"
        local_update = {"weights": [0.5, 0.6, 0.7], "bias": 0.25}

        with patch(
            "src.application.services.federated_learning_service.logger"
        ) as mock_logger:
            await service.process_local_model_update(device_id, local_update)

            # Check logging calls
            assert mock_logger.info.call_count >= 2

            log_messages = [call[0][0] for call in mock_logger.info.call_args_list]

            # Should log receiving the update
            receive_log = next(
                (msg for msg in log_messages if "Received local model update" in msg),
                None,
            )
            assert receive_log is not None
            assert device_id in receive_log

            # Should log aggregating the update
            aggregate_log = next(
                (msg for msg in log_messages if "Aggregating model update" in msg),
                None,
            )
            assert aggregate_log is not None

    @pytest.mark.asyncio
    async def test_different_model_structures(self, service):
        """Test handling different model update structures."""
        # Test with different weight vector lengths
        updates_different_lengths = [
            {"weights": [0.1], "bias": 0.05},  # Too short
            {"weights": [0.1, 0.2], "bias": 0.05},  # Still too short
            {"weights": [0.1, 0.2, 0.3, 0.4], "bias": 0.05},  # Too long
        ]

        for update in updates_different_lengths:
            # Should handle gracefully (might raise IndexError or handle
            # differently)
            try:
                await service.process_local_model_update("test_device", update)
            except (IndexError, KeyError):
                # Expected for incompatible structures
                pass

    @pytest.mark.asyncio
    async def test_model_update_with_missing_fields(self, service):
        """Test handling model updates with missing fields."""
        incomplete_updates = [
            {"weights": [0.1, 0.2, 0.3]},  # Missing bias
            {"bias": 0.05},  # Missing weights
            {},  # Missing both
            {"extra_field": "value"},  # Different structure
        ]

        for update in incomplete_updates:
            try:
                await service.process_local_model_update("test_device", update)
            except (KeyError, TypeError):
                # Expected for incomplete updates
                pass

    def test_model_persistence_across_operations(self, service):
        """Test that model state persists across multiple operations."""
        # Record initial state
        initial_model = service.get_global_model().copy()

        # Perform multiple operations
        updates = [
            {"weights": [0.2, 0.3, 0.4], "bias": 0.1},
            {"weights": [0.3, 0.4, 0.5], "bias": 0.2},
        ]

        for update in updates:
            with patch("src.application.services.federated_learning_service.logger"):
                service._aggregate_model_update(update)

        # Model should have changed from initial state
        final_model = service.get_global_model()
        assert final_model != initial_model

        # But structure should be preserved
        assert len(final_model["weights"]) == len(initial_model["weights"])
        assert "bias" in final_model

    @pytest.mark.asyncio
    async def test_device_id_variations(self, service):
        """Test processing updates from various device ID formats."""
        device_ids = [
            "device_001",
            "DEVICE_ABC",
            "device-with-dashes",
            "device_with_underscores",
            "device.with.dots",
            "123_numeric_device",
            "very_long_device_identifier_with_many_characters",
        ]

        update = {"weights": [0.2, 0.3, 0.4], "bias": 0.1}

        for device_id in device_ids:
            with patch("src.application.services.federated_learning_service.logger"):
                await service.process_local_model_update(device_id, update)

            # Should process without errors regardless of device ID format

    def test_model_aggregation_mathematical_correctness(self, service):
        """Test that model aggregation produces mathematically correct results."""
        # Set known initial state
        service.global_model = {"weights": [1.0, 2.0, 3.0], "bias": 0.5}

        # Apply known update
        local_update = {"weights": [3.0, 4.0, 5.0], "bias": 1.5}

        with patch("src.application.services.federated_learning_service.logger"):
            service._aggregate_model_update(local_update)

        # Check mathematical correctness of simple averaging
        expected_weights = [2.0, 3.0, 4.0]  # (1+3)/2, (2+4)/2, (3+5)/2
        expected_bias = 1.0  # (0.5 + 1.5) / 2

        assert service.global_model["weights"] == expected_weights
        assert service.global_model["bias"] == expected_bias

    @pytest.mark.parametrize("num_updates", [1, 5, 10, 50])
    @pytest.mark.asyncio
    async def test_multiple_sequential_updates(self, service, num_updates):
        """Test processing multiple sequential updates."""
        device_id = "sequential_test_device"

        for i in range(num_updates):
            update = {"weights": [0.1 * i, 0.2 * i, 0.3 * i], "bias": 0.05 * i}

            await service.process_local_model_update(device_id, update)

        # Model should be in a valid state after all updates
        final_model = service.get_global_model()
        assert len(final_model["weights"]) == 3
        assert isinstance(final_model["bias"], (int, float))

    def test_service_state_isolation(self):
        """Test that different service instances maintain separate state."""
        service1 = FederatedLearningService()
        service2 = FederatedLearningService()

        # Modify first service
        with patch("src.application.services.federated_learning_service.logger"):
            service1._aggregate_model_update({"weights": [1.0, 1.0, 1.0], "bias": 1.0})

        # Second service should be unaffected
        model1 = service1.get_global_model()
        model2 = service2.get_global_model()

        assert model1 != model2
        assert model2["weights"] == [0.1, 0.2, 0.3]  # Original values
        assert model2["bias"] == 0.05  # Original value
