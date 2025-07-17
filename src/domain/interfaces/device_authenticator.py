from abc import ABC, abstractmethod
from uuid import UUID


class IDeviceAuthenticator(ABC):
    @abstractmethod
    async def authenticate_device(self, device_id: UUID) -> bool:
        """Authenticates an ESP32 device based on its ID.

        Args:
            device_id: The UUID of the device to authenticate.

        Returns:
            True if the device is authenticated, False otherwise.

        """
