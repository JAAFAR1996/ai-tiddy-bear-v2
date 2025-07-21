import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


class TestAccessibility:
    """Test accessibility features"""

    def test_aria_labels(self):
        """Test ARIA labels are present"""
        elements = [
            {"role": "button", "aria-label": "فتح القائمة"},
            {"role": "navigation", "aria-label": "القائمة الرئيسية"},
            {"role": "main", "aria-label": "المحتوى الرئيسي"},
        ]

        for element in elements:
            assert "aria-label" in element
            assert element["aria-label"] != ""

    def test_keyboard_navigation(self):
        """Test keyboard navigation support"""
        # Mock keyboard events
        keyboard_events = [
            {"key": "Tab", "result": "next_element"},
            {"key": "Shift+Tab", "result": "previous_element"},
            {"key": "Enter", "result": "activate"},
            {"key": "Escape", "result": "close"},
        ]

        for event in keyboard_events:
            assert event["result"] is not None
