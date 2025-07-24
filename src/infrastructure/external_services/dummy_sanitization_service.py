from src.domain.interfaces.sanitization_service import ISanitizationService
from src.infrastructure.logging_config import get_logger

try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine

    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False

logger = get_logger(__name__, component="sanitization_service")


class SanitizationService(ISanitizationService):
    """Production implementation of ISanitizationService using Presidio for PII detection and anonymization."""

    def __init__(self) -> None:
        self.logger = logger
        if PRESIDIO_AVAILABLE:
            self.analyzer = AnalyzerEngine()
            self.anonymizer = AnonymizerEngine()
        else:
            self.analyzer = None
            self.anonymizer = None

    async def sanitize_text(self, text: str) -> str:
        if not PRESIDIO_AVAILABLE:
            self.logger.error("Presidio not installed. Cannot sanitize text.")
            raise RuntimeError(
                "Presidio not installed. Please install presidio-analyzer and presidio-anonymizer."
            )
        try:
            results = self.analyzer.analyze(text=text, language="en")
            if not results:
                return text
            anonymized = self.anonymizer.anonymize(text=text, analyzer_results=results)
            self.logger.info("Text sanitized using Presidio.")
            return anonymized.text
        except Exception as e:
            self.logger.exception(f"Sanitization error: {e}")
            raise

    async def detect_pii(self, text: str) -> bool:
        if not PRESIDIO_AVAILABLE:
            self.logger.error("Presidio not installed. Cannot detect PII.")
            raise RuntimeError(
                "Presidio not installed. Please install presidio-analyzer."
            )
        try:
            results = self.analyzer.analyze(text=text, language="en")
            has_pii = bool(results)
            self.logger.info(f"PII detected: {has_pii}")
            return has_pii
        except Exception as e:
            self.logger.exception(f"PII detection error: {e}")
            raise
