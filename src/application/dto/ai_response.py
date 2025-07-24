from dataclasses import dataclass, field


@dataclass
class AIResponse:
    response_text: str = field(metadata={"description": "AI generated text response"})
    audio_response: bytes = field(metadata={"description": "Binary audio data"})
    emotion: str = field(
        metadata={"description": "Detected emotion (happy, sad, excited, etc.)"}
    )
    sentiment: float = field(
        metadata={
            "description": ("Sentiment score from -1.0 (negative) " "to 1.0 (positive)")
        }
    )
    safe: bool = field(metadata={"description": "Content safety validation result"})
    conversation_id: str | None = field(
        default=None,
        metadata={"description": "Conversation tracking ID"},
    )
    safety_score: float = field(
        default=1.0,
        metadata={"description": "Detailed safety score (0.0-1.0)"},
    )
    moderation_flags: list[str] = field(
        default_factory=list,
        metadata={"description": "Content moderation warnings"},
    )
    age_appropriate: bool = field(
        default=True,
        metadata={"description": "COPPA age appropriateness"},
    )

    def __post_init__(self) -> None:
        if (
            not isinstance(self.sentiment, (int, float))
            or not -1.0 <= self.sentiment <= 1.0
        ):
            raise ValueError(
                f"Sentiment must be between -1.0 and 1.0, " f"got {self.sentiment}",
            )

        if (
            not isinstance(self.safety_score, (int, float))
            or not 0.0 <= self.safety_score <= 1.0
        ):
            raise ValueError(
                f"Safety score must be between 0.0 and 1.0, "
                f"got {self.safety_score}",
            )

        if not self.response_text.strip():
            raise ValueError("Response text cannot be empty")

        # Mark as unsafe if safety score is too low
        if self.safety_score < 0.8:
            self.safe = False
            if "low_safety_score" not in self.moderation_flags:
                self.moderation_flags.append("low_safety_score")
