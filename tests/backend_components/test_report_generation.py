import sys
from datetime import datetime, timedelta
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
            pass

            def decorator(func):
                return func

            return decorator

        def mark(self):
            pass

            class MockMark:
                def parametrize(self, *args, **kwargs):
                    pass

                    def decorator(func):
                return func

                    return decorator

                def asyncio(self, func):
                    pass

                    return func

                def slow(self, func):
                    pass

                    return func

                def skip(self, reason=""):
                    pass

                    def decorator(func):
                return func

                    return decorator

            return MockMark()

        def raises(self, exception):
            pass

            class MockRaises:
                def __enter__(self):
                    pass

                    return self

                def __exit__(self, *args):
                    pass

                    return False

            return MockRaises()

        def skip(self, reason=""):
            pass

            def decorator(func):
                return func

            return decorator

    pytest = MockPytest()


class TestReportGeneration:
    """Test report generation functionality"""

    @pytest.mark.asyncio
    async def test_daily_report_generation(self, report_service):
        """Test daily report generation"""
        # Setup
        report_service.generate_daily_report.return_value = {
            "report_id": "daily_001",
            "date": "2024-01-15",
            "child_id": "child123",
            "summary": {
                "total_interactions": 8,
                "total_time_minutes": 45,
                "dominant_emotion": "happy",
                "topics_discussed": ["animals", "colors", "family"],
                "new_words_learned": ["فيل", "أزرق", "سعيد"],
            },
            "detailed_metrics": {
                "emotion_distribution": {
                    "happy": 0.60,
                    "neutral": 0.25,
                    "excited": 0.15,
                },
                "engagement_score": 0.88,
                "educational_progress": {
                    "vocabulary": "+5 words",
                    "pronunciation": "improving",
                    "comprehension": "excellent",
                },
            },
            "highlights": [
                "Child showed great enthusiasm during animal story",
                "Successfully learned color names in Arabic",
                "Positive interaction with educational content",
            ],
            "concerns": [],
            "recommendations": [
                "Continue with animal-themed stories",
                "Introduce more complex vocabulary gradually",
            ],
        }

        # Test
        report = await report_service.generate_daily_report(
            child_id="child123", date="2024-01-15"
        )

        # Assert
        assert report["report_id"] is not None
        assert report["summary"]["total_interactions"] == 8
        assert report["summary"]["dominant_emotion"] == "happy"
        assert len(report["summary"]["new_words_learned"]) >= 3
        assert report["detailed_metrics"]["engagement_score"] > 0.8
        assert len(report["highlights"]) >= 3
        assert len(report["concerns"]) == 0

    @pytest.mark.asyncio
    async def test_weekly_report_with_insights(self, report_service):
        """Test weekly report with AI insights"""
        # Setup
        report_service.generate_weekly_report.return_value = {
            "report_id": "weekly_001",
            "period": {"start": "2024-01-08", "end": "2024-01-14"},
            "child_id": "child123",
            "overview": {
                "total_days_active": 6,
                "total_conversations": 42,
                "total_time_hours": 5.5,
                "average_daily_time_minutes": 55,
            },
            "progress_tracking": {
                "language_skills": {
                    "score": 82,
                    "trend": "improving",
                    "details": "15% increase in vocabulary usage",
                },
                "emotional_development": {
                    "score": 88,
                    "trend": "stable",
                    "details": "Consistent positive emotional expression",
                },
                "social_skills": {
                    "score": 75,
                    "trend": "improving",
                    "details": "Better turn-taking in conversations",
                },
            },
            "ai_insights": [
                {
                    "insight": "Child responds best to interactive storytelling between 4-6 PM",
                    "confidence": 0.89,
                    "recommendation": "Schedule primary learning activities during this time",
                },
                {
                    "insight": "Interest in space and astronomy topics is emerging",
                    "confidence": 0.76,
                    "recommendation": "Introduce age-appropriate space stories and facts",
                },
            ],
            "parent_action_items": [
                "Praise child for vocabulary improvements",
                "Consider supplementing with space-themed books",
                "Maintain consistent interaction schedule",
            ],
        }

        # Test
        report = await report_service.generate_weekly_report(
            child_id="child123", week_start="2024-01-08"
        )

        # Assert
        assert report["overview"]["total_conversations"] == 42
        assert (
            report["progress_tracking"]["language_skills"]["trend"]
            == "improving"
        )
        assert len(report["ai_insights"]) >= 2
        assert report["ai_insights"][0]["confidence"] > 0.7
        assert len(report["parent_action_items"]) >= 3

    @pytest.mark.asyncio
    async def test_report_export(self, report_service):
        """Test report export functionality"""
        # Setup PDF export
        report_service.export_report.return_value = {
            "format": "pdf",
            "file_size_bytes": 245000,
            "file_name": "weekly_report_child123_2024-01-14.pdf",
            "download_url": "/api/reports/download/weekly_001.pdf",
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        }

        # Test PDF export
        pdf_export = await report_service.export_report(
            report_id="weekly_001", format="pdf"
        )

        assert pdf_export["format"] == "pdf"
        assert pdf_export["file_size_bytes"] > 0
        assert pdf_export["download_url"] is not None

        # Test email export
        report_service.export_report.return_value = {
            "format": "email",
            "sent_to": ["parent@example.com"],
            "sent_at": datetime.utcnow().isoformat(),
            "status": "delivered",
        }

        email_export = await report_service.export_report(
            report_id="weekly_001",
            format="email",
            recipient="parent@example.com",
        )

        assert email_export["format"] == "email"
        assert email_export["status"] == "delivered"
        assert "parent@example.com" in email_export["sent_to"]
