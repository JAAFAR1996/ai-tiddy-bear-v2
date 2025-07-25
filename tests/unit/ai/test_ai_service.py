import sys
from pathlib import Path

from infrastructure.ai.real_ai_service import AIService

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

"""
اختبارات خدمة الذكاء الاصطناعي
"""

try:
    import pytest
except ImportError:
    # Mock pytest when not available
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
    """اختبارات خدمة الذكاء الاصطناعي"""

    def setup_method(self):
        """إعداد الاختبار"""
        self.ai_service = AIService()

    def test_safety_analysis_safe_content(self):
        """اختبار تحليل الأمان للمحتوى الآمن"""
        safe_text = "I love playing with my teddy bear"
        analysis = self.ai_service.analyze_safety(safe_text)

        assert analysis["safe"] is True
        assert analysis["severity"] == "none"
        assert len(analysis["issues"]) == 0

    def test_safety_analysis_unsafe_content(self):
        """اختبار تحليل الأمان للمحتوى غير الآمن"""
        unsafe_text = "I want to use a weapon to fight"
        analysis = self.ai_service.analyze_safety(unsafe_text)

        assert analysis["safe"] is False
        assert analysis["severity"] in ["low", "medium", "high"]
        assert len(analysis["issues"]) > 0

    def test_generate_story_response(self):
        """اختبار توليد استجابة قصة"""
        response = self.ai_service.generate_response(
            "Tell me a story",
            6,
            {"interests": ["animals"], "favorite_character": "bunny"},
        )

        assert response["response_type"] == "story"
        assert "bunny" in response["response"].lower()
        assert response["safety_analysis"]["safe"] is True

    def test_generate_greeting_response(self):
        """اختبار توليد استجابة تحية"""
        response = self.ai_service.generate_response("Hello", 6, {"language": "en"})

        assert response["response_type"] == "greeting"
        assert response["emotion"] == "friendly"
        assert len(response["response"]) > 0

    def test_age_appropriate_response(self):
        """اختبار الاستجابة المناسبة للعمر"""
        young_response = self.ai_service.generate_story(3, {"interests": ["animals"]})
        older_response = self.ai_service.generate_story(9, {"interests": ["animals"]})

        assert len(young_response) > 0
        assert len(older_response) > 0
        # قصص الأطفال الصغار أبسط
        assert "sunshine" in young_response or "friends" in young_response

    def test_content_filtering(self):
        """اختبار تصفية المحتوى"""
        inappropriate_text = "That's stupid and dumb"
        filtered = self.ai_service.filter_content(inappropriate_text)

        assert "stupid" not in filtered
        assert "dumb" not in filtered
        assert "silly" in filtered or "funny" in filtered

    def test_emotion_determination(self):
        """اختبار تحديد العاطفة"""
        happy_text = "I'm so happy and excited!"
        sad_text = "I feel sad and upset"

        happy_emotion = self.ai_service.determine_emotion(happy_text)
        sad_emotion = self.ai_service.determine_emotion(sad_text)

        assert happy_emotion == "happy"
        assert sad_emotion == "empathetic"
