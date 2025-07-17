"""
Safety Filter for ChatGPT - Child Safety Content Filtering
"""

from typing import Dict, List, Any
import logging
import re
from src.domain.constants import (
    MAX_RESPONSE_LENGTH,
    MAX_NEGATIVE_INDICATORS as NEGATIVE_THRESHOLD,
    EARLY_CHILD_MAX_AGE as MIN_AGE_COMPLEX_CONTENT,
    TODDLER_MAX_AGE as MAX_AGE_SIMPLE_CONTENT,
)

from src.infrastructure.logging_config import get_logger
logger = get_logger(__name__, component="infrastructure")

class SafetyFilter:
    """Safety filter for child - specific content filtering and protection."""
    def __init__(self) -> None:
        # Forbidden words for children
        self.forbidden_words = [
            "violence", "weapon", "kill", "death", "blood", "scary",
            "nightmare", "monster", "ghost", "demon", "hell", "damn",
            "adult", "sex", "drug", "alcohol", "cigarette", "smoke"
        ]
        # Safe topics for children
        self.safe_topics = [
            "animals", "nature", "friendship", "family", "school",
            "books", "games", "art", "music", "sports", "food",
            "colors", "shapes", "numbers", "letters", "stories"
        ]
        # Child safety rules
        self.child_safety_rules = [
            "Always use child-friendly language",
            "Avoid scary or violent content",
            "Keep responses age-appropriate",
            "Encourage learning and creativity",
            "Be supportive and positive",
            "Don't discuss adult topics",
            "Redirect inappropriate questions to safe topics"
        ]

    def analyze_message_safety(self, message: str) -> Dict[str, Any]:
        """Analyze message safety for child - appropriate content."""
        message_lower = message.lower()
        # Check for forbidden words
        forbidden_found = [word for word in self.forbidden_words if word in message_lower]
        if forbidden_found:
            return {
                "safe": False,
                "issues": forbidden_found,
                "severity": "high",
                "reason": f"Contains forbidden words: {', '.join(forbidden_found)}"
            }
        # Check for dangerous patterns
        dangerous_patterns = [
            r"how to (hurt|kill|fight)",
            r"where to (buy|get|find) (weapon|drug|alcohol)",
            r"(scary|frightening|terrifying) (story|movie|game)",
            r"(violence|violent|aggressive) (game|movie|show)"
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, message_lower):
                return {
                    "safe": False,
                    "issues": [pattern],
                    "severity": "high",
                    "reason": f"Contains dangerous pattern: {pattern}"
                }
        return {
            "safe": True,
            "issues": [],
            "severity": "none",
            "reason": "Message is safe for children"
        }

    def sanitize_message(self, message: str) -> str:
        """Clean message from inappropriate content."""
        # Replace inappropriate words
        replacements = {
            "stupid": "silly",
            "dumb": "funny",
            "hate": "don't like",
            "kill": "stop",
            "die": "sleep",
            "fight": "play",
            "scary": "interesting",
            "monster": "funny creature"
        }
        cleaned_message = message
        for bad_word, replacement in replacements.items():
            cleaned_message = re.sub(
                r'\b' + re.escape(bad_word) + r'\b',
                replacement,
                cleaned_message,
                flags=re.IGNORECASE
            )
        return cleaned_message

    def analyze_response_safety(self, response: str) -> Dict[str, Any]:
        """Analyze response safety for child - appropriate content."""
        response_lower = response.lower()
        # Check for forbidden words in response
        forbidden_found = [word for word in self.forbidden_words if word in response_lower]
        if forbidden_found:
            return {
                "safe": False,
                "issues": forbidden_found,
                "severity": "high",
                "reason": f"Response contains forbidden content: {', '.join(forbidden_found)}"
            }
        # Check for negative tone
        negative_indicators = [
            "don't", "can't", "won't", "never", "impossible",
            "difficult", "hard", "trouble", "problem", "wrong"
        ]
        negative_count = sum(1 for indicator in negative_indicators if indicator in response_lower)
        if negative_count > NEGATIVE_THRESHOLD:
            return {
                "safe": False,
                "issues": ["too_negative"],
                "severity": "medium",
                "reason": "Response is too negative for children"
            }
        # Check appropriate length
        if len(response) > MAX_RESPONSE_LENGTH:
            return {
                "safe": False,
                "issues": ["too_long"],
                "severity": "low",
                "reason": "Response is too long for children's attention span"
            }
        return {
            "safe": True,
            "issues": [],
            "severity": "none",
            "reason": "Response is safe and appropriate for children"
        }

    def check_age_appropriateness(self, content: str, child_age: int) -> Dict[str, Any]:
        """Check content appropriateness for child age."""
        age_inappropriate_content = {
            (0, 4): ["complex", "difficult", "advanced", "sophisticated"],
            (5, 7): ["abstract", "philosophical", "theoretical", "complex"],
            (8, 10): ["mature", "adult", "advanced", "complicated"],
            (11, 12): ["adult", "mature", "sophisticated", "complex"]
        }
        content_lower = content.lower()
        for age_range, inappropriate_words in age_inappropriate_content.items():
            if age_range[0] <= child_age <= age_range[1]:
                found_words = [word for word in inappropriate_words if word in content_lower]
                if found_words:
                    return {
                        "appropriate": False,
                        "issues": found_words,
                        "reason": f"Content contains age-inappropriate words for {child_age}-year-old"
                    }
        return {
            "appropriate": True,
            "issues": [],
            "reason": f"Content is appropriate for {child_age}-year-old"
        }

    def get_safe_alternative_topics(self, unsafe_topic: str) -> List[str]:
        """Get safe alternative topics for redirection."""
        topic_alternatives = {
            "violence": ["friendship", "cooperation", "helping others"],
            "scary": ["adventure", "exploration", "discovery"],
            "death": ["nature cycles", "plant growth", "animal habitats"],
            "fight": ["games", "sports", "teamwork"],
            "monster": ["friendly animals", "imaginary friends", "cartoon characters"],
            "weapon": ["tools", "art supplies", "musical instruments"],
            "adult": ["family", "growing up", "learning new things"]
        }
        unsafe_lower = unsafe_topic.lower()
        for key, alternatives in topic_alternatives.items():
            if key in unsafe_lower:
                return alternatives
        return self.safe_topics[:3]  # Return first 3 safe topics as default