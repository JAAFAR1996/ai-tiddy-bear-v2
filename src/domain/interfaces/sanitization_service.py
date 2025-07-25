from abc import ABC, abstractmethod


class ISanitizationService(ABC):
    """Abstract interface for content sanitization operations."""

    @abstractmethod
    async def sanitize_text(self, text: str) -> str:
        ...

    @abstractmethod
    async def detect_pii(self, text: str) -> bool:
        ...
