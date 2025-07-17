from datetime import datetime, timedelta
from typing import Any

# Constants for child analytics
EMOTION_NEUTRAL_BASELINE = 0.5
MINIMUM_EMOTION_SAMPLES = 2
EMOTION_ANALYSIS_WINDOW = 10  # Last N interactions to analyze
MINIMUM_STABILITY_SCORE = 0.0
MAXIMUM_STABILITY_SCORE = 1.0
SPEECH_ANALYSIS_DAYS = 30
CLARITY_THRESHOLD_LOW = 0.7
CLARITY_THRESHOLD_CRITICAL = 0.5
VOCABULARY_DEVELOPMENT_FACTOR = 10  # words per month of age
VOCABULARY_THRESHOLD_RATIO = 0.7
REPETITION_THRESHOLD_LOW = 0.3
REPETITION_THRESHOLD_HIGH = 0.5
MINIMUM_CHILD_AGE_MONTHS = 36  # 3 years default
MINIMUM_VOCABULARY_SIZE = 50
TRIVIA_SCORE_INCREMENT = 10
RIDDLE_SCORE_INCREMENT = 15
STORY_SCORE_INCREMENT = 10


class ChildAnalytics:
    """Analytics service for monitoring child emotional and speech patterns."""

    def __init__(self) -> None:
        """Initialize child analytics service with empty data storage."""
        self.emotion_history = {}  # In production, this would be a database
        self.speech_data = {}

    def calculate_emotion_stability(self, child_id: str) -> float:
        """Calculate emotional stability score for a child (0.0 to 1.0)
        Higher score = more stable emotions.
        """
        try:
            if child_id not in self.emotion_history:
                return EMOTION_NEUTRAL_BASELINE  # Neutral baseline

            emotions = self.emotion_history[child_id]
            if len(emotions) < MINIMUM_EMOTION_SAMPLES:
                return EMOTION_NEUTRAL_BASELINE  # Not enough data

            # Calculate variance in emotions (lower variance = more stable)
            emotion_values = [
                emotion.get("score", EMOTION_NEUTRAL_BASELINE)
                for emotion in emotions[-EMOTION_ANALYSIS_WINDOW:]
            ]  # Last N interactions

            if not emotion_values:
                return EMOTION_NEUTRAL_BASELINE

            mean_emotion = sum(emotion_values) / len(emotion_values)
            variance = sum((x - mean_emotion) ** 2 for x in emotion_values) / len(
                emotion_values,
            )

            # Convert variance to stability score (inverted and normalized)
            stability_score = max(
                MINIMUM_STABILITY_SCORE,
                min(MAXIMUM_STABILITY_SCORE, MAXIMUM_STABILITY_SCORE - variance),
            )

            return stability_score
        except Exception:
            return EMOTION_NEUTRAL_BASELINE

    def get_speech_concerns(self, child_id: str) -> list[dict[str, Any]]:
        """Analyze speech patterns and return potential concerns
        Returns list of concern objects with type, severity, and recommendations.
        """
        try:
            if child_id not in self.speech_data:
                return []

            speech_history = self.speech_data[child_id]
            concerns = []

            # Analyze recent speech patterns
            recent_data = [
                entry
                for entry in speech_history
                if entry.get("timestamp", datetime.min)
                > datetime.now() - timedelta(days=SPEECH_ANALYSIS_DAYS)
            ]

            if not recent_data:
                return []

            # Check for clarity issues
            clarity_scores = [entry.get("clarity_score", 1.0) for entry in recent_data]
            avg_clarity = (
                sum(clarity_scores) / len(clarity_scores) if clarity_scores else 1.0
            )

            if avg_clarity < CLARITY_THRESHOLD_LOW:
                concerns.append(
                    {
                        "type": "clarity",
                        "severity": (
                            "medium"
                            if avg_clarity < CLARITY_THRESHOLD_CRITICAL
                            else "low"
                        ),
                        "score": avg_clarity,
                        "description": "Speech clarity may need attention",
                        "recommendation": "Consider speech therapy evaluation",
                    },
                )

            # Check for vocabulary development
            vocabulary_size = len(
                {entry.get("words_used", []) for entry in recent_data},
            )
            age_months = speech_history[0].get(
                "child_age_months",
                MINIMUM_CHILD_AGE_MONTHS,
            )  # Default 3 years
            expected_vocabulary = max(
                MINIMUM_VOCABULARY_SIZE,
                age_months * VOCABULARY_DEVELOPMENT_FACTOR,
            )  # Rough estimate

            if vocabulary_size < expected_vocabulary * VOCABULARY_THRESHOLD_RATIO:
                concerns.append(
                    {
                        "type": "vocabulary",
                        "severity": "medium",
                        "vocabulary_size": vocabulary_size,
                        "expected_range": expected_vocabulary,
                        "description": "Vocabulary development may be below expected range",
                        "recommendation": "Encourage more reading and verbal interaction",
                    },
                )

            # Check for speech patterns (repetition, stuttering indicators)
            repetition_rate = sum(
                1 for entry in recent_data if entry.get("repetition_detected", False)
            ) / len(recent_data)

            if (
                repetition_rate > REPETITION_THRESHOLD_LOW
            ):  # More than threshold of interactions show repetition
                concerns.append(
                    {
                        "type": "fluency",
                        "severity": (
                            "medium"
                            if repetition_rate > REPETITION_THRESHOLD_HIGH
                            else "low"
                        ),
                        "rate": repetition_rate,
                        "description": "Possible fluency concerns detected",
                        "recommendation": "Monitor speech patterns and consider professional assessment",
                    },
                )

            return concerns
        except Exception:
            return []

    def record_emotion_data(
        self,
        child_id: str,
        emotion_score: float,
        context: str = "",
    ) -> None:
        """Record emotion data for analysis."""
        if child_id not in self.emotion_history:
            self.emotion_history[child_id] = []

        self.emotion_history[child_id].append(
            {"timestamp": datetime.now(), "score": emotion_score, "context": context},
        )

    def record_speech_data(
        self,
        child_id: str,
        speech_analysis: dict[str, Any],
    ) -> None:
        """Record speech analysis data."""
        if child_id not in self.speech_data:
            self.speech_data[child_id] = []

        speech_analysis["timestamp"] = datetime.now()
        self.speech_data[child_id].append(speech_analysis)
