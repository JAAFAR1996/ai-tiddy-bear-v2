"""
STEP 3: ITERATIVE DI CONTAINER RECOVERY
Minimal FastAPI app to test dependencies one by one
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("🔄 STEP 3: Testing minimal FastAPI app with incremental dependencies")
print("=" * 80)

# Test 1: Basic FastAPI without any custom dependencies
print("\n📋 TEST 1: Basic FastAPI import and creation")
try:
    from fastapi import FastAPI

    app = FastAPI(title="AI Teddy Bear - Minimal Test", version="0.1.0")

    @app.get("/")
    async def root():
        return {"message": "Minimal FastAPI app working"}

    print("✅ TEST 1 PASSED: Basic FastAPI app created successfully")

except Exception as e:
    print(f"❌ TEST 1 FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Import python-dotenv
print("\n📋 TEST 2: Import python-dotenv")
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ TEST 2 PASSED: python-dotenv imported and loaded")

except Exception as e:
    print(f"❌ TEST 2 FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Import fastapi-limiter (but don't initialize yet)
print("\n📋 TEST 3: Import fastapi-limiter")
try:
    from fastapi_limiter import FastAPILimiter
    print("✅ TEST 3 PASSED: fastapi-limiter imported successfully")

except Exception as e:
    print(f"❌ TEST 3 FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Import redis (but don't connect yet)
print("\n📋 TEST 4: Import redis")
try:
    from redis.asyncio import Redis
    print("✅ TEST 4 PASSED: redis imported successfully")

except Exception as e:
    print(f"❌ TEST 4 FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Try to import common exceptions
print("\n📋 TEST 5: Import common exceptions")
try:
    from src.common.exceptions import StartupValidationException
    print("✅ TEST 5 PASSED: Common exceptions imported")

except Exception as e:
    print(f"❌ TEST 5 FAILED: {e}")
    print("🔍 Checking what files exist in src/common/...")
    common_path = Path("src/common")
    if common_path.exists():
        print(f"📁 Files in {common_path}:")
        for item in common_path.iterdir():
            print(f"  - {item.name}")
    else:
        print(f"❌ Directory {common_path} does not exist")

# Test 6: Try to import logging config
print("\n📋 TEST 6: Import logging config")
try:
    from src.infrastructure.logging_config import configure_logging, get_logger
    logger = get_logger(__name__, component="test")
    print("✅ TEST 6 PASSED: Logging config imported and logger created")

except Exception as e:
    print(f"❌ TEST 6 FAILED: {e}")
    print("🔍 Checking logging_config.py...")

# Test 7: Try to import DI container
print("\n📋 TEST 7: Import DI container")
try:
    from src.infrastructure.di.container import container
    print("✅ TEST 7 PASSED: DI container imported")

except Exception as e:
    print(f"❌ TEST 7 FAILED: {e}")
    print("🔍 This is expected - we know the DI container has issues")

print("\n" + "=" * 80)
print("🎯 SUMMARY: Completed initial dependency tests")
print("Next: Start uvicorn server with minimal app to test basic functionality")

if __name__ == "__main__":
    print("\n🚀 Starting minimal uvicorn server...")
    import uvicorn

    # Try to start the minimal server
    try:
        uvicorn.run(
            "minimal_main:app",
            host="127.0.0.1",
            port=8001,  # Different port to avoid conflicts
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        import traceback
        traceback.print_exc()
