from infrastructure.di.container import Container as AppContainer
import asyncio
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


try:
    import pytest
except ImportError:
    try:
        from common.mock_pytest import pytest
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


@pytest.mark.asyncio
async def test_singleton_thread_safety():
    container1 = AppContainer()
    container2 = AppContainer()
    assert container1 is container2, "AppContainer is not a singleton!"

    # Test async singleton
    results = await asyncio.gather(
        *(asyncio.to_thread(lambda: AppContainer()) for _ in range(10))
    )
    assert all(r is container1 for r in results)


@pytest.mark.asyncio
async def test_cleanup_on_shutdown(monkeypatch):
    container = AppContainer()
    container.config.from_dict(
        {
            "db": {
                "url": "sqlite+aiosqlite:///:memory:",
                "echo": False,
                "pool_size": 1,
                "max_overflow": 1,
            },
            "redis": {"url": "redis://localhost:6379/0"},
        }
    )
    await container.init_resources()
    # Patch resource close methods to track calls
    closed = {}

    async def fake_close():
        closed["db"] = True

    async def fake_redis_close():
        closed["redis"] = True

    monkeypatch.setattr(container.db_engine(), "dispose", fake_close)
    monkeypatch.setattr(container.redis_client(), "close", fake_redis_close)
    await container.shutdown_resources()
    assert closed.get("db"), "Database resource not closed on shutdown!"
    assert closed.get("redis"), "Redis resource not closed on shutdown!"


@pytest.mark.asyncio
async def test_cleanup_on_init_failure(monkeypatch):
    container = AppContainer()
    container.config.from_dict(
        {
            "db": {
                "url": "invalid://",
                "echo": False,
                "pool_size": 1,
                "max_overflow": 1,
            },
            "redis": {"url": "redis://localhost:6379/0"},
        }
    )
    # Patch db_engine to raise
    monkeypatch.setattr(
        container,
        "db_engine",
        lambda: (_ for _ in ()).throw(Exception("DB init fail")),
    )
    with pytest.raises(Exception):
        await container.init_resources()
    # Should not leave resources open
    await container.shutdown_resources()


@pytest.mark.asyncio
async def test_dependency_injection_and_no_circular():
    container = AppContainer()
    container.config.from_dict(
        {
            "db": {
                "url": "sqlite+aiosqlite:///:memory:",
                "echo": False,
                "pool_size": 1,
                "max_overflow": 1,
            },
            "redis": {"url": "redis://localhost:6379/0"},
        }
    )
    await container.init_resources()
    # Example: ai_service and session_manager should not cause circular import
    ai_service = container.ai_service()
    session_manager = container.session_manager()
    assert ai_service is not None
    assert session_manager is not None
    await container.shutdown_resources()
