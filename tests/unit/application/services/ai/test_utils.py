"""
Tests for AI Utils
Testing AI service utility functions for content analysis and safety.
"""

import pytest
from unittest.mock import patch
import hashlib

from src.application.services.ai.utils import AIServiceUtils
from src.application.services.ai.models import AIResponse


class TestAIServiceUtils:
    """Test the AI Service Utils."""
    
    def test_extract_topics_emotions(self):
        """Test topic extraction for emotion-related content."""
        content = "I'm feeling happy and excited about playing with my friends"
        topics = AIServiceUtils.extract_topics(content)
        
        assert "emotions" in topics
        assert "play" in topics
        assert "friendship" in topics
    
    def test_extract_topics_learning(self):
        """Test topic extraction for learning-related content."""
        content = "I want to learn math and study science at school"
        topics = AIServiceUtils.extract_topics(content)
        
        assert "learning" in topics
        assert len(topics) >= 1
    
    def test_extract_topics_creativity(self):
        """Test topic extraction for creativity-related content."""
        content = "Let me draw a picture and create a beautiful story"
        topics = AIServiceUtils.extract_topics(content)
        
        assert "creativity" in topics
    
    def test_extract_topics_nature(self):
        """Test topic extraction for nature-related content."""
        content = "Look at the beautiful flowers and animals outside in nature"
        topics = AIServiceUtils.extract_topics(content)
        
        assert "nature" in topics
    
    def test_extract_topics_multiple_categories(self):
        """Test topic extraction with content matching multiple categories."""
        content = "I love to play games with my animal friends and learn about nature"
        topics = AIServiceUtils.extract_topics(content)
        
        assert "play" in topics
        assert "nature" in topics
        assert "friendship" in topics
        assert len(topics) >= 3
    
    def test_extract_topics_no_matches(self):
        """Test topic extraction with content that doesn't match any categories."""
        content = "This is completely unrelated content with no keywords"
        topics = AIServiceUtils.extract_topics(content)
        
        assert topics == []
    
    def test_extract_topics_case_insensitive(self):
        """Test that topic extraction is case insensitive."""
        content_variations = [
            "I LOVE to PLAY games",
            "I Love To Play Games", 
            "i love to play games",
            "I love to PLAY GAMES"
        ]
        
        for content in content_variations:
            topics = AIServiceUtils.extract_topics(content)
            assert "play" in topics
    
    def test_clean_content_basic(self):
        """Test basic content cleaning."""
        test_cases = [
            ("  Hello world  ", "Hello world"),
            ("\n\nContent with newlines\n\n", "Content with newlines"),
            ("\t\tTabbed content\t\t", "Tabbed content"),
            ("Already clean content", "Already clean content"),
            ("", ""),
            ("   ", "")
        ]
        
        for input_content, expected in test_cases:
            result = AIServiceUtils.clean_content(input_content)
            assert result == expected
    
    def test_get_age_group_classifications(self):
        """Test age group classification for different ages."""
        test_cases = [
            (2, "toddler"),
            (3, "toddler"),
            (4, "preschool"),
            (5, "preschool"),
            (6, "early_elementary"),
            (7, "early_elementary"),
            (8, "early_elementary"),
            (9, "elementary"),
            (10, "elementary"),
            (11, "elementary"),
            (12, "elementary"),
            (13, "middle_school"),
            (14, "middle_school")
        ]
        
        for age, expected_group in test_cases:
            result = AIServiceUtils.get_age_group(age)
            assert result == expected_group
    
    def test_get_age_group_boundary_conditions(self):
        """Test age group classification at boundary conditions."""
        # Test exact boundaries
        assert AIServiceUtils.get_age_group(3) == "toddler"
        assert AIServiceUtils.get_age_group(4) == "preschool"
        assert AIServiceUtils.get_age_group(5) == "preschool"
        assert AIServiceUtils.get_age_group(6) == "early_elementary"
        assert AIServiceUtils.get_age_group(8) == "early_elementary"
        assert AIServiceUtils.get_age_group(9) == "elementary"
        assert AIServiceUtils.get_age_group(12) == "elementary"
        assert AIServiceUtils.get_age_group(13) == "middle_school"
    
    def test_generate_cache_key_consistency(self):
        """Test cache key generation consistency."""
        message = "Hello teddy bear"
        age = 6
        name = "Alice"
        
        # Generate multiple times - should be consistent
        key1 = AIServiceUtils.generate_cache_key(message, age, name)
        key2 = AIServiceUtils.generate_cache_key(message, age, name)
        
        assert key1 == key2
        assert len(key1) == 16  # Truncated SHA256
        assert isinstance(key1, str)
    
    def test_generate_cache_key_uniqueness(self):
        """Test that different inputs generate different cache keys."""
        # Different messages
        key1 = AIServiceUtils.generate_cache_key("Hello", 6, "Alice")
        key2 = AIServiceUtils.generate_cache_key("Goodbye", 6, "Alice")
        assert key1 != key2
        
        # Different ages
        key3 = AIServiceUtils.generate_cache_key("Hello", 6, "Alice")
        key4 = AIServiceUtils.generate_cache_key("Hello", 8, "Alice")
        assert key3 != key4
        
        # Different names
        key5 = AIServiceUtils.generate_cache_key("Hello", 6, "Alice")
        key6 = AIServiceUtils.generate_cache_key("Hello", 6, "Bob")
        assert key5 != key6
    
    def test_generate_cache_key_format(self):
        """Test cache key generation format and algorithm."""
        message = "Test message"
        age = 7
        name = "TestChild"
        
        # Generate expected key manually
        key_data = f"{message}:{age}:{name}"
        expected_key = hashlib.sha256(key_data.encode()).hexdigest()[:16]
        
        result = AIServiceUtils.generate_cache_key(message, age, name)
        assert result == expected_key
    
    def test_get_fallback_response_basic(self):
        """Test basic fallback response generation."""
        child_name = "Alice"
        child_age = 6
        
        response = AIServiceUtils.get_fallback_response(child_name, child_age)
        
        assert isinstance(response, AIResponse)
        assert child_name in response.content
        assert response.safety_score == 1.0
        assert response.age_appropriate is True
        assert response.sentiment == "positive"
        assert len(response.topics) > 0
        assert response.processing_time < 0.01
        assert response.cached is False
        assert "fallback_response" in response.moderation_flags
    
    def test_get_fallback_response_different_names(self):
        """Test fallback response with different child names."""
        names = ["Alice", "Bob", "Charlie", "Diana", "Eduardo"]
        
        for name in names:
            response = AIServiceUtils.get_fallback_response(name, 7)
            assert name in response.content
            assert response.safety_score == 1.0
    
    def test_get_fallback_response_different_ages(self):
        """Test fallback response with different ages."""
        ages = [3, 5, 7, 9, 11, 13]
        
        for age in ages:
            response = AIServiceUtils.get_fallback_response("TestChild", age)
            assert response.safety_score == 1.0
            assert response.age_appropriate is True
            assert "TestChild" in response.content
    
    def test_get_fallback_response_randomness(self):
        """Test that fallback responses have some variety."""
        responses = []
        for _ in range(10):
            response = AIServiceUtils.get_fallback_response("Alice", 6)
            responses.append(response.content)
        
        # Should have some variety in responses
        unique_responses = set(responses)
        assert len(unique_responses) > 1  # At least some variety
    
    def test_calculate_safety_score_safe_content(self):
        """Test safety score calculation for safe content."""
        content = "Hello! Let's play a fun learning game together!"
        moderation_result = {"safe": True, "categories": [], "scores": {}}
        banned_topics = ["violence", "inappropriate"]
        
        score = AIServiceUtils.calculate_safety_score(content, moderation_result, banned_topics)
        
        assert score > 0.9  # Should be high for safe content with positive words
        assert score <= 1.0
    
    def test_calculate_safety_score_unsafe_moderation(self):
        """Test safety score calculation when moderation flags content as unsafe."""
        content = "Safe content text"
        moderation_result = {"safe": False, "categories": ["hate"], "scores": {}}
        banned_topics = []
        
        score = AIServiceUtils.calculate_safety_score(content, moderation_result, banned_topics)
        
        assert score == 0.0  # Should be 0 when moderation fails
    
    def test_calculate_safety_score_banned_topics(self):
        """Test safety score calculation with banned topics."""
        content = "This contains violence and inappropriate content"
        moderation_result = {"safe": True, "categories": [], "scores": {}}
        banned_topics = ["violence", "inappropriate"]
        
        score = AIServiceUtils.calculate_safety_score(content, moderation_result, banned_topics)
        
        assert score < 0.9  # Should be reduced due to banned topics
        assert score >= 0.0
    
    def test_calculate_safety_score_positive_content(self):
        """Test safety score calculation with positive content indicators."""
        content = "Let's have fun and learn together! This is a happy adventure game!"
        moderation_result = {"safe": True, "categories": [], "scores": {}}
        banned_topics = []
        
        score = AIServiceUtils.calculate_safety_score(content, moderation_result, banned_topics)
        
        assert score > 0.9  # Should be high due to positive words
        assert score <= 1.0
    
    def test_calculate_safety_score_edge_cases(self):
        """Test safety score calculation edge cases."""
        banned_topics = ["violence", "inappropriate"]
        
        # Empty content
        score = AIServiceUtils.calculate_safety_score("", {"safe": True}, banned_topics)
        assert 0.0 <= score <= 1.0
        
        # Content with many banned topics
        content = "violence violence inappropriate inappropriate"
        score = AIServiceUtils.calculate_safety_score(content, {"safe": True}, banned_topics)
        assert score == 0.0  # Should hit minimum
        
        # Content with many positive words
        content = "fun fun fun learn learn learn play play play happy happy happy"
        score = AIServiceUtils.calculate_safety_score(content, {"safe": True}, banned_topics)
        assert score == 1.0  # Should hit maximum
    
    def test_check_age_appropriateness_toddlers(self):
        """Test age appropriateness check for toddlers (under 5)."""
        inappropriate_content = [
            "This is scary monster content",
            "Dark and frightening story",
            "You are all alone in the dark"
        ]
        
        appropriate_content = [
            "Let's play with colorful toys!",
            "Look at the pretty flowers",
            "Time for a happy song"
        ]
        
        for content in inappropriate_content:
            assert AIServiceUtils.check_age_appropriateness(content, 3) is False
            assert AIServiceUtils.check_age_appropriateness(content, 4) is False
        
        for content in appropriate_content:
            assert AIServiceUtils.check_age_appropriateness(content, 3) is True
            assert AIServiceUtils.check_age_appropriateness(content, 4) is True
    
    def test_check_age_appropriateness_preschool(self):
        """Test age appropriateness check for preschool (5-7)."""
        inappropriate_content = [
            "Let's solve complex math equations",
            "Here are some advanced concepts"
        ]
        
        appropriate_content = [
            "Let's count to ten!",
            "What color is this apple?",
            "Simple addition: 1 + 1 = 2"
        ]
        
        for content in inappropriate_content:
            assert AIServiceUtils.check_age_appropriateness(content, 6) is False
            assert AIServiceUtils.check_age_appropriateness(content, 7) is False
        
        for content in appropriate_content:
            assert AIServiceUtils.check_age_appropriateness(content, 6) is True
            assert AIServiceUtils.check_age_appropriateness(content, 7) is True
    
    def test_check_age_appropriateness_school_age(self):
        """Test age appropriateness check for school age (8+)."""
        content = "Let's learn about complex math and advanced concepts"
        
        # Should be appropriate for older children
        assert AIServiceUtils.check_age_appropriateness(content, 8) is True
        assert AIServiceUtils.check_age_appropriateness(content, 10) is True
        assert AIServiceUtils.check_age_appropriateness(content, 12) is True
    
    def test_analyze_sentiment_positive(self):
        """Test sentiment analysis for positive content."""
        positive_content = [
            "This is a happy and wonderful day!",
            "I feel great and awesome today!",
            "What an amazing and fun experience!",
            "Life is wonderful and full of joy!"
        ]
        
        for content in positive_content:
            sentiment = AIServiceUtils.analyze_sentiment(content)
            assert sentiment == "positive"
    
    def test_analyze_sentiment_negative(self):
        """Test sentiment analysis for negative content."""
        negative_content = [
            "This is a sad and terrible situation",
            "I feel bad and awful about this",
            "This is scary and worried content",
            "Everything is terrible and bad"
        ]
        
        for content in negative_content:
            sentiment = AIServiceUtils.analyze_sentiment(content)
            assert sentiment == "negative"
    
    def test_analyze_sentiment_neutral(self):
        """Test sentiment analysis for neutral content."""
        neutral_content = [
            "This is a regular day at school",
            "The weather report says it will rain",
            "Please complete your homework assignment",
            "The meeting is scheduled for tomorrow"
        ]
        
        for content in neutral_content:
            sentiment = AIServiceUtils.analyze_sentiment(content)
            assert sentiment == "neutral"
    
    def test_analyze_sentiment_mixed(self):
        """Test sentiment analysis for mixed content."""
        # Equal positive and negative words should be neutral
        mixed_content = "I feel happy but also sad about this situation"
        sentiment = AIServiceUtils.analyze_sentiment(mixed_content)
        assert sentiment == "neutral"
    
    def test_analyze_sentiment_case_insensitive(self):
        """Test that sentiment analysis is case insensitive."""
        content_variations = [
            "HAPPY and WONDERFUL",
            "Happy And Wonderful",
            "happy and wonderful",
            "HaPpY aNd WoNdErFuL"
        ]
        
        for content in content_variations:
            sentiment = AIServiceUtils.analyze_sentiment(content)
            assert sentiment == "positive"
    
    def test_analyze_sentiment_empty_content(self):
        """Test sentiment analysis with empty content."""
        sentiment = AIServiceUtils.analyze_sentiment("")
        assert sentiment == "neutral"
        
        sentiment = AIServiceUtils.analyze_sentiment("   ")
        assert sentiment == "neutral"
    
    def test_utility_functions_integration(self):
        """Test integration between utility functions."""
        # Test a complete workflow
        content = "I love to play fun games and learn about happy animals!"
        age = 8
        name = "TestChild"
        
        # Extract topics
        topics = AIServiceUtils.extract_topics(content)
        assert "play" in topics
        assert "emotions" in topics
        assert "nature" in topics
        
        # Clean content
        cleaned = AIServiceUtils.clean_content(content)
        assert cleaned == content  # Already clean
        
        # Get age group
        age_group = AIServiceUtils.get_age_group(age)
        assert age_group == "early_elementary"
        
        # Check age appropriateness
        appropriate = AIServiceUtils.check_age_appropriateness(content, age)
        assert appropriate is True
        
        # Analyze sentiment
        sentiment = AIServiceUtils.analyze_sentiment(content)
        assert sentiment == "positive"
        
        # Calculate safety score
        moderation_result = {"safe": True, "categories": [], "scores": {}}
        safety_score = AIServiceUtils.calculate_safety_score(content, moderation_result, [])
        assert safety_score > 0.9
        
        # Generate cache key
        cache_key = AIServiceUtils.generate_cache_key(content, age, name)
        assert len(cache_key) == 16
    
    def test_performance_characteristics(self):
        """Test performance characteristics of utility functions."""
        import time
        
        # Test with reasonably large content
        large_content = "fun learning happy play " * 100  # 400 words
        
        # All functions should complete quickly
        start_time = time.time()
        
        AIServiceUtils.extract_topics(large_content)
        AIServiceUtils.clean_content(large_content)
        AIServiceUtils.check_age_appropriateness(large_content, 8)
        AIServiceUtils.analyze_sentiment(large_content)
        AIServiceUtils.calculate_safety_score(large_content, {"safe": True}, ["violence"])
        AIServiceUtils.generate_cache_key(large_content, 8, "TestChild")
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete in reasonable time
        assert processing_time < 1.0  # Less than 1 second for all operations