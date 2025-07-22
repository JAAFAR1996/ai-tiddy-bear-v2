"""
STEP 3.2: Testing routing and middleware dependencies
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("🔄 STEP 3.2: Testing routing and middleware dependencies")
print("=" * 80)

# Test 8: Try to import middleware setup
print("\n📋 TEST 8: Import middleware setup")
try:
    from src.infrastructure.middleware import setup_middleware
    print("✅ TEST 8 PASSED: Middleware setup imported")

except Exception as e:
    print(f"❌ TEST 8 FAILED: {e}")
    print("🔍 Checking middleware directory...")
    middleware_path = Path("src/infrastructure/middleware")
    if middleware_path.exists():
        print(f"📁 Files in {middleware_path}:")
        for item in middleware_path.iterdir():
            print(f"  - {item.name}")
    else:
        print(f"❌ Directory {middleware_path} does not exist")

# Test 9: Try to import routing setup
print("\n📋 TEST 9: Import routing setup")
try:
    from src.presentation.routing import setup_routing
    print("✅ TEST 9 PASSED: Routing setup imported")

except Exception as e:
    print(f"❌ TEST 9 FAILED: {e}")
    print("🔍 Checking routing in presentation...")
    routing_path = Path("src/presentation")
    if routing_path.exists():
        print(f"📁 Files in {routing_path}:")
        for item in routing_path.iterdir():
            print(f"  - {item.name}")

        # Check for routing.py specifically
        routing_file = routing_path / "routing.py"
        if routing_file.exists():
            print(f"📄 routing.py exists, checking first few lines...")
            with open(routing_file, 'r') as f:
                lines = f.readlines()[:10]
                for i, line in enumerate(lines, 1):
                    print(f"  {i}: {line.rstrip()}")
    else:
        print(f"❌ Directory {routing_path} does not exist")

# Test 10: Try to import OpenAPI config
print("\n📋 TEST 10: Import OpenAPI config")
try:
    from src.presentation.api.openapi_config import configure_openapi
    print("✅ TEST 10 PASSED: OpenAPI config imported")

except Exception as e:
    print(f"❌ TEST 10 FAILED: {e}")
    print("🔍 Checking openapi_config...")

# Test 11: Try to import production check
print("\n📋 TEST 11: Import production check")
try:
    from src.infrastructure.config.core.production_check import enforce_production_safety
    print("✅ TEST 11 PASSED: Production check imported")

except Exception as e:
    print(f"❌ TEST 11 FAILED: {e}")
    print("🔍 Checking production_check...")

# Test 12: Try to import startup validator (without DI container)
print("\n📋 TEST 12: Import startup validator")
try:
    from src.infrastructure.validators.config.startup_validator import validate_startup
    print("✅ TEST 12 PASSED: Startup validator imported")

except Exception as e:
    print(f"❌ TEST 12 FAILED: {e}")
    print("🔍 Checking startup_validator...")

# Test 13: Try to create FastAPI app with basic middleware (no DI)
print("\n📋 TEST 13: Create FastAPI app with basic setup (no DI)")
try:
    from fastapi import FastAPI
    from dotenv import load_dotenv
    load_dotenv()

    app = FastAPI(
        title="AI Teddy Bear v5 - Test with Basic Setup",
        description="Testing basic setup without DI container",
        version="5.0.0-dev"
    )

    @app.get("/health")
    async def health():
        return {"status": "healthy", "message": "Basic setup working"}

    # Try to add middleware if it imported successfully
    # We'll check this in the next test

    print("✅ TEST 13 PASSED: FastAPI app created with basic configuration")

except Exception as e:
    print(f"❌ TEST 13 FAILED: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'=' * 80}")
print("🎯 SUMMARY: Routing and middleware dependency tests completed")
print("Next: Try to identify specific routers and test them individually")
