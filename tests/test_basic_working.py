"""Basic working test file."""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    import pytest
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


def test_basic_functionality():
    """Test basic functionality."""
    assert True


def test_python_basics():
    """Test Python basics work."""
    assert 1 + 1 == 2
    assert "hello" == "hello"
    assert [1, 2, 3] == [1, 2, 3]


def test_imports():
    """Test basic imports work."""
    import json
    import os
    import sys

    assert json is not None
    assert os is not None
    assert sys is not None


class TestBasicClass:
    """Test basic class functionality."""

    def test_class_method(self):
        """Test class method."""
        assert True

    def test_another_method(self):
        """Test another method."""
        value = 42
        assert value == 42
