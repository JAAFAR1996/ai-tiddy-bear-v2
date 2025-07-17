import logging
from typing import Any, Dict

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

    async def analyze_safety(self, text: str) -> Dict[str, Any]:
        """Performs a multi-layer safety analysis on the given text.
        Args:
            text: The text to analyze.
        Returns:
            A dictionary containing safety analysis results.
        """
        flagged_keywords = []
        text_lower = text.lower()
        # Keyword-based filtering
        for keyword in self.forbidden_keywords:
            if keyword in text_lower:
                flagged_keywords.append(keyword)
        # Placeholder for more advanced AI-based moderation
        # In a real system, this would call OpenAI's moderation API or a custom model
        ai_moderation_score = 0.0  # Assume safe by default for mock
        if flagged_keywords:
            ai_moderation_score = 0.9  # Simulate high risk if keywords found
        is_safe = not bool(flagged_keywords) and ai_moderation_score < 0.9
        return {
            "safe": is_safe,
            "safety_score": 1.0 - ai_moderation_score,  # 1.0 is perfectly safe
            "flagged_categories": flagged_keywords,
            "analysis_details": "Keyword and mock AI moderation",
        }