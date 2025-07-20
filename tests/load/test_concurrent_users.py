import asyncio
import sys
import time
from pathlib import Path

import aiohttp

from src.infrastructure.logging_config import get_logger

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    import aiohttp
except ImportError:
    # Mock aiohttp when not available
    class MockAiohttp:
        class ClientSession:
            def __init__(self, *args, **kwargs):
                pass

            async def get(self, url, **kwargs):
                class MockResponse:
                    def __init__(self):
                        self.status = 200

                    async def json(self):
                        return {"mock": "response"}

                    async def text(self):
                        return "mock response"

                return MockResponse()

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

    aiohttp = MockAiohttp()


logger = get_logger(__name__, component="test")


class ConcurrentUserTest:
    """Test concurrent user scenarios"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: list[dict] = []

    async def simulate_user_session(self, session: aiohttp.ClientSession, user_id: int):
        """Simulate a complete user session"""
        start_time = time.time()
        try:
            async with session.post(
                f"{self.base_url}/api/v1/auth/login",
                json={
                    "email": f"user{user_id}@test.com",
                    "password": "test-password",
                },
            ) as response:
                if response.status != 200:
                    return {"user_id": user_id, "status": "login_failed"}
                token = (await response.json())["access_token"]
                headers = {"Authorization": f"Bearer {token}"}
            async with session.post(
                f"{self.base_url}/api/v1/conversations/start",
                json={
                    "child_id": f"child-{user_id}",
                    "initial_message": "Hello",
                },
                headers=headers,
            ) as response:
                if response.status != 200:
                    return {
                        "user_id": user_id,
                        "status": "conversation_failed",
                    }
            for i in range(3):
                async with session.post(
                    f"{self.base_url}/api/v1/conversations/active/messages",
                    json={"text": f"Message {i + 1}"},
                    headers=headers,
                ) as response:
                    if response.status != 200:
                        return {"user_id": user_id, "status": "message_failed"}
                await asyncio.sleep(0.5)
            end_time = time.time()
            return {
                "user_id": user_id,
                "status": "success",
                "duration": end_time - start_time,
            }
        except Exception as e:
            return {"user_id": user_id, "status": "error", "error": str(e)}

    async def run_concurrent_test(self, num_users: int = 50):
        """Run concurrent user test"""
        async with aiohttp.ClientSession() as session:
            tasks = [self.simulate_user_session(session, i) for i in range(num_users)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            successful = sum(
                1
                for r in results
                if isinstance(r, dict) and r.get("status") == "success"
            )
            failed = len(results) - successful
            if successful > 0:
                avg_duration = (
                    sum(
                        r["duration"]
                        for r in results
                        if isinstance(r, dict) and "duration" in r
                    )
                    / successful
                )
            else:
                avg_duration = 0
            logger.info(f"Concurrent Users: {num_users}")
            logger.info(f"Successful: {successful}")
            logger.info(f"Failed: {failed}")
            logger.info(f"Success Rate: {successful / num_users * 100:.1f}%")
            logger.info(f"Average Duration: {avg_duration:.2f}s")
            return results


if __name__ == "__main__":
    test = ConcurrentUserTest()
    asyncio.run(test.run_concurrent_test(50))
