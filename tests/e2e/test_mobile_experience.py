import sys
from pathlib import Path

from playwright.async_api import async_playwright

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


@pytest.mark.asyncio
class TestMobileExperience:
    """Test mobile user experience"""

    async def test_mobile_conversation(self):
        """Test conversation on mobile device"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()

            # Create mobile context
            context = await browser.new_context(
                viewport={"width": 375, "height": 667},
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
            )

            page = await context.new_page()

            # Navigate to mobile app
            await page.goto("http://localhost:3000")

            # Test touch interactions
            await page.tap("#login-button")
            await page.fill("#email", "parent@test.com")
            await page.fill("#password", "secure-password")
            await page.tap("#submit-login")

            # Test mobile conversation
            await page.tap("#child-avatar")
            await page.tap("#voice-chat-button")

            # Verify mobile UI elements
            assert await page.is_visible("#mobile-voice-controls")
            assert await page.is_visible("#mobile-chat-interface")

            # Test swipe gestures (if applicable)
            await page.swipe("#conversation-area", "left")

            await browser.close()

    async def test_responsive_design(self):
        """Test responsive design across devices"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()

            # Test different screen sizes
            viewports = [
                {"width": 320, "height": 568},  # iPhone SE
                {"width": 768, "height": 1024},  # iPad
                {"width": 1920, "height": 1080},  # Desktop
            ]

            for viewport in viewports:
                context = await browser.new_context(viewport=viewport)
                page = await context.new_page()

                await page.goto("http://localhost:3000")

                # Check if navigation is accessible
                if viewport["width"] < 768:
                    # Mobile menu
                    assert await page.is_visible("#mobile-menu-button")
                else:
                    # Desktop navigation
                    assert await page.is_visible("#desktop-nav")

                # Check conversation interface adapts
                await page.goto("http://localhost:3000/conversation")
                assert await page.is_visible("#conversation-container")

                await context.close()

            await browser.close()
