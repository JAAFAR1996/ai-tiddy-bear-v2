"""
STEP 3.3: Testing individual router imports
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("🔄 STEP 3.3: Testing individual router imports")
print("=" * 80)

# Test 14: Try to import individual routers one by one
routers_to_test = [
    ("ESP32 router", "src.presentation.api.esp32_endpoints", "router"),
    ("Health router", "src.presentation.api.health_endpoints", "router"),
    ("ChatGPT router", "src.presentation.api.endpoints.chatgpt", "router"),
    ("Auth router", "src.presentation.api.endpoints.auth", "router"),
    ("Parental dashboard router", "src.presentation.api.parental_dashboard", "router"),
]

working_routers = []
failed_routers = []

for router_name, module_path, router_attr in routers_to_test:
    print(f"\n📋 Testing {router_name}")
    try:
        module = __import__(module_path, fromlist=[router_attr])
        router = getattr(module, router_attr)
        working_routers.append((router_name, module_path, router))
        print(f"✅ {router_name} imported successfully")

        # Try to inspect the router routes
        if hasattr(router, 'routes'):
            route_count = len(router.routes)
            print(f"   📊 Routes found: {route_count}")
            for route in router.routes[:3]:  # Show first 3 routes
                if hasattr(route, 'path') and hasattr(route, 'methods'):
                    methods = getattr(route, 'methods', {})
                    print(f"   🛣️  {list(methods)} {route.path}")

    except Exception as e:
        failed_routers.append((router_name, module_path, str(e)))
        print(f"❌ {router_name} failed: {e}")
        print(f"   📍 Module: {module_path}")

print(f"\n{'=' * 80}")
print("🎯 ROUTER IMPORT SUMMARY:")
print(f"✅ Working routers: {len(working_routers)}")
for name, _, _ in working_routers:
    print(f"   - {name}")

print(f"❌ Failed routers: {len(failed_routers)}")
for name, path, error in failed_routers:
    print(f"   - {name}: {error}")

# Test 15: Create minimal FastAPI app with working routers only
if working_routers:
    print(f"\n📋 TEST 15: Create FastAPI app with working routers")
    try:
        from fastapi import FastAPI
        from dotenv import load_dotenv
        load_dotenv()

        app = FastAPI(
            title="AI Teddy Bear v5 - Partial Router Test",
            description="Testing with working routers only",
            version="5.0.0-dev"
        )

        # Add a basic health endpoint
        @app.get("/")
        async def root():
            return {
                "message": "Partial router test",
                "working_routers": [name for name, _, _ in working_routers],
                "failed_routers": [name for name, _, _ in failed_routers]
            }

        # Include working routers
        for router_name, _, router in working_routers:
            try:
                app.include_router(router, prefix=f"/api/{router_name.lower().replace(' ', '-')}")
                print(f"   ✅ {router_name} included successfully")
            except Exception as e:
                print(f"   ❌ Failed to include {router_name}: {e}")

        print("✅ TEST 15 PASSED: FastAPI app created with working routers")

        # Try to start the server briefly
        print("\n🚀 Starting server with working routers...")
        import uvicorn

        # Quick server test
        uvicorn.run(
            "test_individual_routers:app",
            host="127.0.0.1",
            port=8002,
            reload=False,
            log_level="info"
        )

    except Exception as e:
        print(f"❌ TEST 15 FAILED: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\n❌ No working routers found - cannot create functional app")
