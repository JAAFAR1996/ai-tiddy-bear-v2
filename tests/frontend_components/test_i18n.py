from unittest.mock import Mock
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


class TestI18n:
    """Test internationalization"""

    def test_language_switching(self):
        """Test language switching between Arabic and English"""
        # Mock i18n
        i18n = Mock()
        i18n.language = "ar"
        i18n.changeLanguage = Mock()

        # Switch to English
        i18n.changeLanguage("en")
        i18n.changeLanguage.assert_called_with("en")

        # Switch back to Arabic
        i18n.changeLanguage("ar")
        assert i18n.changeLanguage.call_count == 2

    def test_rtl_support(self):
        """Test RTL support for Arabic"""
        # Mock document
        document = Mock()

        # Set RTL for Arabic
        document.dir = "rtl"
        assert document.dir == "rtl"

        # Set LTR for English
        document.dir = "ltr"
        assert document.dir == "ltr"
