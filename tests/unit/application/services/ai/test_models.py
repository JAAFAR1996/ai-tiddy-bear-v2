"""
Tests for AI Models
Testing AI service response models and data structures.
"""

import pytest
from pydantic import ValidationError

from src.application.services.ai.models import AIResponse


class TestAIResponse:
    """Test the AIResponse model."""
    
    def test_ai_response_creation_minimal(self):
        """Test AIResponse creation with minimal required fields."""
        response = AIResponse(
            content="Hello, I'm a friendly teddy bear!",
            safety_score=0.95,
            age_appropriate=True,
            sentiment="positive",
            processing_time=0.5
        )
        
        assert response.content == "Hello, I'm a friendly teddy bear!"
        assert response.safety_score == 0.95
        assert response.age_appropriate is True
        assert response.sentiment == "positive"
        assert response.processing_time == 0.5
        assert response.topics == []  # Default empty list
        assert response.cached is False  # Default value
        assert response.moderation_flags == []  # Default empty list
    
    def test_ai_response_creation_complete(self):
        """Test AIResponse creation with all fields."""
        response = AIResponse(
            content="Let's learn about animals together!",
            safety_score=0.98,
            age_appropriate=True,
            sentiment="educational",
            topics=["animals", "learning", "education"],
            processing_time=1.2,
            cached=True,
            moderation_flags=["reviewed", "approved"]
        )
        
        assert response.content == "Let's learn about animals together!"
        assert response.safety_score == 0.98
        assert response.age_appropriate is True
        assert response.sentiment == "educational"
        assert response.topics == ["animals", "learning", "education"]
        assert response.processing_time == 1.2
        assert response.cached is True
        assert response.moderation_flags == ["reviewed", "approved"]
    
    def test_safety_score_validation_valid_range(self):
        """Test safety score validation with valid values."""
        valid_scores = [0.0, 0.5, 0.75, 0.9, 1.0]
        
        for score in valid_scores:
            response = AIResponse(
                content="Test content",
                safety_score=score,
                age_appropriate=True,
                sentiment="neutral",
                processing_time=0.1
            )
            assert response.safety_score == score
    
    def test_safety_score_validation_invalid_range(self):
        """Test safety score validation with invalid values."""
        invalid_scores = [-0.1, -1.0, 1.1, 2.0, 10.0]
        
        for score in invalid_scores:
            with pytest.raises(ValidationError):
                AIResponse(
                    content="Test content",
                    safety_score=score,
                    age_appropriate=True,
                    sentiment="neutral",
                    processing_time=0.1
                )
    
    def test_content_field_validation(self):
        """Test content field validation."""
        # Valid content
        response = AIResponse(
            content="Valid content string",
            safety_score=0.9,
            age_appropriate=True,
            sentiment="positive",
            processing_time=0.3
        )
        assert response.content == "Valid content string"
        
        # Empty string should be valid
        response = AIResponse(
            content="",
            safety_score=0.9,
            age_appropriate=True,
            sentiment="neutral",
            processing_time=0.1
        )
        assert response.content == ""
    
    def test_age_appropriate_field(self):
        """Test age_appropriate field validation."""
        # Test True
        response = AIResponse(
            content="Age appropriate content",
            safety_score=0.9,
            age_appropriate=True,
            sentiment="positive",
            processing_time=0.2
        )
        assert response.age_appropriate is True
        
        # Test False
        response = AIResponse(
            content="Not age appropriate",
            safety_score=0.3,
            age_appropriate=False,
            sentiment="neutral",
            processing_time=0.2
        )
        assert response.age_appropriate is False
    
    def test_sentiment_field_validation(self):
        """Test sentiment field validation."""
        sentiments = ["positive", "negative", "neutral", "educational", "playful", "caring"]
        
        for sentiment in sentiments:
            response = AIResponse(
                content="Test content",
                safety_score=0.8,
                age_appropriate=True,
                sentiment=sentiment,
                processing_time=0.1
            )
            assert response.sentiment == sentiment
    
    def test_topics_field_validation(self):
        """Test topics field validation."""
        # Test empty list (default)
        response = AIResponse(
            content="Test content",
            safety_score=0.8,
            age_appropriate=True,
            sentiment="neutral",
            processing_time=0.1
        )
        assert response.topics == []
        
        # Test single topic
        response = AIResponse(
            content="Educational content",
            safety_score=0.9,
            age_appropriate=True,
            sentiment="educational",
            topics=["learning"],
            processing_time=0.2
        )
        assert response.topics == ["learning"]
        
        # Test multiple topics
        response = AIResponse(
            content="Fun learning game",
            safety_score=0.95,
            age_appropriate=True,
            sentiment="playful",
            topics=["games", "learning", "fun", "interactive"],
            processing_time=0.3
        )
        assert response.topics == ["games", "learning", "fun", "interactive"]
    
    def test_processing_time_validation(self):
        """Test processing_time field validation."""
        processing_times = [0.0, 0.1, 0.5, 1.0, 2.5, 10.0]
        
        for time_val in processing_times:
            response = AIResponse(
                content="Test content",
                safety_score=0.8,
                age_appropriate=True,
                sentiment="neutral",
                processing_time=time_val
            )
            assert response.processing_time == time_val
    
    def test_cached_field_validation(self):
        """Test cached field validation."""
        # Test default False
        response = AIResponse(
            content="Fresh response",
            safety_score=0.9,
            age_appropriate=True,
            sentiment="positive",
            processing_time=1.0
        )
        assert response.cached is False
        
        # Test explicitly True
        response = AIResponse(
            content="Cached response",
            safety_score=0.9,
            age_appropriate=True,
            sentiment="positive",
            processing_time=0.001,
            cached=True
        )
        assert response.cached is True
    
    def test_moderation_flags_validation(self):
        """Test moderation_flags field validation."""
        # Test default empty list
        response = AIResponse(
            content="Clean content",
            safety_score=1.0,
            age_appropriate=True,
            sentiment="positive",
            processing_time=0.2
        )
        assert response.moderation_flags == []
        
        # Test single flag
        response = AIResponse(
            content="Reviewed content",
            safety_score=0.95,
            age_appropriate=True,
            sentiment="neutral",
            processing_time=0.3,
            moderation_flags=["human_reviewed"]
        )
        assert response.moderation_flags == ["human_reviewed"]
        
        # Test multiple flags
        response = AIResponse(
            content="Flagged content",
            safety_score=0.7,
            age_appropriate=True,
            sentiment="neutral",
            processing_time=0.4,
            moderation_flags=["low_safety_score", "manual_review", "approved"]
        )
        assert response.moderation_flags == ["low_safety_score", "manual_review", "approved"]
    
    def test_model_serialization(self):
        """Test model serialization to dict and JSON."""
        response = AIResponse(
            content="Serialization test",
            safety_score=0.88,
            age_appropriate=True,
            sentiment="test",
            topics=["serialization", "testing"],
            processing_time=0.25,
            cached=False,
            moderation_flags=["test_flag"]
        )
        
        # Test dict conversion
        response_dict = response.model_dump()
        assert isinstance(response_dict, dict)
        assert response_dict["content"] == "Serialization test"
        assert response_dict["safety_score"] == 0.88
        assert response_dict["age_appropriate"] is True
        assert response_dict["sentiment"] == "test"
        assert response_dict["topics"] == ["serialization", "testing"]
        assert response_dict["processing_time"] == 0.25
        assert response_dict["cached"] is False
        assert response_dict["moderation_flags"] == ["test_flag"]
        
        # Test JSON conversion
        response_json = response.model_dump_json()
        assert isinstance(response_json, str)
        assert "Serialization test" in response_json
        assert "0.88" in response_json
    
    def test_model_deserialization(self):
        """Test model deserialization from dict and JSON."""
        # Test from dict
        data = {
            "content": "Deserialization test",
            "safety_score": 0.92,
            "age_appropriate": True,
            "sentiment": "positive",
            "topics": ["deserialization"],
            "processing_time": 0.15,
            "cached": True,
            "moderation_flags": ["validated"]
        }
        
        response = AIResponse.model_validate(data)
        assert response.content == "Deserialization test"
        assert response.safety_score == 0.92
        assert response.age_appropriate is True
        assert response.sentiment == "positive"
        assert response.topics == ["deserialization"]
        assert response.processing_time == 0.15
        assert response.cached is True
        assert response.moderation_flags == ["validated"]
        
        # Test from JSON
        json_data = '{"content": "JSON test", "safety_score": 0.85, "age_appropriate": true, "sentiment": "neutral", "processing_time": 0.3}'
        response = AIResponse.model_validate_json(json_data)
        assert response.content == "JSON test"
        assert response.safety_score == 0.85
        assert response.topics == []  # Default value
        assert response.cached is False  # Default value
    
    def test_model_validation_errors(self):
        """Test model validation with invalid data."""
        # Missing required fields
        with pytest.raises(ValidationError):
            AIResponse()
        
        with pytest.raises(ValidationError):
            AIResponse(content="Test")
        
        # Invalid safety_score type
        with pytest.raises(ValidationError):
            AIResponse(
                content="Test",
                safety_score="invalid",
                age_appropriate=True,
                sentiment="neutral",
                processing_time=0.1
            )
        
        # Invalid age_appropriate type
        with pytest.raises(ValidationError):
            AIResponse(
                content="Test",
                safety_score=0.8,
                age_appropriate="invalid",
                sentiment="neutral",
                processing_time=0.1
            )
        
        # Invalid processing_time type
        with pytest.raises(ValidationError):
            AIResponse(
                content="Test",
                safety_score=0.8,
                age_appropriate=True,
                sentiment="neutral",
                processing_time="invalid"
            )
    
    def test_model_immutability_after_creation(self):
        """Test model behavior after creation."""
        response = AIResponse(
            content="Test content",
            safety_score=0.9,
            age_appropriate=True,
            sentiment="positive",
            processing_time=0.2
        )
        
        # Should be able to access fields
        assert response.content == "Test content"
        assert response.safety_score == 0.9
        
        # Should be able to modify fields (Pydantic models are mutable by default)
        response.content = "Modified content"
        assert response.content == "Modified content"
    
    def test_model_equality(self):
        """Test model equality comparison."""
        response1 = AIResponse(
            content="Same content",
            safety_score=0.9,
            age_appropriate=True,
            sentiment="positive",
            processing_time=0.2
        )
        
        response2 = AIResponse(
            content="Same content",
            safety_score=0.9,
            age_appropriate=True,
            sentiment="positive",
            processing_time=0.2
        )
        
        response3 = AIResponse(
            content="Different content",
            safety_score=0.9,
            age_appropriate=True,
            sentiment="positive",
            processing_time=0.2
        )
        
        assert response1 == response2
        assert response1 != response3
    
    def test_model_realistic_scenarios(self):
        """Test model with realistic AI response scenarios."""
        # Educational response
        educational_response = AIResponse(
            content="Did you know that elephants are the largest land animals? They use their trunks like we use our hands!",
            safety_score=0.98,
            age_appropriate=True,
            sentiment="educational",
            topics=["animals", "facts", "learning"],
            processing_time=0.45,
            cached=False,
            moderation_flags=[]
        )
        assert educational_response.safety_score > 0.9
        assert "animals" in educational_response.topics
        
        # Story response
        story_response = AIResponse(
            content="Once upon a time, there was a little rabbit who loved to hop through the meadow...",
            safety_score=0.96,
            age_appropriate=True,
            sentiment="positive",
            topics=["story", "animals", "adventure"],
            processing_time=0.78,
            cached=False,
            moderation_flags=[]
        )
        assert story_response.sentiment == "positive"
        assert "story" in story_response.topics
        
        # Low safety score response
        flagged_response = AIResponse(
            content="This content needed review due to potential safety concerns.",
            safety_score=0.65,
            age_appropriate=True,
            sentiment="neutral",
            topics=["safety"],
            processing_time=0.32,
            cached=False,
            moderation_flags=["low_safety_score", "manual_review"]
        )
        assert flagged_response.safety_score < 0.8
        assert "manual_review" in flagged_response.moderation_flags
    
    def test_model_field_constraints(self):
        """Test model field constraints and edge cases."""
        # Test exact boundary values for safety_score
        boundary_response = AIResponse(
            content="Boundary test",
            safety_score=0.0,  # Minimum allowed
            age_appropriate=True,
            sentiment="neutral",
            processing_time=0.0
        )
        assert boundary_response.safety_score == 0.0
        
        boundary_response = AIResponse(
            content="Boundary test",
            safety_score=1.0,  # Maximum allowed
            age_appropriate=True,
            sentiment="neutral",
            processing_time=0.0
        )
        assert boundary_response.safety_score == 1.0
        
        # Test very long content
        long_content = "A" * 10000  # Very long content
        long_response = AIResponse(
            content=long_content,
            safety_score=0.8,
            age_appropriate=True,
            sentiment="neutral",
            processing_time=2.5
        )
        assert len(long_response.content) == 10000
        
        # Test very long topics list
        many_topics = [f"topic_{i}" for i in range(100)]
        topic_response = AIResponse(
            content="Many topics test",
            safety_score=0.8,
            age_appropriate=True,
            sentiment="neutral",
            topics=many_topics,
            processing_time=0.1
        )
        assert len(topic_response.topics) == 100