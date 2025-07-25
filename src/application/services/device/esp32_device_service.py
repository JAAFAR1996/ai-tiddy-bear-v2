"""Provides services for interacting with ESP32-based devices.

This service handles the processing of various data types from ESP32 devices,
including sensor readings, voice commands, gesture events, firmware update
statuses, device statuses, and edge AI results. It integrates with an event
bus to publish processed data for further system consumption.
"""

from src.application.interfaces.read_model_interfaces import IEventBus, get_event_bus
from src.domain.interfaces.device_authenticator import IDeviceAuthenticator
from src.domain.models.esp32_models import (
    ESP32DeviceStatus,
    ESP32EdgeAIResult,
    ESP32FirmwareUpdateStatus,
    ESP32GestureEvent,
    ESP32SensorReading,
    ESP32VoiceCommand,
)
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="esp32_device_service")


class ESP32DeviceService:
    """Service for processing data from ESP32 devices."""

    def __init__(
        self,
        event_bus: IEventBus = None,
        device_authenticator: IDeviceAuthenticator = None,
    ) -> None:
        """Initializes the ESP32 device service.

        Args:
            event_bus: An optional event bus for publishing events.
            device_authenticator: An optional device authenticator for validating device access.

        """
        self.event_bus = event_bus or get_event_bus()
        self.device_authenticator = device_authenticator
        self.logger = logger

    async def process_sensor_reading(self, reading: ESP32SensorReading) -> None:
        """Processes a sensor reading from an ESP32 device.

        Args:
            reading: The ESP32 sensor reading data.

        """
        if (
            self.device_authenticator
            and not await self.device_authenticator.authenticate_device(
                reading.device_id,
            )
        ):
            self.logger.warning(
                f"Unauthorized sensor reading attempt from device: {reading.device_id}",
            )
            return
        # Process sensor data (e.g., store in a time-series DB, trigger alerts)
        self.logger.info(
            f"Processing sensor reading from {reading.device_id}: {reading}",
        )
        # Example: Publish an event for further processing
        # await self.event_bus.publish(SensorReadingReceived(reading.device_id,
        # reading.timestamp, reading.temperature))

    async def process_voice_command(self, command: ESP32VoiceCommand) -> None:
        """Processes a voice command from an ESP32 device.

        Args:
            command: The ESP32 voice command data.

        """
        if (
            self.device_authenticator
            and not await self.device_authenticator.authenticate_device(
                command.device_id,
            )
        ):
            self.logger.warning(
                f"Unauthorized voice command attempt from device: {command.device_id}",
            )
            return
        # Process voice command (e.g., send to AI for response generation)
        self.logger.info(
            f"Processing voice command from {command.device_id}: {command.command_text}",
        )
        # Example: Publish an event for AI processing
        # await self.event_bus.publish(VoiceCommandReceived(command.device_id,
        # command.timestamp, command.command_text))

    async def process_gesture_event(self, gesture: ESP32GestureEvent) -> None:
        """Processes a gesture event from an ESP32 device.

        Args:
            gesture: The ESP32 gesture event data.

        """
        if (
            self.device_authenticator
            and not await self.device_authenticator.authenticate_device(
                gesture.device_id,
            )
        ):
            self.logger.warning(
                f"Unauthorized gesture event attempt from device: {gesture.device_id}",
            )
            return
        # Process gesture event (e.g., trigger a specific action on the bear)
        self.logger.info(
            f"Processing gesture event from {gesture.device_id}: {gesture.gesture_type}",
        )
        # Example: Publish an event for gesture interpretation
        # await self.event_bus.publish(GestureEventReceived(gesture.device_id,
        # gesture.timestamp, gesture.gesture_type))

    async def process_firmware_update_status(
        self,
        status: ESP32FirmwareUpdateStatus,
    ) -> None:
        """Processes a firmware update status from an ESP32 device.

        Args:
            status: The ESP32 firmware update status data.

        """
        if (
            self.device_authenticator
            and not await self.device_authenticator.authenticate_device(
                status.device_id,
            )
        ):
            self.logger.warning(
                f"Unauthorized firmware update status attempt from device: {status.device_id}",
            )
            return
        # Update firmware status in database or notify relevant service
        self.logger.info(
            f"Processing firmware update status from {status.device_id}: {status.status}",
        )

    async def process_device_status(self, status: ESP32DeviceStatus) -> None:
        """Processes a device status update from an ESP32 device.

        Args:
            status: The ESP32 device status data.

        """
        if (
            self.device_authenticator
            and not await self.device_authenticator.authenticate_device(
                status.device_id,
            )
        ):
            self.logger.warning(
                f"Unauthorized device status update attempt from device: {status.device_id}",
            )
            return
        # Update device status in database or notify relevant service
        self.logger.info(
            f"Processing device status from {status.device_id}: {status.status}",
        )

    async def process_edge_ai_result(self, result: ESP32EdgeAIResult) -> None:
        """Processes an edge AI result from an ESP32 device.

        Args:
            result: The ESP32 edge AI result data.

        """
        if (
            self.device_authenticator
            and not await self.device_authenticator.authenticate_device(
                result.device_id,
            )
        ):
            self.logger.warning(
                f"Unauthorized edge AI result attempt from device: {result.device_id}",
            )
            return
        # Process edge AI result (e.g., integrate with main AI, store for
        # analytics)
        self.logger.info(
            f"Processing edge AI result from {result.device_id}: {result.result_type}",
        )
