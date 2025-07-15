"""
Tests for AI Main Service
Testing production-grade AI service with OpenAI integration and child safety.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

from src.application.services.ai.main_service import AITeddyBearService
from src.application.services.ai.models import AIResponse


class TestAITeddyBearService:
    """Test the AI Teddy Bear Service."""
    
    @pytest.fixture
    def mock_openai_client(self):
        """Create a mock OpenAI client."""
        client = Mock()
        client.chat = Mock()
        client.chat.completions = Mock()
        client.chat.completions.create = AsyncMock()
        client.moderations = Mock()
        client.moderations.create = AsyncMock()
        return client
    
    @pytest.fixture
    def mock_redis_cache(self):
        """Create a mock Redis cache."""
        cache = Mock()
        cache.get = AsyncMock()
        cache.setex = AsyncMock()
        return cache
    
    @pytest.fixture
    def service(self, mock_redis_cache):
        """Create an AI service instance."""
        with patch('src.application.services.ai.main_service.AsyncOpenAI') as mock_openai:
            mock_openai.return_value = Mock()
            service = AITeddyBearService(
                openai_api_key="test_api_key",
                redis_cache=mock_redis_cache
            )
            return service
    
    @pytest.fixture
    def service_no_cache(self):
        """Create an AI service instance without cache."""
        with patch('src.application.services.ai.main_service.AsyncOpenAI') as mock_openai:
            mock_openai.return_value = Mock()
            return AITeddyBearService(openai_api_key="test_api_key")
    
    def test_initialization_with_api_key(self, mock_redis_cache):
        """Test service initialization with API key."""
        with patch('src.application.services.ai.main_service.AsyncOpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            service = AITeddyBearService(
                openai_api_key="test_key",
                redis_cache=mock_redis_cache
            )
            
            assert service.redis_cache == mock_redis_cache
            assert service.model == "gpt-4-turbo-preview"
            assert service.max_tokens == 200
            assert service.temperature == 0.7
            assert service.safety_threshold == 0.9
            assert len(service.banned_topics) > 0
            mock_openai.assert_called_once_with(api_key="test_key")
    
    def test_initialization_without_api_key(self):
        """Test service initialization without API key."""
        with pytest.raises(ValueError, match="OpenAI API key is required"):
            AITeddyBearService(openai_api_key="")
    
    def test_initialization_banned_topics(self, service):
        """Test that banned topics are properly configured."""
        expected_topics = [
            "violence", "adult content", "drugs", "alcohol", "weapons",
            "inappropriate language", "scary content", "personal information"
        ]
        
        for topic in expected_topics:
            assert topic in service.banned_topics
    
    @pytest.mark.asyncio
    async def test_generate_response_basic_success(self, service):
        """Test basic successful response generation."""
        # Mock moderation response
        mock_moderation = Mock()
        mock_moderation.results = [Mock()]
        mock_moderation.results[0].flagged = False
        mock_moderation.results[0].categories = Mock()
        mock_moderation.results[0].categories.model_dump.return_value = {}
        mock_moderation.results[0].category_scores = Mock()
        mock_moderation.results[0].category_scores.model_dump.return_value = {}
        
        service.client.moderations.create.return_value = mock_moderation
        
        # Mock chat completion response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Hello! I'm a friendly teddy bear."
        
        service.client.chat.completions.create.return_value = mock_response
        
        # Mock utility methods
        with patch.object(service, '_post_process_response') as mock_post_process:
            mock_ai_response = AIResponse(
                content="Hello! I'm a friendly teddy bear.",
                safety_score=0.95,
                age_appropriate=True,
                sentiment="positive",
                topics=["friendship"],
                processing_time=0.5
            )
            mock_post_process.return_value = mock_ai_response
            
            result = await service.generate_response(
                message="Hello teddy bear",
                child_age=6,
                child_name="Alice"
            )
            
            assert isinstance(result, AIResponse)
            assert result.content == "Hello! I'm a friendly teddy bear."
            assert result.safety_score == 0.95
            assert result.age_appropriate is True
            assert result.processing_time > 0
    
    @pytest.mark.asyncio
    async def test_generate_response_coppa_validation(self, service):
        """Test COPPA compliance validation."""
        with pytest.raises(ValueError, match="Service only available for children 13 and under"):
            await service.generate_response(
                message="Hello",
                child_age=14,
                child_name="Alice"
            )
    
    @pytest.mark.asyncio
    async def test_generate_response_empty_message(self, service):
        """Test validation of empty messages."""
        with pytest.raises(ValueError, match="Message cannot be empty"):
            await service.generate_response(
                message="",
                child_age=6,
                child_name="Alice"
            )
        
        with pytest.raises(ValueError, match="Message cannot be empty"):
            await service.generate_response(
                message="   ",
                child_age=6,
                child_name="Alice"
            )
    
    @pytest.mark.asyncio
    async def test_generate_response_with_context(self, service):
        """Test response generation with conversation context."""
        # Setup mocks
        service.client.moderations.create.return_value = Mock()
        service.client.moderations.create.return_value.results = [Mock()]
        service.client.moderations.create.return_value.results[0].flagged = False
        service.client.moderations.create.return_value.results[0].categories = Mock()
        service.client.moderations.create.return_value.results[0].categories.model_dump.return_value = {}
        service.client.moderations.create.return_value.results[0].category_scores = Mock()
        service.client.moderations.create.return_value.results[0].category_scores.model_dump.return_value = {}
        
        service.client.chat.completions.create.return_value = Mock()
        service.client.chat.completions.create.return_value.choices = [Mock()]
        service.client.chat.completions.create.return_value.choices[0].message = Mock()
        service.client.chat.completions.create.return_value.choices[0].message.content = "That's a great question!"
        
        context = [
            {"role": "user", "content": "What's your favorite color?"},
            {"role": "assistant", "content": "I love all colors!"}
        ]
        
        with patch.object(service, '_post_process_response') as mock_post_process:
            mock_ai_response = AIResponse(
                content="That's a great question!",
                safety_score=0.95,
                age_appropriate=True,
                sentiment="positive",
                topics=["conversation"],
                processing_time=0.3
            )
            mock_post_process.return_value = mock_ai_response
            
            result = await service.generate_response(
                message="What about blue?",
                child_age=8,
                child_name="Bob",
                context=context
            )
            
            assert isinstance(result, AIResponse)
            # Verify context was used in API call
            call_args = service.client.chat.completions.create.call_args
            messages = call_args[1]["messages"]
            assert len(messages) >= 3  # system + context + user message
    
    @pytest.mark.asyncio
    async def test_generate_response_with_parent_guidelines(self, service):
        """Test response generation with parent guidelines."""
        service.client.moderations.create.return_value = Mock()
        service.client.moderations.create.return_value.results = [Mock()]
        service.client.moderations.create.return_value.results[0].flagged = False
        service.client.moderations.create.return_value.results[0].categories = Mock()
        service.client.moderations.create.return_value.results[0].categories.model_dump.return_value = {}
        service.client.moderations.create.return_value.results[0].category_scores = Mock()
        service.client.moderations.create.return_value.results[0].category_scores.model_dump.return_value = {}
        
        service.client.chat.completions.create.return_value = Mock()
        service.client.chat.completions.create.return_value.choices = [Mock()]
        service.client.chat.completions.create.return_value.choices[0].message = Mock()
        service.client.chat.completions.create.return_value.choices[0].message.content = "Let's focus on learning!"
        
        parent_guidelines = "Please focus on educational content and avoid any mention of toys"
        
        with patch.object(service, '_post_process_response') as mock_post_process:
            mock_ai_response = AIResponse(
                content="Let's focus on learning!",
                safety_score=0.98,
                age_appropriate=True,
                sentiment="positive",
                topics=["education"],
                processing_time=0.4
            )
            mock_post_process.return_value = mock_ai_response
            
            result = await service.generate_response(
                message="What should we do?",
                child_age=7,
                child_name="Charlie",
                parent_guidelines=parent_guidelines
            )
            
            assert isinstance(result, AIResponse)
            # Verify system prompt includes parent guidelines
            call_args = service.client.chat.completions.create.call_args
            system_message = call_args[1]["messages"][0]["content"]
            assert "PARENT GUIDELINES" in system_message
            assert parent_guidelines in system_message
    
    @pytest.mark.asyncio
    async def test_moderate_content_safe(self, service):
        """Test content moderation with safe content."""
        mock_moderation = Mock()
        mock_moderation.results = [Mock()]
        mock_moderation.results[0].flagged = False
        mock_moderation.results[0].categories = Mock()
        mock_moderation.results[0].categories.model_dump.return_value = {"hate": False, "violence": False}
        mock_moderation.results[0].category_scores = Mock()
        mock_moderation.results[0].category_scores.model_dump.return_value = {"hate": 0.1, "violence": 0.05}
        
        service.client.moderations.create.return_value = mock_moderation
        
        result = await service._moderate_content("Hello, how are you?")
        
        assert result["safe"] is True
        assert result["categories"] == []
        assert "hate" in result["scores"]
        assert "violence" in result["scores"]
    
    @pytest.mark.asyncio
    async def test_moderate_content_unsafe(self, service):
        """Test content moderation with unsafe content."""
        mock_moderation = Mock()
        mock_moderation.results = [Mock()]
        mock_moderation.results[0].flagged = True
        mock_moderation.results[0].categories = Mock()
        mock_moderation.results[0].categories.model_dump.return_value = {"hate": True, "violence": False}
        mock_moderation.results[0].category_scores = Mock()
        mock_moderation.results[0].category_scores.model_dump.return_value = {"hate": 0.9, "violence": 0.1}
        
        service.client.moderations.create.return_value = mock_moderation
        
        result = await service._moderate_content("Inappropriate content here")
        
        assert result["safe"] is False
        assert "hate" in result["categories"]
        assert "violence" not in result["categories"]
    
    @pytest.mark.asyncio
    async def test_moderate_content_api_error(self, service):
        """Test content moderation with API error."""
        service.client.moderations.create.side_effect = Exception("API error")
        
        result = await service._moderate_content("Test content")
        
        assert result["safe"] is False
        assert "moderation_error" in result["categories"]
    
    def test_create_system_prompt_different_ages(self, service):
        """Test system prompt creation for different age groups."""
        test_cases = [
            (3, "toddler"),
            (5, "preschool"),
            (8, "early_elementary"),
            (10, "elementary"),
            (12, "middle_school")
        ]
        
        for age, expected_group in test_cases:
            prompt = service._create_system_prompt(age, "TestChild")
            
            assert "TestChild" in prompt
            assert str(age) in prompt
            assert "CRITICAL SAFETY RULES" in prompt
            assert "age-appropriate" in prompt
            assert expected_group in prompt.lower() or "children" in prompt
    
    def test_create_system_prompt_with_guidelines(self, service):
        """Test system prompt creation with parent guidelines."""
        guidelines = "Focus on science topics only"
        prompt = service._create_system_prompt(8, "TestChild", guidelines)
        
        assert "PARENT GUIDELINES" in prompt
        assert guidelines in prompt
    
    @pytest.mark.asyncio
    async def test_post_process_response(self, service):
        """Test response post-processing."""
        content = "This is a safe and educational response for children."
        moderation_result = {"safe": True, "categories": [], "scores": {}}
        
        with patch.object(service, '_calculate_safety_score', return_value=0.95):
            with patch.object(service, '_check_age_appropriateness', return_value=True):
                with patch.object(service, '_analyze_sentiment', return_value="positive"):
                    with patch.object(service, '_extract_topics', return_value=["education"]):
                        with patch.object(service, '_clean_content', return_value=content):
                            result = await service._post_process_response(content, 8, moderation_result)
                            
                            assert isinstance(result, AIResponse)
                            assert result.content == content
                            assert result.safety_score == 0.95
                            assert result.age_appropriate is True
                            assert result.sentiment == "positive"
                            assert result.topics == ["education"]
                            assert len(result.moderation_flags) == 0
    
    @pytest.mark.asyncio
    async def test_post_process_response_unsafe(self, service):
        """Test response post-processing with unsafe content."""
        content = "Potentially unsafe content"
        moderation_result = {"safe": False, "categories": ["inappropriate"], "scores": {}}
        
        with patch.object(service, '_calculate_safety_score', return_value=0.3):
            with patch.object(service, '_check_age_appropriateness', return_value=False):
                with patch.object(service, '_analyze_sentiment', return_value="negative"):
                    with patch.object(service, '_extract_topics', return_value=["inappropriate"]):
                        with patch.object(service, '_clean_content', return_value=content):
                            result = await service._post_process_response(content, 6, moderation_result)
                            
                            assert result.safety_score == 0.3
                            assert result.age_appropriate is False
                            assert len(result.moderation_flags) == 2  # low_safety_score, age_inappropriate
                            assert "low_safety_score" in result.moderation_flags
                            assert "age_inappropriate" in result.moderation_flags
    
    @pytest.mark.asyncio
    async def test_caching_functionality(self, service, mock_redis_cache):
        """Test response caching functionality."""
        # Test cache key generation
        cache_key = service._generate_cache_key("Hello", 6, "Alice")
        assert isinstance(cache_key, str)
        assert len(cache_key) == 16  # SHA256 hash truncated to 16 chars
        
        # Test cache retrieval (cache miss)
        mock_redis_cache.get.return_value = None
        cached_response = await service._get_cached_response(cache_key)
        assert cached_response is None
        
        # Test cache storage
        ai_response = AIResponse(
            content="Cached response",
            safety_score=0.9,
            age_appropriate=True,
            sentiment="positive",
            topics=["test"],
            processing_time=0.1
        )
        
        await service._cache_response(cache_key, ai_response)
        mock_redis_cache.setex.assert_called_once()
        args = mock_redis_cache.setex.call_args
        assert args[0][0] == cache_key
        assert args[0][1] == 3600  # 1 hour TTL
    
    @pytest.mark.asyncio
    async def test_cache_error_handling(self, service, mock_redis_cache):
        """Test cache error handling."""
        cache_key = "test_key"
        
        # Test cache retrieval error
        mock_redis_cache.get.side_effect = Exception("Cache error")
        result = await service._get_cached_response(cache_key)
        assert result is None
        
        # Test cache storage error
        ai_response = AIResponse(
            content="Test",
            safety_score=0.9,
            age_appropriate=True,
            sentiment="positive",
            topics=["test"],
            processing_time=0.1
        )
        
        mock_redis_cache.setex.side_effect = Exception("Cache error")
        # Should not raise exception
        await service._cache_response(cache_key, ai_response)
    
    @pytest.mark.asyncio
    async def test_fallback_response(self, service):
        """Test fallback response generation."""
        result = await service._get_fallback_response("Alice", 6)
        
        assert isinstance(result, AIResponse)
        assert "Alice" in result.content
        assert result.safety_score == 1.0
        assert result.age_appropriate is True
        assert result.sentiment == "positive"
        assert len(result.topics) > 0
        assert result.processing_time < 0.01
        assert result.cached is False
        assert "fallback_response" in result.moderation_flags
    
    @pytest.mark.asyncio
    async def test_generate_response_with_api_error(self, service):
        """Test response generation when OpenAI API fails."""
        service.client.moderations.create.return_value = Mock()
        service.client.moderations.create.return_value.results = [Mock()]
        service.client.moderations.create.return_value.results[0].flagged = False
        service.client.moderations.create.return_value.results[0].categories = Mock()
        service.client.moderations.create.return_value.results[0].categories.model_dump.return_value = {}
        service.client.moderations.create.return_value.results[0].category_scores = Mock()
        service.client.moderations.create.return_value.results[0].category_scores.model_dump.return_value = {}
        
        # Make API call fail
        service.client.chat.completions.create.side_effect = Exception("API error")
        
        result = await service.generate_response(
            message="Hello",
            child_age=6,
            child_name="Alice"
        )
        
        # Should return fallback response
        assert isinstance(result, AIResponse)
        assert "Alice" in result.content
        assert result.safety_score == 1.0
        assert "fallback_response" in result.moderation_flags
    
    @pytest.mark.asyncio
    async def test_generate_response_moderation_failure(self, service):
        """Test response generation when moderation flags content."""
        mock_moderation = Mock()
        mock_moderation.results = [Mock()]
        mock_moderation.results[0].flagged = True
        mock_moderation.results[0].categories = Mock()
        mock_moderation.results[0].categories.model_dump.return_value = {"hate": True}
        mock_moderation.results[0].category_scores = Mock()
        mock_moderation.results[0].category_scores.model_dump.return_value = {}
        
        service.client.moderations.create.return_value = mock_moderation
        
        with pytest.raises(ValueError, match="Content flagged by moderation"):
            await service.generate_response(
                message="Inappropriate content",
                child_age=6,
                child_name="Alice"
            )
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, service):
        """Test handling of concurrent requests."""
        import asyncio
        
        # Setup mocks for successful responses
        service.client.moderations.create.return_value = Mock()
        service.client.moderations.create.return_value.results = [Mock()]
        service.client.moderations.create.return_value.results[0].flagged = False
        service.client.moderations.create.return_value.results[0].categories = Mock()
        service.client.moderations.create.return_value.results[0].categories.model_dump.return_value = {}
        service.client.moderations.create.return_value.results[0].category_scores = Mock()
        service.client.moderations.create.return_value.results[0].category_scores.model_dump.return_value = {}
        
        service.client.chat.completions.create.return_value = Mock()
        service.client.chat.completions.create.return_value.choices = [Mock()]
        service.client.chat.completions.create.return_value.choices[0].message = Mock()
        service.client.chat.completions.create.return_value.choices[0].message.content = "Safe response"
        
        with patch.object(service, '_post_process_response') as mock_post_process:
            mock_ai_response = AIResponse(
                content="Safe response",
                safety_score=0.95,
                age_appropriate=True,
                sentiment="positive",
                topics=["conversation"],
                processing_time=0.1
            )
            mock_post_process.return_value = mock_ai_response
            
            # Make concurrent requests
            tasks = [
                service.generate_response(f"Message {i}", 6, f"Child{i}")
                for i in range(3)
            ]
            
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 3
            assert all(isinstance(r, AIResponse) for r in results)
            assert all(r.content == "Safe response" for r in results)
    
    def test_utility_method_integration(self, service):
        """Test integration with utility methods."""
        # Test that utility methods are called correctly
        with patch('src.application.services.ai.main_service.AIServiceUtils') as mock_utils:
            mock_utils.calculate_safety_score.return_value = 0.9
            mock_utils.check_age_appropriateness.return_value = True
            mock_utils.analyze_sentiment.return_value = "positive"
            mock_utils.extract_topics.return_value = ["education"]
            mock_utils.clean_content.return_value = "Clean content"
            mock_utils.get_age_group.return_value = "elementary"
            mock_utils.generate_cache_key.return_value = "test_key"
            mock_utils.get_fallback_response.return_value = AIResponse(
                content="Fallback",
                safety_score=1.0,
                age_appropriate=True,
                sentiment="positive",
                topics=["test"],
                processing_time=0.1
            )
            
            # Test utility method calls
            service._calculate_safety_score("content", {})
            service._check_age_appropriateness("content", 8)
            service._analyze_sentiment("content")
            service._extract_topics("content")
            service._clean_content("content")
            service._get_age_group(8)
            service._generate_cache_key("msg", 8, "name")
            
            # Verify calls
            mock_utils.calculate_safety_score.assert_called_once()
            mock_utils.check_age_appropriateness.assert_called_once()
            mock_utils.analyze_sentiment.assert_called_once()
            mock_utils.extract_topics.assert_called_once()
            mock_utils.clean_content.assert_called_once()
            mock_utils.get_age_group.assert_called_once()
            mock_utils.generate_cache_key.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_service_without_cache(self, service_no_cache):
        """Test service functionality without Redis cache."""
        # Cache methods should handle None cache gracefully
        cache_key = "test_key"
        
        # Should return None for cache miss
        result = await service_no_cache._get_cached_response(cache_key)
        assert result is None
        
        # Should not raise error for cache storage
        ai_response = AIResponse(
            content="Test",
            safety_score=0.9,
            age_appropriate=True,
            sentiment="positive",
            topics=["test"],
            processing_time=0.1
        )
        
        await service_no_cache._cache_response(cache_key, ai_response)  # Should not raise
    
    def test_configuration_validation(self, service):
        """Test that service configuration is properly validated."""
        assert service.model in ["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"]
        assert 50 <= service.max_tokens <= 500
        assert 0.0 <= service.temperature <= 1.0
        assert 0.0 <= service.safety_threshold <= 1.0
        assert isinstance(service.banned_topics, list)
        assert len(service.banned_topics) > 0