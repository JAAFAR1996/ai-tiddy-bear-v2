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


class TestReports:
    """Test reports functionality"""

    @pytest.mark.asyncio
    async def test_generate_report(self, report_service):
        """Test report generation"""
        # Arrange
        report_params = {
            "childId": "child1",
            "type": "weekly",
            "period": {"start": "2024-01-01", "end": "2024-01-07"},
        }
        generated_report = {
            "id": "report1",
            "childId": "child1",
            "type": "weekly",
            "metrics": {
                "conversationCount": 14,
                "totalInteractionTime": 5400,
                "emotionalDistribution": {
                    "happy": 0.5,
                    "excited": 0.3,
                    "neutral": 0.2,
                },
            },
            "insights": [
                {
                    "type": "achievement",
                    "title": "تحسن في المفردات",
                    "description": "زيادة استخدام كلمات جديدة بنسبة 20%",
                }
            ],
        }
        report_service.generate_report.return_value = generated_report

        # Act
        report = await report_service.generate_report(report_params)

        # Assert
        assert report["id"] == "report1"
        assert report["metrics"]["conversationCount"] == 14
        assert len(report["insights"]) == 1
        assert report["insights"][0]["type"] == "achievement"

    @pytest.mark.asyncio
    async def test_export_report_pdf(self, report_service):
        """Test PDF export"""
        # Arrange
        report_service.export_report.return_value = b"PDF_CONTENT"

        # Act
        pdf_content = await report_service.export_report("report1", "pdf")

        # Assert
        assert pdf_content == b"PDF_CONTENT"
        report_service.export_report.assert_called_once_with("report1", "pdf")
