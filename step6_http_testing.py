#!/usr/bin/env python3
"""
STEP 6: HTTP INTEGRATION TESTING FOR FUNCTIONAL ENDPOINTS
=========================================================
Comprehensive testing of all 14 functional endpoints across 3 routers.
"""

import asyncio
import json
import subprocess
import sys
import time
from datetime import datetime
from typing import Any, Dict, List

import httpx


class EndpointTester:
    """Comprehensive HTTP endpoint testing framework."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url, timeout=30.0)
        self.results = []

    def log_test(self, endpoint: str, scenario: str, status: str, details: str):
        """Log a test result."""
        result = {
            "endpoint": endpoint,
            "scenario": scenario,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        print(f"  {status} {endpoint} - {scenario}: {details}")

    def test_endpoint(self, method: str, path: str, scenario: str,
                      data: Dict[str, Any] = None, headers: Dict[str, str] = None,
                      expected_status: int = None) -> Dict[str, Any]:
        """Test a single endpoint scenario."""
        full_url = f"{self.base_url}{path}"

        try:
            if method.upper() == "GET":
                response = self.client.get(path, headers=headers)
            elif method.upper() == "POST":
                response = self.client.post(path, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = self.client.put(path, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = self.client.delete(path, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            # Parse response
            try:
                response_json = response.json()
            except:
                response_json = {"raw_content": response.text}

            # Determine status
            status = "✅ Success" if 200 <= response.status_code < 300 else "❌ Failed"
            if expected_status and response.status_code == expected_status:
                status = "✅ Expected"

            details = f"Status: {response.status_code}, Response: {str(response_json)[:100]}..."

            self.log_test(f"{method.upper()} {path}", scenario, status, details)

            return {
                "status_code": response.status_code,
                "response": response_json,
                "success": 200 <= response.status_code < 300
            }

        except Exception as e:
            self.log_test(f"{method.upper()} {path}", scenario, "❌ Error", f"Exception: {str(e)}")
            return {
                "status_code": 0,
                "response": {"error": str(e)},
                "success": False
            }

    def test_parental_dashboard_endpoints(self):
        """Test all Parental Dashboard endpoints."""
        print("\n🟢 TESTING PARENTAL DASHBOARD ENDPOINTS (9 endpoints)")
        print("=" * 60)

        # 1. POST /children - Create child profile
        self.test_endpoint("POST", "/children", "Valid input", {
            "name": "Test Child",
            "age": 8,
            "parent_email": "parent@example.com"
        })

        self.test_endpoint("POST", "/children", "Invalid input - missing fields", {
            "name": "Test Child"
        }, expected_status=422)

        self.test_endpoint("POST", "/children", "Invalid input - negative age", {
            "name": "Test Child",
            "age": -5,
            "parent_email": "parent@example.com"
        }, expected_status=422)

        # Use a test child ID for subsequent tests
        test_child_id = "test-child-123"

        # 2. GET /children/{child_id} - Get child details
        self.test_endpoint("GET", f"/children/{test_child_id}", "Valid child ID")
        self.test_endpoint("GET", "/children/nonexistent", "Non-existent child ID", expected_status=404)
        self.test_endpoint("GET", "/children/", "Empty child ID", expected_status=404)

        # 3. PUT /children/{child_id} - Update child profile
        self.test_endpoint("PUT", f"/children/{test_child_id}", "Valid update", {
            "name": "Updated Child",
            "age": 9
        })

        self.test_endpoint("PUT", f"/children/{test_child_id}", "Invalid update - bad data", {
            "age": "not_a_number"
        }, expected_status=422)

        # 4. DELETE /children/{child_id} - Delete child profile
        self.test_endpoint("DELETE", f"/children/{test_child_id}", "Valid deletion")
        self.test_endpoint("DELETE", "/children/nonexistent", "Non-existent child", expected_status=404)

        # 5. POST /children/{child_id}/story - Generate story
        self.test_endpoint("POST", f"/children/{test_child_id}/story", "Valid story request", {
            "theme": "adventure",
            "length": "short"
        })

        self.test_endpoint("POST", f"/children/{test_child_id}/story", "Invalid story request", {
            "theme": "",
            "length": "invalid_length"
        }, expected_status=422)

        # 6. POST /children/{child_id}/consent/request - Request consent
        self.test_endpoint("POST", f"/children/{test_child_id}/consent/request", "Valid consent request", {
            "consent_type": "data_collection",
            "purpose": "personalized_content"
        })

        # 7. POST /children/{child_id}/consent/grant - Grant consent
        self.test_endpoint("POST", f"/children/{test_child_id}/consent/grant", "Valid consent grant", {
            "consent_type": "data_collection",
            "granted": True
        })

        # 8. GET /children/{child_id}/consent/status - Check consent status
        self.test_endpoint("GET", f"/children/{test_child_id}/consent/status", "Valid consent check")
        self.test_endpoint("GET", "/children/invalid/consent/status", "Invalid child ID", expected_status=404)

        # 9. DELETE /children/{child_id}/consent/{consent_type} - Revoke consent
        self.test_endpoint("DELETE", f"/children/{test_child_id}/consent/data_collection", "Valid consent revocation")
        self.test_endpoint("DELETE", f"/children/{test_child_id}/consent/invalid_type", "Invalid consent type", expected_status=404)

    def test_chatgpt_endpoints(self):
        """Test all ChatGPT endpoints."""
        print("\n🟢 TESTING CHATGPT ENDPOINTS (2 endpoints)")
        print("=" * 60)

        # 1. GET /chatgpt/status - Service status check
        self.test_endpoint("GET", "/chatgpt/status", "Service status check")
        self.test_endpoint("GET", "/chatgpt/status?invalid=param", "With invalid parameters")

        # 2. POST /chatgpt/chat - Chat functionality
        self.test_endpoint("POST", "/chatgpt/chat", "Valid chat request", {
            "message": "Hello, tell me a story",
            "child_id": "test-child-123"
        })

        self.test_endpoint("POST", "/chatgpt/chat", "Empty message", {
            "message": "",
            "child_id": "test-child-123"
        }, expected_status=422)

        self.test_endpoint("POST", "/chatgpt/chat", "Missing child_id", {
            "message": "Hello"
        }, expected_status=422)

        self.test_endpoint("POST", "/chatgpt/chat", "Very long message", {
            "message": "x" * 5000,  # Very long message
            "child_id": "test-child-123"
        })

    def test_auth_endpoints(self):
        """Test all Auth endpoints."""
        print("\n🟢 TESTING AUTH ENDPOINTS (3 endpoints)")
        print("=" * 60)

        # 1. GET /auth/status - Authentication status
        self.test_endpoint("GET", "/auth/status", "Auth status check")

        # 2. POST /auth/login - User login
        self.test_endpoint("POST", "/auth/login", "Valid login", {
            "username": "testuser",
            "password": "testpass123"
        })

        self.test_endpoint("POST", "/auth/login", "Invalid credentials", {
            "username": "baduser",
            "password": "wrongpass"
        }, expected_status=401)

        self.test_endpoint("POST", "/auth/login", "Missing password", {
            "username": "testuser"
        }, expected_status=422)

        self.test_endpoint("POST", "/auth/login", "Empty credentials", {
            "username": "",
            "password": ""
        }, expected_status=422)

        self.test_endpoint("POST", "/auth/login", "SQL injection attempt", {
            "username": "'; DROP TABLE users; --",
            "password": "password"
        }, expected_status=422)

        # 3. POST /auth/logout - User logout
        self.test_endpoint("POST", "/auth/logout", "Valid logout", {
            "token": "fake-jwt-token"
        })

        self.test_endpoint("POST", "/auth/logout", "Missing token", {}, expected_status=422)

        self.test_endpoint("POST", "/auth/logout", "Invalid token", {
            "token": "invalid.jwt.token"
        }, expected_status=401)

    def generate_report(self):
        """Generate comprehensive test report."""
        print("\n" + "=" * 80)
        print("🎯 STEP 6: HTTP INTEGRATION TESTING RESULTS")
        print("=" * 80)

        # Summary statistics
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if "✅" in r["status"]])
        failed_tests = len([r for r in self.results if "❌" in r["status"]])

        print(f"\n📊 SUMMARY STATISTICS")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Successful: {successful_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   Success Rate: {(successful_tests / total_tests) * 100:.1f}%")

        # Detailed results table
        print(f"\n📋 DETAILED TEST RESULTS")
        print("-" * 80)
        print(f"{'Endpoint':<35} {'Scenario':<25} {'Status':<12} {'Details':<35}")
        print("-" * 80)

        for result in self.results:
            endpoint = result["endpoint"][:34]
            scenario = result["scenario"][:24]
            status = result["status"][:11]
            details = result["details"][:34] + "..." if len(result["details"]) > 37 else result["details"]

            print(f"{endpoint:<35} {scenario:<25} {status:<12} {details:<35}")

        # Group by endpoint for analysis
        print(f"\n🔍 ENDPOINT ANALYSIS")
        print("-" * 80)

        endpoints = {}
        for result in self.results:
            endpoint = result["endpoint"]
            if endpoint not in endpoints:
                endpoints[endpoint] = {"total": 0, "success": 0, "scenarios": []}
            endpoints[endpoint]["total"] += 1
            if "✅" in result["status"]:
                endpoints[endpoint]["success"] += 1
            endpoints[endpoint]["scenarios"].append(result["scenario"])

        for endpoint, stats in endpoints.items():
            success_rate = (stats["success"] / stats["total"]) * 100
            status_icon = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 50 else "❌"
            print(f"{status_icon} {endpoint}: {stats['success']}/{stats['total']} ({success_rate:.0f}%)")
            print(f"   Scenarios: {', '.join(stats['scenarios'][:3])}{'...' if len(stats['scenarios']) > 3 else ''}")

        # Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        print("-" * 80)

        critical_failures = [r for r in self.results if "❌" in r["status"] and "Error" in r["details"]]
        if critical_failures:
            print("🚨 CRITICAL ISSUES FOUND:")
            for failure in critical_failures:
                print(f"   • {failure['endpoint']}: {failure['details']}")

        validation_failures = [r for r in self.results if "422" in r["details"]]
        if not validation_failures:
            print("⚠️  NO INPUT VALIDATION: Many endpoints may lack proper validation")

        if successful_tests / total_tests >= 0.8:
            print("✅ PRODUCTION READINESS: Most endpoints working correctly")
        else:
            print("❌ NOT PRODUCTION READY: Significant issues need fixing")

        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": (successful_tests / total_tests) * 100,
            "results": self.results
        }

    def close(self):
        """Close the HTTP client."""
        self.client.close()


def main():
    """Main testing function."""
    print("🎯 STEP 6: HTTP INTEGRATION TESTING FOR FUNCTIONAL ENDPOINTS")
    print("Starting comprehensive testing of 14 functional endpoints...")
    print("=" * 80)

    tester = EndpointTester()

    try:
        # Test each router's endpoints
        tester.test_parental_dashboard_endpoints()
        tester.test_chatgpt_endpoints()
        tester.test_auth_endpoints()

        # Generate comprehensive report
        report = tester.generate_report()

        # Save results to file
        with open("step6_http_test_results.json", "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Full results saved to: step6_http_test_results.json")
        print("🏆 STEP 6 HTTP INTEGRATION TESTING COMPLETED")

    except Exception as e:
        print(f"❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        tester.close()


if __name__ == "__main__":
    main()
