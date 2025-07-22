#!/usr/bin/env python3
"""
STEP 4.2: Test Parental Dashboard router after adding get_manage_child_profile_use_case()
"""

import sys


def test_parental_router():
    """Test Parental Dashboard router import after DI fix"""
    print("🔄 STEP 4.2: Testing Parental Dashboard router after DI Container fix")
    print("=" * 80)

    try:
        print("📋 Testing Parental Dashboard router import...")
        from src.presentation.api.parental_dashboard import router as parental_router
        print("✅ Parental Dashboard router imported successfully!")
        print(f"   📍 Router type: {type(parental_router)}")
        print(f"   📍 Router routes: {len(parental_router.routes)} routes")

        # Try to list routes
        for route in parental_router.routes:
            print(f"   🔗 Route: {route.path} [{getattr(route, 'methods', 'N/A')}]")

        return True

    except Exception as e:
        print(f"❌ Parental Dashboard router failed: {str(e)}")
        print(f"   📍 Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_parental_router()
    if success:
        print("\n🎯 RESULT: Parental Dashboard router is now FUNCTIONAL!")
        sys.exit(0)
    else:
        print("\n❌ RESULT: Parental Dashboard router still has blocking issues")
        sys.exit(1)
