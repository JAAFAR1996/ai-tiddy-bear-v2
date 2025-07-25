from typing import Any

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="infrastructure")


class SafetyAnalyzer:
    """Analyzes the safety of AI responses for child-friendliness and COPPA compliance."""

    def __init__(self, openai_client: Any):
        self.openai_client = openai_client
        self.forbidden_keywords = [
            "violence",
            "weapon",
            "kill",
            "death",
            "blood",
            "scary",
            "nightmare",
            "monster",
            "ghost",
            "demon",
            "hell",
            "damn",
            "adult",
            "sex",
            "drug",
            "alcohol",
            "cigarette",
            "smoke",
            "hate",
            "harm",
            "danger",
            "exploit",
            "abuse",
            "suicide",
            "curse",
            "swear",
            "porn",
            "nude",
            "sexual",
            "explicit",
        ]
        logger.info("SafetyAnalyzer initialized.")

    async def analyze_safety(self, text: str) -> dict[str, Any]:
        """Performs a multi-layer safety analysis on the given text using real AI moderation if available."""
        flagged_keywords = []
        text_lower = text.lower()
        # Keyword-based filtering
        for keyword in self.forbidden_keywords:
            if keyword in text_lower:
                flagged_keywords.append(keyword)

        ai_moderation_score = 0.0
        ai_flagged_categories = []
        ai_details = ""
        # Real AI moderation layer if openai_client is available
        if self.openai_client is not None:
            try:
                moderation_response = await self.openai_client.moderations.create(
                    input=text
                )
                moderation_result = moderation_response.results[0]
                ai_moderation_score = float(
                    moderation_result.category_scores.get("sexual", 0.0)
                )
                # Collect all flagged categories
                ai_flagged_categories = [
                    cat
                    for cat, flagged in moderation_result.categories.items()
                    if flagged
                ]
                ai_details = "OpenAI moderation API used"
            except Exception as e:
                logger.warning(f"AI moderation API failed: {e}")
                ai_details = "AI moderation unavailable, fallback to keyword only"
        else:
            ai_details = "AI moderation unavailable, fallback to keyword only"

        is_safe = (
            not bool(flagged_keywords or ai_flagged_categories)
            and ai_moderation_score < 0.7
        )
        all_flagged = list(set(flagged_keywords + ai_flagged_categories))
        return {
            "safe": is_safe,
            "safety_score": 1.0
            - max(ai_moderation_score, 0.9 if flagged_keywords else 0.0),
            "flagged_categories": all_flagged,
            "analysis_details": f"Keyword + AI moderation. {ai_details}",
        }
