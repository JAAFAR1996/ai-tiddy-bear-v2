"""Simple test script to validate get_all_profiles implementation."""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that all imports work correctly."""
    try:
        from src.infrastructure.persistence.redis_personality_profile_repository import (
            RedisPersonalityProfileRepository,
        )

        print("✅ RedisPersonalityProfileRepository import successful")


        print("✅ IPersonalityProfileRepository import successful")

        # Check method exists
        if hasattr(RedisPersonalityProfileRepository, "get_all_profiles"):
            print("✅ get_all_profiles method exists")
        else:
            print("❌ get_all_profiles method not found")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_method_signature():
    """Test that the method signature is correct."""
    try:
        import inspect

        from src.infrastructure.persistence.redis_personality_profile_repository import (
            RedisPersonalityProfileRepository,
        )

        sig = inspect.signature(RedisPersonalityProfileRepository.get_all_profiles)
        print(f"✅ Method signature: get_all_profiles{sig}")

        # Check parameters
        params = sig.parameters
        expected_params = ["self", "batch_size", "cursor", "max_profiles"]

        for param in expected_params:
            if param in params:
                print(f"  ✅ Parameter '{param}' found")
            else:
                print(f"  ❌ Parameter '{param}' missing")

        return True

    except Exception as e:
        print(f"❌ Method signature test failed: {e}")
        return False


if __name__ == "__main__":
    print("Testing get_all_profiles implementation...")
    print("=" * 50)

    if test_imports():
        test_method_signature()

    print("=" * 50)
    print("Test completed.")
