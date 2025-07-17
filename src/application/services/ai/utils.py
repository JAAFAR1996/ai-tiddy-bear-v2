"""
AI Service Utilities - Extracted from main service for better maintainability
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
import hashlib
import random
from .models import AIResponse

class AIServiceUtils:
    """Utility functions for AI service operations"""
    @staticmethod
    def extract_topics(content: str) -> List[str]:
        """Extract topics from content using keyword matching"""
        topics = []
        topic_keywords = {
            "emotions": ["happy", "sad", "angry", "excited", "scared", "love"],
            "learning": ["learn", "study", "school", "read", "write"],
            "play": ["play", "game", "toy", "fun", "adventure"],
            "creativity": ["draw", "paint", "create", "imagine", "story"],
            "friendship": ["friend", "together", "share", "help", "kind"],
            "nature": ["animal", "tree", "flower", "outside", "nature"]
        }
        content_lower = content.lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append(topic)
        return topics

    @staticmethod
    def clean_content(content: str) -> str:
        """Clean and sanitize content"""
        # Remove any potential harmful content
        # Add more cleaning logic as needed
        return content.strip()

    @staticmethod
    def get_age_group(age: int) -> str:
        """Get age group classification"""
        if age <= 3:
            return "toddler"
        elif age <= 5:
            return "preschool"
        elif age <= 8:
            return "early_elementary"
        elif age <= 12:
            return "elementary"
        else:
            return "middle_school"

    @staticmethod
    def generate_cache_key(message: str, age: int, name: str) -> str:
        """Generate cache key for response"""
        key_data = f"{message}:{age}:{name}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]

    @staticmethod
    def get_fallback_response(child_name: str, child_age: int) -> AIResponse:
        """Get safe fallback response when AI service fails"""
        fallback_responses = [
            f"Hi {child_name}! I'm having a little trouble thinking right now. Can you tell me about your favorite toy?",
            f"Hello {child_name}! Let's talk about something fun. What makes you happy today?",
            f"Hey there, {child_name}! I love chatting with you. What's your favorite color?"
        ]
        content = random.choice(fallback_responses)
        return AIResponse(
            content=content,
            safety_score=1.0,
            age_appropriate=True,
            sentiment="positive",
            topics=["friendship"],
            processing_time=0.001,
            cached=False,
            moderation_flags=["fallback_response"]
        )

    @staticmethod
    def calculate_safety_score(content: str, moderation_result: Dict, banned_topics: List[str]) -> float:
        """Calculate content safety score"""
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
        positive_words = ["fun", "learn", "play", "happy", "friend", "adventure"]
        for word in positive_words:
            if word in content_lower:
                score += 0.02
        return max(0.0, min(1.0, score))

    @staticmethod
    def check_age_appropriateness(content: str, age: int) -> bool:
        """Check if content is appropriate for child's age"""
        content_lower = content.lower()
        # Age-specific inappropriate content
        if age < 5:  # Toddlers
            inappropriate = ["scary", "monster", "dark", "alone"]
        elif age < 8:  # Preschool
            inappropriate = ["complex math", "advanced concepts"]
        else:  # School age
            inappropriate = []
        return not any(word in content_lower for word in inappropriate)

    @staticmethod
    def analyze_sentiment(content: str) -> str:
        """Simple sentiment analysis"""
        positive_words = ["happy", "fun", "great", "awesome", "wonderful", "amazing"]
        negative_words = ["sad", "bad", "terrible", "awful", "scary", "worried"]
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"