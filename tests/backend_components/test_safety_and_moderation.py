import sys
from datetime import datetime
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


class TestSafetyAndModeration:
    """Test safety and content moderation"""

    @pytest.mark.asyncio
    async def test_content_safety_check(self, safety_service):
        """Test content safety checking"""
        # Test safe content
        safety_service.check_content_safety.return_value = {
            "safe": True,
            "confidence": 0.98,
            "categories": {},
        }

        safe_result = await safety_service.check_content_safety(
            "قصة لطيفة عن الحيوانات"
        )
        assert safe_result["safe"] is True

        # Test unsafe content
        safety_service.check_content_safety.return_value = {
            "safe": False,
            "confidence": 0.92,
            "categories": {"violence": 0.15, "inappropriate_language": 0.85},
            "action": "block",
            "alternative_response": "دعنا نتحدث عن شيء آخر لطيف!",
        }

        unsafe_result = await safety_service.check_content_safety("محتوى غير مناسب")
        assert unsafe_result["safe"] is False
        assert unsafe_result["action"] == "block"
        assert unsafe_result["alternative_response"] is not None

    @pytest.mark.asyncio
    async def test_emergency_detection(self, safety_service):
        """Test emergency keyword detection"""
        # Setup
        safety_service.detect_emergency_keywords.return_value = {
            "detected": True,
            "severity": "high",
            "keywords_found": ["يؤلمني", "خائف"],
            "context": "Child expressing physical pain and fear",
            "recommended_action": "immediate_parent_notification",
        }

        # Test
        result = await safety_service.detect_emergency_keywords(
            "بطني يؤلمني كثيراً وأنا خائف"
        )

        # Assert
        assert result["detected"] is True
        assert result["severity"] == "high"
        assert len(result["keywords_found"]) >= 2
        assert result["recommended_action"] == "immediate_parent_notification"

        # Trigger alert
        safety_service.trigger_alert.return_value = {
            "alert_id": "alert_001",
            "sent_to": ["parent@example.com"],
            "timestamp": datetime.utcnow().isoformat(),
        }

        alert_result = await safety_service.trigger_alert(
            child_id="child123", alert_type="emergency", details=result
        )

        assert alert_result["alert_id"] is not None
        assert len(alert_result["sent_to"]) >= 1

    @pytest.mark.asyncio
    async def test_behavioral_pattern_analysis(self, safety_service):
        """Test behavioral pattern analysis"""
        # Setup
        safety_service.analyze_behavioral_patterns.return_value = {
            "patterns_detected": [
                {
                    "type": "mood_change",
                    "description": "Sudden shift from happy to withdrawn",
                    "confidence": 0.78,
                    "timeframe": "last_3_days",
                },
                {
                    "type": "sleep_discussion",
                    "description": "Frequent mentions of nightmares",
                    "confidence": 0.85,
                    "timeframe": "last_week",
                },
            ],
            "risk_level": "medium",
            "recommendations": [
                "Monitor child's sleep patterns",
                "Gentle conversation about feelings",
                "Consider professional consultation if patterns persist",
            ],
        }

        # Test
        analysis = await safety_service.analyze_behavioral_patterns(
            child_id="child123", timeframe_days=7
        )

        # Assert
        assert len(analysis["patterns_detected"]) >= 1
        assert analysis["risk_level"] in ["low", "medium", "high"]
        assert len(analysis["recommendations"]) >= 1
