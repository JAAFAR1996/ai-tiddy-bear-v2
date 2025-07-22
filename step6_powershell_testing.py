#!/usr/bin/env python3
"""
STEP 6: HTTP Integration Testing - PowerShell Compatible Version
=================================================================
Tests all available endpoints using simple HTTP requests.
"""

import subprocess
import json
import sys
from datetime import datetime


class PowerShellHTTPTester:
    """HTTP tester using PowerShell commands."""

    def __init__(self):
        self.results = []
        self.base_url = "http://localhost:8000"

    def run_powershell(self, command: str) -> dict:
        """Run PowerShell command and return result."""
        try:
            # Run the PowerShell command
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "output": result.stdout.strip(),
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "output": result.stdout.strip(),
                    "error": result.stderr.strip()
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "Request timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e)
            }

    def test_get_endpoint(self, path: str, scenario: str) -> dict:
        """Test GET endpoint."""
        command = f'Invoke-RestMethod -Uri "{self.base_url}{path}" -Method GET'
        result = self.run_powershell(command)

        status = "✅ Success" if result["success"] else "❌ Failed"
        details = result["output"] if result["success"] else result["error"]

        self.log_result(f"GET {path}", scenario, status, details[:100])
        return result

    def test_post_endpoint(self, path: str, scenario: str, body: dict = None) -> dict:
        """Test POST endpoint."""
        if body is None:
            body = {}

        body_json = json.dumps(body).replace('"', '\\"')
        command = f'''
$body = '{body_json}'
Invoke-RestMethod -Uri "{self.base_url}{path}" -Method POST -Body $body -ContentType "application/json"
        '''.strip()

        result = self.run_powershell(command)

        status = "✅ Success" if result["success"] else "❌ Failed"
        details = result["output"] if result["success"] else result["error"]

        self.log_result(f"POST {path}", scenario, status, details[:100])
        return result

    def test_put_endpoint(self, path: str, scenario: str, body: dict = None) -> dict:
        """Test PUT endpoint."""
        if body is None:
            body = {}

        body_json = json.dumps(body).replace('"', '\\"')
        command = f'''
$body = '{body_json}'
Invoke-RestMethod -Uri "{self.base_url}{path}" -Method PUT -Body $body -ContentType "application/json"
        '''.strip()

        result = self.run_powershell(command)

        status = "✅ Success" if result["success"] else "❌ Failed"
        details = result["output"] if result["success"] else result["error"]

        self.log_result(f"PUT {path}", scenario, status, details[:100])
        return result

    def test_delete_endpoint(self, path: str, scenario: str) -> dict:
        """Test DELETE endpoint."""
        command = f'Invoke-RestMethod -Uri "{self.base_url}{path}" -Method DELETE'
        result = self.run_powershell(command)

        status = "✅ Success" if result["success"] else "❌ Failed"
        details = result["output"] if result["success"] else result["error"]

        self.log_result(f"DELETE {path}", scenario, status, details[:100])
        return result

    def log_result(self, endpoint: str, scenario: str, status: str, details: str):
        """Log test result."""
        result = {
            "endpoint": endpoint,
            "scenario": scenario,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        print(f"  {status} {endpoint:25} | {scenario:20} | {details[:50]}")


def main():
    """Run comprehensive HTTP integration testing."""
    print("🎯 STEP 6: HTTP INTEGRATION TESTING")
    print("=" * 80)
    print("Testing all available endpoints with PowerShell commands...")
    print()

    tester = PowerShellHTTPTester()

    # === ChatGPT Endpoints (2 endpoints) ===
    print("🟢 CHATGPT ENDPOINTS")
    print("-" * 60)

    tester.test_get_endpoint("/chatgpt/status", "Service status check")
    tester.test_post_endpoint("/chatgpt/chat", "Empty chat request")
    tester.test_post_endpoint("/chatgpt/chat", "Valid chat request", {
        "message": "Hello",
        "user_id": "test-user"
    })

    # === Auth Endpoints (3 endpoints) ===
    print("\n🟢 AUTH ENDPOINTS")
    print("-" * 60)

    tester.test_get_endpoint("/auth/status", "Auth service status")
    tester.test_post_endpoint("/auth/login", "Empty login request")
    tester.test_post_endpoint("/auth/login", "Valid login request", {
        "username": "testuser",
        "password": "testpass"
    })
    tester.test_post_endpoint("/auth/logout", "Empty logout request")
    tester.test_post_endpoint("/auth/logout", "Valid logout request", {
        "token": "fake-jwt-token"
    })

    # === Parental Dashboard Endpoints (9 endpoints) ===
    print("\n🟢 PARENTAL DASHBOARD ENDPOINTS")
    print("-" * 60)

    # Test if any work
    tester.test_get_endpoint("/children/test-123", "Get child by ID")
    tester.test_post_endpoint("/children", "Create child - empty")
    tester.test_post_endpoint("/children", "Create child - valid", {
        "name": "Test Child",
        "age": 8,
        "parent_email": "parent@example.com"
    })
    tester.test_put_endpoint("/children/test-123", "Update child", {
        "name": "Updated Child"
    })
    tester.test_delete_endpoint("/children/test-123", "Delete child")
    tester.test_post_endpoint("/children/test-123/story", "Generate story", {
        "theme": "adventure"
    })
    tester.test_post_endpoint("/children/test-123/consent/request", "Request consent", {
        "consent_type": "data_collection"
    })
    tester.test_post_endpoint("/children/test-123/consent/grant", "Grant consent", {
        "consent_type": "data_collection",
        "granted": True
    })
    tester.test_get_endpoint("/children/test-123/consent/status", "Check consent status")
    tester.test_delete_endpoint("/children/test-123/consent/data_collection", "Revoke consent")

    # === Generate Report ===
    print("\n" + "=" * 80)
    print("📊 STEP 6 HTTP INTEGRATION TEST RESULTS")
    print("=" * 80)

    total_tests = len(tester.results)
    successful_tests = len([r for r in tester.results if "✅" in r["status"]])
    failed_tests = len([r for r in tester.results if "❌" in r["status"]])

    print(f"\n📈 SUMMARY:")
    print(f"   Total Tests: {total_tests}")
    print(f"   ✅ Successful: {successful_tests}")
    print(f"   ❌ Failed: {failed_tests}")
    print(f"   Success Rate: {(successful_tests / total_tests) * 100:.1f}%")

    print(f"\n📋 DETAILED RESULTS:")
    print("-" * 80)
    print(f"{'Endpoint':<30} {'Scenario':<25} {'Status':<12} {'Details':<30}")
    print("-" * 80)

    for result in tester.results:
        endpoint = result["endpoint"][:29]
        scenario = result["scenario"][:24]
        status = result["status"][:11]
        details = result["details"][:29]
        print(f"{endpoint:<30} {scenario:<25} {status:<12} {details:<30}")

    # Analyze by router
    print(f"\n🔍 ROUTER ANALYSIS:")
    print("-" * 80)

    chatgpt_results = [r for r in tester.results if "/chatgpt/" in r["endpoint"]]
    auth_results = [r for r in tester.results if "/auth/" in r["endpoint"]]
    parental_results = [r for r in tester.results if "/children/" in r["endpoint"]]

    def analyze_router(results, name):
        if not results:
            print(f"❌ {name}: No endpoints tested")
            return
        success = len([r for r in results if "✅" in r["status"]])
        total = len(results)
        rate = (success / total) * 100
        status_icon = "✅" if rate >= 80 else "⚠️" if rate >= 50 else "❌"
        print(f"{status_icon} {name}: {success}/{total} ({rate:.0f}%) functional")

        # Show common errors
        errors = [r["details"] for r in results if "❌" in r["status"]]
        if errors:
            common_error = max(set(errors), key=errors.count) if errors else ""
            print(f"   Common Error: {common_error[:60]}")

    analyze_router(chatgpt_results, "ChatGPT Router")
    analyze_router(auth_results, "Auth Router")
    analyze_router(parental_results, "Parental Dashboard Router")

    # Production readiness assessment
    print(f"\n💡 PRODUCTION READINESS ASSESSMENT:")
    print("-" * 80)

    if successful_tests / total_tests >= 0.8:
        print("✅ EXCELLENT: Most endpoints are functional and ready for production")
    elif successful_tests / total_tests >= 0.6:
        print("⚠️  GOOD: Majority of endpoints work, minor issues to address")
    elif successful_tests / total_tests >= 0.4:
        print("⚠️  FAIR: Significant issues found, needs attention before production")
    else:
        print("❌ POOR: Major functionality issues, not ready for production")

    # Key findings
    dependency_errors = [r for r in tester.results if "dependency" in r["details"].lower() or "injection" in r["details"].lower()]
    auth_errors = [r for r in tester.results if "auth" in r["details"].lower() or "token" in r["details"].lower()]
    validation_errors = [r for r in tester.results if "422" in r["details"] or "validation" in r["details"].lower()]

    print(f"\n🚨 KEY FINDINGS:")
    if dependency_errors:
        print(f"   • Dependency Injection Issues: {len(dependency_errors)} endpoints affected")
    if auth_errors:
        print(f"   • Authentication Issues: {len(auth_errors)} endpoints affected")
    if validation_errors:
        print(f"   • Input Validation Issues: {len(validation_errors)} endpoints affected")

    # Save results
    with open("step6_final_http_test_results.json", "w") as f:
        json.dump({
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": (successful_tests / total_tests) * 100
            },
            "results": tester.results
        }, f, indent=2)

    print(f"\n📄 Full results saved to: step6_final_http_test_results.json")
    print("🏆 STEP 6 HTTP INTEGRATION TESTING COMPLETED")


if __name__ == "__main__":
    main()
