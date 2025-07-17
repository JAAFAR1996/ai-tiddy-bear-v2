from datetime import datetime
from typing import Dict, Any, Optional, List
import asyncio
import logging
from .speech_analysis_base import SpeechAnalysisConfig, create_response_template

"""Speech Disorder Analysis Engine
Core disorder detection and analysis logic"""

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="infrastructure")


class DisorderAnalyzer:
    """Core disorder analysis engine."""

    def __init__(self, config: SpeechAnalysisConfig) -> None:
        self.config = config

    async def analyze_for_disorders(
        self, features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze extracted features for speech disorders."""
        analysis_result = create_response_template()
        try:
            # Analyze different disorder types
            stuttering_analysis = await self._analyze_stuttering(features)
            lisping_analysis = await self._analyze_lisping(features)
            articulation_analysis = await self._analyze_articulation(features)
            voice_analysis = await self._analyze_voice_disorder(features)

            # Combine results
            all_analyses = [
                stuttering_analysis,
                lisping_analysis,
                articulation_analysis,
                voice_analysis,
            ]

            # Process results
            for analysis in all_analyses:
                if analysis["detected"]:
                    analysis_result["disorders_detected"].append(
                        analysis["disorder_type"],
                    )
                    analysis_result["confidence_scores"][
                        analysis["disorder_type"]
                    ] = analysis["confidence"]
                    analysis_result["recommendations"].extend(
                        analysis["recommendations"],
                    )

            # Determine overall severity
            analysis_result["severity_level"] = self._calculate_severity(
                all_analyses
            )
            analysis_result["professional_referral_needed"] = (
                self._needs_referral(
                    all_analyses,
                )
            )

            return analysis_result
        except Exception as e:
            logger.error(f"Disorder analysis error: {e}")
            return {
                "error": f"Disorder analysis failed: {e!s}",
                "analysis_timestamp": datetime.now().isoformat(),
            }

    async def _analyze_stuttering(
        self, features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze for stuttering patterns."""
        # Mock stuttering detection logic
        speech_rate = features.get("temporal_features", {}).get(
            "speech_rate", 5.0
        )
        silence_ratio = features.get("temporal_features", {}).get(
            "silence_ratio", 0.1
        )

        # Simple heuristic: stuttering often correlates with irregular speech patterns
        stuttering_indicators = 0
        confidence = 0.0

        if speech_rate < 3.0:  # Slow speech rate
            stuttering_indicators += 1
            confidence += 0.3

        if silence_ratio > 0.2:  # Frequent pauses
            stuttering_indicators += 1
            confidence += 0.4

        detected = (
            confidence
            > self.config.disorder_patterns["stuttering"][
                "confidence_threshold"
            ]
        )

        return {
            "disorder_type": "stuttering",
            "detected": detected,
            "confidence": min(confidence, 1.0),
            "indicators": stuttering_indicators,
            "recommendations": (
                [
                    "Practice slow, deliberate speech patterns",
                    "Use breathing exercises before speaking",
                    "Consider speech therapy consultation",
                ]
                if detected
                else []
            ),
        }

    async def _analyze_lisping(
        self, features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze for lisping patterns."""
        # Mock lisping detection
        spectral_centroid = features.get("spectral_features", {}).get(
            "spectral_centroid",
            2500,
        )

        # Lisping often affects high-frequency sounds
        confidence = 0.0
        detected = False

        if (
            spectral_centroid < 2000
        ):  # Lower spectral centroid might indicate lisping
            confidence = 0.65
            detected = True

        return {
            "disorder_type": "lisping",
            "detected": detected,
            "confidence": confidence,
            "indicators": ["s_sound_distortion"] if detected else [],
            "recommendations": (
                [
                    "Practice tongue placement exercises",
                    "Work on s and z sound production",
                    "Consider articulation therapy",
                ]
                if detected
                else []
            ),
        }

    async def _analyze_articulation(
        self, features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze for articulation disorders."""
        # Mock articulation analysis
        zero_crossing_rate = features.get("spectral_features", {}).get(
            "zero_crossing_rate",
            0.15,
        )

        confidence = 0.0
        detected = False

        if (
            zero_crossing_rate > 0.2
        ):  # High zero crossing rate might indicate articulation issues
            confidence = 0.6
            detected = True

        return {
            "disorder_type": "articulation_disorder",
            "detected": detected,
            "confidence": confidence,
            "indicators": ["sound_substitution"] if detected else [],
            "recommendations": (
                [
                    "Practice specific sound production",
                    "Use mirror exercises for visual feedback",
                    "Consider articulation therapy",
                ]
                if detected
                else []
            ),
        }

    async def _analyze_voice_disorder(
        self, features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze for voice disorders."""
        # Mock voice disorder detection
        fundamental_frequency = features.get("prosodic_features", {}).get(
            "fundamental_frequency",
            180,
        )
        intensity = features.get("prosodic_features", {}).get("intensity", 65)

        confidence = 0.0
        detected = False

        if fundamental_frequency < 100 or fundamental_frequency > 400:
            confidence += 0.3

        if intensity < 45 or intensity > 85:
            confidence += 0.4

        detected = (
            confidence
            > self.config.disorder_patterns["voice_disorder"][  # type: ignore
                "confidence_threshold"
            ]
        )

        return {
            "disorder_type": "voice_disorder",
            "detected": detected,
            "confidence": min(confidence, 1.0),
            "indicators": ["hoarseness"] if detected else [],
            "recommendations": (
                [
                    "Practice proper breathing techniques",
                    "Avoid vocal strain",
                    "Consider voice therapy consultation",
                ]
                if detected
                else []
            ),
        }

    def _calculate_severity(self, analyses: List[Dict[str, Any]]) -> str:
        """Calculate overall severity level."""
        detected_disorders = [a for a in analyses if a["detected"]]

        if not detected_disorders:
            return "normal"

        max_confidence = max(a["confidence"] for a in detected_disorders)

        if max_confidence > 0.9:
            return "severe"
        if max_confidence > 0.7:
            return "moderate"
        return "mild"

    def _needs_referral(self, analyses: List[Dict[str, Any]]) -> bool:
        """Determine if professional referral is needed."""
        detected_disorders = [a for a in analyses if a["detected"]]

        if len(detected_disorders) >= 2:  # Multiple disorders
            return True

        if any(
            a["confidence"] > 0.8 for a in detected_disorders
        ):  # High confidence
            return True

        return False
