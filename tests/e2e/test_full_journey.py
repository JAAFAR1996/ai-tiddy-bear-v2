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


@pytest.mark.asyncio
class TestFullUserJourney:
    """End-to-end tests using Playwright"""

    async def test_parent_child_interaction(self):
        """Test complete parent-child interaction flow"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()

            # Parent login
            page = await browser.new_page()
            await page.goto("http://localhost:3000")
            await page.fill("#email", "parent@test.com")
            await page.fill("#password", "secure-password")
            await page.click("#login-button")

            # Wait for dashboard
            await page.wait_for_selector("#dashboard")

            # Create child profile
            await page.click("#add-child")
            await page.fill("#child-name", "Test Child")
            await page.select_option("#child-age", "7")
            await page.select_option("#language", "ar")
            await page.click("#save-child")

            # Start conversation
            await page.click("#start-conversation")
            await page.wait_for_selector("#conversation-active")

            # Verify audio is playing
            audio_element = await page.query_selector("#audio-player")
            if audio_element:
                is_playing = await audio_element.evaluate("el => !el.paused")
                assert is_playing

            await browser.close()

    async def test_conversation_flow(self):
        """Test conversation interaction"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            # Login and navigate to conversation
            await page.goto("http://localhost:3000/login")
            await page.fill("#email", "parent@test.com")
            await page.fill("#password", "secure-password")
            await page.click("#login-button")

            # Start conversation
            await page.click("#child-profile")
            await page.click("#start-chat")

            # Send text message
            await page.fill("#message-input", "مرحبا، كيف حالك؟")
            await page.click("#send-button")

            # Wait for response
            await page.wait_for_selector(".ai-response", timeout=10000)

            # Verify response appears
            response = await page.text_content(".ai-response")
            assert len(response) > 0

            # Test voice input
            await page.click("#voice-button")
            await page.wait_for_selector("#recording-indicator")

            # Stop recording
            await page.click("#stop-recording")
            await page.wait_for_selector(".ai-response", timeout=15000)

            await browser.close()

    async def test_parental_controls(self):
        """Test parental control features"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            # Login as parent
            await page.goto("http://localhost:3000")
            await page.fill("#email", "parent@test.com")
            await page.fill("#password", "secure-password")
            await page.click("#login-button")

            # Navigate to settings
            await page.click("#settings-menu")
            await page.click("#parental-controls")

            # Set time limits
            await page.fill("#daily-limit", "60")
            await page.check("#content-filter")
            await page.click("#save-settings")

            # Verify settings saved
            success_message = await page.text_content("#success-message")
            assert "Settings saved" in success_message

            # Check conversation history
            await page.click("#conversation-history")
            await page.wait_for_selector(".conversation-item")

            # Verify history is accessible
            conversations = await page.query_selector_all(".conversation-item")
            assert len(conversations) > 0

            await browser.close()
