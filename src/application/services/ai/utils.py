class AIServiceUtils:
    """Utility class providing helper methods for AI service."""

    @staticmethod
    def calculate_safety_score(
        content: str,
        moderation_result: dict,
        banned_topics: list[str],
    ) -> float:
        """Calculate content safety score."""
        if not moderation_result.get("safe", True):
            return 0.0

        # Base score
        score = 0.9

        # Check for banned topics
        content_lower = content.lower()
        for topic in banned_topics:
            if topic in content_lower:
                score -= 0.2

        # Positive content indicators
        positive_words = [
            "fun",
            "learn",
            "play",
            "happy",
            "friend",
            "adventure",
        ]
        for word in positive_words:
            if word in content_lower:
                score += 0.02

        return max(0.0, min(1.0, score))

    @staticmethod
    def check_age_appropriateness(content: str, age: int) -> bool:
        """Simple age appropriateness check."""
        if age < 5:
            # For very young children, restrict complex words
            restricted_words = ["kill", "death", "scary"]
            for word in restricted_words:
                if word in content.lower():
                    return False
        return True

    @staticmethod
    def analyze_sentiment(content: str) -> str:
        """Dummy sentiment analysis implementation."""
        positive_keywords = ["happy", "joy", "fun", "love"]
        negative_keywords = ["sad", "angry", "hate", "fear"]

        content_lower = content.lower()
        score = 0
        for word in positive_keywords:
            if word in content_lower:
                score += 1
        for word in negative_keywords:
            if word in content_lower:
                score -= 1

        if score > 0:
            return "positive"
        if score < 0:
            return "negative"
        return "neutral"

    @staticmethod
    def extract_topics(content: str) -> list[str]:
        """Extract main topics from content (dummy implementation)."""
        topics = []
        keywords = ["adventure", "friendship", "magic", "school", "family"]
        for word in keywords:
            if word in content.lower():
                topics.append(word)
        return topics

    @staticmethod
    def clean_content(content: str) -> str:
        """Basic content cleaning."""
        return content.strip()

    @staticmethod
    def get_age_group(age: int) -> str:
        """Get age group classification."""
        if age <= 5:
            return "toddler"
        if age <= 8:
            return "young child"
        if age <= 13:
            return "preteen"
        return "adult"

    @staticmethod
    def generate_cache_key(message: str, age: int, name: str) -> str:
        """Generate cache key for AI response caching."""
        safe_name = name.lower().replace(" ", "_")
        safe_message = message.lower().replace(" ", "_")[:30]
        return f"ai_response:{safe_name}:{age}:{safe_message}"
