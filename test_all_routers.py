#!/usr/bin/env python3
"""
STEP 5: SYSTEMATIC ROUTER ACTIVATION & INTEGRATION TESTING
==========================================================
Testing each router one by one to achieve full API functionality.
"""

import sys
import traceback
from typing import Dict, List, Any


def test_router_import(router_name: str, import_path: str) -> Dict[str, Any]:
    """Test if a router can be imported and return its status."""
    result = {
        "name": router_name,
        "status": "Unknown",
        "blocking_issue": None,
        "endpoints": [],
        "router_object": None,
        "error_details": None
    }

    try:
        print(f"\n🔍 Testing {router_name} router import...")
        print(f"   Import path: {import_path}")

        # Dynamic import
        module_parts = import_path.split('.')
        module_name = '.'.join(module_parts[:-1])
        router_attr = module_parts[-1]

        module = __import__(module_name, fromlist=[router_attr])
        router = getattr(module, router_attr)

        result["router_object"] = router
        result["status"] = "Functional"

        # Extract endpoints
        if hasattr(router, 'routes'):
            for route in router.routes:
                if hasattr(route, 'path') and hasattr(route, 'methods'):
                    methods = ', '.join(sorted(route.methods)) if route.methods else 'N/A'
                    result["endpoints"].append(f"{methods} {route.path}")

        print(f"   ✅ SUCCESS: {router_name} router imported")
        print(f"   📍 Type: {type(router)}")
        print(f"   📍 Endpoints: {len(result['endpoints'])}")

    except Exception as e:
        result["status"] = "Failed"
        result["blocking_issue"] = str(e)
        result["error_details"] = {
            "exception_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc()
        }
        print(f"   ❌ FAILED: {e}")

    return result


def main():
    """Main testing function."""
    print("🎯 STEP 5: SYSTEMATIC ROUTER ACTIVATION & INTEGRATION TESTING")
    print("=" * 70)

    # Define routers to test
    routers_to_test = [
        ("Parental Dashboard", "src.presentation.api.parental_dashboard.router"),
        ("ESP32 Endpoints", "src.presentation.api.esp32_endpoints.router"),
        ("ChatGPT Endpoints", "src.presentation.api.chatgpt_endpoints.router"),
        ("Health Endpoints", "src.presentation.api.health_endpoints.router"),
        ("Auth Endpoints", "src.presentation.api.auth_endpoints.router"),
    ]

    results = []

    # Test each router
    for router_name, import_path in routers_to_test:
        result = test_router_import(router_name, import_path)
        results.append(result)

    # Summary table
    print("\n" + "=" * 70)
    print("📊 ROUTER ACTIVATION SUMMARY TABLE")
    print("=" * 70)
    print(f"{'Router Name':<20} {'Status':<12} {'Endpoints':<10} {'Blocking Issue':<25}")
    print("-" * 70)

    functional_count = 0
    failed_count = 0

    for result in results:
        status = result["status"]
        endpoints_count = len(result["endpoints"])
        blocking_issue = result["blocking_issue"][:22] + "..." if result["blocking_issue"] and len(result["blocking_issue"]) > 25 else (result["blocking_issue"] or "None")

        print(f"{result['name']:<20} {status:<12} {endpoints_count:<10} {blocking_issue:<25}")

        if status == "Functional":
            functional_count += 1
        else:
            failed_count += 1

    print("-" * 70)
    print(f"✅ Functional: {functional_count} | ❌ Failed: {failed_count}")

    # Detailed error logs
    print("\n" + "=" * 70)
    print("🔍 DETAILED ERROR LOGS")
    print("=" * 70)

    for result in results:
        if result["status"] == "Failed":
            print(f"\n❌ {result['name']} ROUTER FAILURE:")
            print(f"   Error Type: {result['error_details']['exception_type']}")
            print(f"   Error Message: {result['error_details']['error_message']}")
            print(f"   Full Traceback:")
            for line in result['error_details']['traceback'].split('\n'):
                if line.strip():
                    print(f"      {line}")

    # Functional router details
    print("\n" + "=" * 70)
    print("✅ FUNCTIONAL ROUTER ENDPOINTS")
    print("=" * 70)

    for result in results:
        if result["status"] == "Functional":
            print(f"\n🟢 {result['name']} ({len(result['endpoints'])} endpoints):")
            for i, endpoint in enumerate(result['endpoints'], 1):
                print(f"   {i}. {endpoint}")

    print("\n" + "=" * 70)
    print("🎯 NEXT STEPS:")
    if failed_count > 0:
        print("   1. Fix blocking issues for failed routers")
        print("   2. Re-test until all routers are functional")
        print("   3. Then proceed to HTTP integration testing")
    else:
        print("   1. All routers functional - proceed to HTTP testing")
        print("   2. Test happy-path and failure scenarios")
        print("   3. Document API behavior")
    print("=" * 70)


if __name__ == "__main__":
    main()
