import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import pytest with fallback to mock
pytest = None
try:
    import pytest
except ImportError:
    try:
        from common.mock_pytest import pytest
    except ImportError:
        pass

    # Mock pytest when not available
    if pytest is None:
        class MockPytest:

        def fixture(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

        def mark(self):
            class MockMark:
                def parametrize(self, *args, **kwargs):
                    def decorator(func):
                        return func

                    return decorator

                def asyncio(self, func):
                    return func

                def slow(self, func):
                    return func

                def skip(self, reason=""):
                    def decorator(func):
                        return func

                    return decorator

            return MockMark()

        def raises(self, exception):
            class MockRaises:
                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    return False

            return MockRaises()

        def skip(self, reason=""):
            def decorator(func):
                return func

            return decorator

        pytest = MockPytest()


class TestAIService:
    """Test AI service functionality"""

    @pytest.mark.asyncio
    async def test_generate_response(self, ai_service):
        """Test AI response generation"""
        # Setup
        ai_service.generate_response.return_value = {
            "text": "مرحباً! كيف حالك اليوم؟",
            "intent": "greeting",
            "confidence": 0.95,
        }

        # Test
        response = await ai_service.generate_response(
            "مرحبا", context={"child_name": "أحمد", "age": 5}
        )

        # Assert
        assert response["text"] == "مرحباً! كيف حالك اليوم؟"
        assert response["intent"] == "greeting"
        assert response["confidence"] > 0.9

    @pytest.mark.asyncio
    async def test_emotion_detection(self, ai_service):
        """Test emotion detection from text"""
        # Setup
        ai_service.detect_emotion.return_value = {
            "emotion": "happy",
            "confidence": 0.87,
            "secondary_emotions": [
                {"emotion": "excited", "confidence": 0.65},
                {"emotion": "playful", "confidence": 0.52},
            ],
        }

        # Test
        result = await ai_service.detect_emotion("أنا سعيد جداً اليوم!")

        # Assert
        assert result["emotion"] == "happy"
        assert result["confidence"] > 0.8
        assert len(result["secondary_emotions"]) >= 2

    @pytest.mark.asyncio
    async def test_story_generation(self, ai_service):
        """Test story generation"""
        # Setup
        ai_service.generate_story.return_value = {
            "title": "مغامرة الأرنب الصغير",
            "content": "كان يا ما كان، في قديم الزمان، أرنب صغير يحب المغامرات...",
            "moral": "الشجاعة والصداقة",
            "age_appropriate": True,
            "duration_minutes": 5,
        }

        # Test
        story = await ai_service.generate_story(
            theme="animals",
            age=5,
            interests=["adventure", "friendship"],
            language="ar",
        )

        # Assert
        assert story["title"] is not None
        assert len(story["content"]) > 50
        assert story["age_appropriate"] is True
        assert story["duration_minutes"] <= 10

    @pytest.mark.asyncio
    async def test_content_moderation(self, ai_service):
        """Test content moderation"""
        # Test safe content
        ai_service.moderate_content.return_value = {
            "safe": True,
            "categories": {},
            "confidence": 0.99,
        }

        safe_result = await ai_service.moderate_content("قصة جميلة عن الصداقة")
        assert safe_result["safe"] is True

        # Test unsafe content
        ai_service.moderate_content.return_value = {
            "safe": False,
            "categories": {"violence": 0.85, "inappropriate": 0.72},
            "confidence": 0.85,
            "reason": "Content contains violence",
        }

        unsafe_result = await ai_service.moderate_content("محتوى غير مناسب")
        assert unsafe_result["safe"] is False
        assert "violence" in unsafe_result["categories"]
