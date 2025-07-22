#!/usr/bin/env python3
"""
STEP 4.1: Test ESP32 router after adding get_manage_child_profile_use_case()
"""

import sys


def test_esp32_router():
    """Test ESP32 router import after DI fix"""
    print("🔄 STEP 4.1: Testing ESP32 router after DI Container fix")
    print("=" * 80)

    try:
        print("📋 Testing ESP32 router import...")
        from src.presentation.api.esp32_endpoints import router as esp32_router
        print("✅ ESP32 router imported successfully!")
        print(f"   📍 Router type: {type(esp32_router)}")
        print(f"   📍 Router routes: {len(esp32_router.routes)} routes")

        # Try to list routes
        for route in esp32_router.routes:
            print(f"   🔗 Route: {route.path} [{getattr(route, 'methods', 'N/A')}]")

        return True

    except Exception as e:
        print(f"❌ ESP32 router failed: {str(e)}")
        print(f"   📍 Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_esp32_router()
    if success:
        print("\n🎯 RESULT: ESP32 router is now FUNCTIONAL!")
        sys.exit(0)
    else:
        print("\n❌ RESULT: ESP32 router still has blocking issues")
        sys.exit(1)
