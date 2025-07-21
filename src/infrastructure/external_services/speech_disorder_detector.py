from typing import Any

from .speech_analysis_base import (
    AudioValidator,
    FeatureExtractor,
    SpeechAnalysisConfig,
    create_response_template,
)
from .speech_disorder_analyzer import DisorderAnalyzer

"""Speech Disorder Detection Service for AI Teddy Bear
Main service interface for speech disorder detection"""

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="infrastructure")


class SpeechDisorderDetector:
    """Speech disorder analyzer for children's speech pattern analysis."""

    def __init__(self) -> None:
        self.config = SpeechAnalysisConfig()
        self.validator = AudioValidator(self.config)
        self.feature_extractor = FeatureExtractor(self.config)
        self.disorder_analyzer = DisorderAnalyzer(self.config)

    async def analyze_speech_for_disorders(self, audio_data: bytes) -> dict[str, Any]:
        """Analyze speech audio for potential disorders."""
        try:
            # Validate audio data
            validation_result = await self.validator.validate_audio_data(audio_data)
            if not validation_result["valid"]:
                return self._create_error_response(validation_result["error"])

            # Extract audio features
            features = await self.feature_extractor.extract_audio_features(audio_data)
            if "error" in features:
                return self._create_error_response(features["error"])

            # Analyze for disorders
            analysis_result = await self.disorder_analyzer.analyze_for_disorders(
                features,
            )

            # Add metadata
            analysis_result["audio_quality"] = validation_result
            analysis_result["features_extracted"] = True

            logger.info(
                f"Speech disorder analysis completed. Found {len(analysis_result.get('disorders_detected', []))} disorders",
            )
            return analysis_result
        except Exception as e:
            logger.error(f"Speech disorder analysis failed: {e}")
            return self._create_error_response(f"Analysis failed: {e!s}")

    def _create_error_response(self, error_message: str) -> dict[str, Any]:
        """Create standardized error response."""
        response = create_response_template()
        response["error"] = error_message
        response["analysis_quality"] = "failed"
        return response

    async def get_analysis_capabilities(self) -> dict[str, Any]:
        """Get information about analysis capabilities."""
        return {
            "supported_formats": self.config.supported_formats,
            "min_duration": self.config.min_audio_duration,
            "max_duration": self.config.max_audio_duration,
            "supported_disorders": list(self.config.disorder_patterns.keys()),
            "version": "1.0.0",
        }

    async def validate_audio_format(self, audio_data: bytes) -> dict[str, Any]:
        """Validate audio format without full analysis."""
        return await self.validator.validate_audio_data(audio_data)


# Factory function
def create_speech_disorder_detector() -> SpeechDisorderDetector:
    """Create and return a speech disorder detector instance."""
    return SpeechDisorderDetector()


# Backward compatibility
async def analyze_speech_for_disorders(audio_data: bytes) -> dict[str, Any]:
    """Backward compatibility function."""
    detector = create_speech_disorder_detector()
    return await detector.analyze_speech_for_disorders(audio_data)
