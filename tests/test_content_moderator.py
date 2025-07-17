from domain.safety.models import ContentModerator, ProfanityRule
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


class TestContentModerator:
    """Test content moderation service"""

    def setup_method(self):
        """Setup test fixtures"""
        self.moderator = ContentModerator()

    def test_appropriate_content(self):
        """Test content that should pass moderation"""
        content = "Hello, how are you today?"

        assert self.moderator.is_appropriate(content, 6) is True

    def test_inappropriate_language(self):
        """Test content with inappropriate language"""
        content = "That's so stupid and bad"

        assert self.moderator.is_appropriate(content, 6) is False

    def test_age_appropriate_content(self):
        """Test age-appropriate content filtering"""
        complex_content = "This is very complex and difficult to understand"

        # Should fail for young children
        assert self.moderator.is_appropriate(complex_content, 3) is False

        # Should pass for older children
        assert self.moderator.is_appropriate(complex_content, 8) is True

    def test_custom_rules(self):
        """Test moderator with custom rules"""
        custom_rule = ProfanityRule()
        moderator = ContentModerator([custom_rule])

        assert moderator.is_appropriate("Hello world", 5) is True
        assert moderator.is_appropriate("That's bad", 5) is False
