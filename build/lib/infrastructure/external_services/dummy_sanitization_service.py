import logging
from src.domain.interfaces.sanitization_service import ISanitizationService
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="dummy_sanitization_service")

class DummySanitizationService(ISanitizationService):
    """
    Dummy implementation of ISanitizationService for simulation purposes.
    """
    async def sanitize_text(self, text: str) -> str:
        self.logger.info(f"[DUMMY SANITIZATION] Sanitizing text: {text[:50]}...")
        # Simple sanitization: remove leading/trailing whitespace and replace multiple spaces
        sanitized_text = " ".join(text.strip().split())
        self.logger.debug(f"[DUMMY SANITIZATION] Sanitized to: {sanitized_text[:50]}...")
        return sanitized_text

    async def detect_pii(self, text: str) -> bool:
        self.logger.info(f"[DUMMY SANITIZATION] Detecting PII in text: {text[:50]}...")
        # Dummy PII detection: simple check for common patterns like email or phone number formats
        if "@" in text or any(char.isdigit() for char in text) and len(text) > 7:
            self.logger.warning("[DUMMY SANITIZATION] Possible PII detected. Returning True.")
            return True
        self.logger.debug("[DUMMY SANITIZATION] No PII detected. Returning False.")
        return False

    def __init__(self) -> None:
        self.logger = logger 