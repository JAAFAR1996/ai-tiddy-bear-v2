"""Main Security Tester Class"""
from datetime import datetime
from typing import Dict, Any
import logging
from .authentication_tests import AuthenticationTester
from .compliance_tests import ComplianceTester
from .encryption_tests import EncryptionTester
from .injection_tests import InjectionTester
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")

class SecurityTester:
    """Main security testing orchestrator"""

    def __init__(self, base_path: str = ".") -> None:
        self.base_path = base_path
        self.injection_tester = InjectionTester(base_path)
        self.auth_tester = AuthenticationTester(base_path)
        self.encryption_tester = EncryptionTester(base_path)
        self.compliance_tester = ComplianceTester(base_path)

    def run_all_security_tests(self) -> Dict[str, Any]:
        """Run all security tests"""
        logger.info("🔒 Starting comprehensive security tests...")
        results = {
            "test_date": datetime.now().isoformat(),
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_results": []
        }

        # Define all tests
        tests = [
            ("Code Injection", self.injection_tester.test_code_injection),
            ("SQL Injection", self.injection_tester.test_sql_injection),
            ("XSS Vulnerabilities", self.injection_tester.test_xss_vulnerabilities),
            ("Path Traversal", self.injection_tester.test_path_traversal),
            ("Authentication", self.auth_tester.test_authentication),
            ("Input Validation", self.auth_tester.test_input_validation),
            ("Rate Limiting", self.auth_tester.test_rate_limiting),
            ("Encryption", self.encryption_tester.test_encryption),
            ("Secrets Exposure", self.encryption_tester.test_secrets_exposure),
            ("COPPA Compliance", self.compliance_tester.test_coppa_compliance),
            ("GDPR Compliance", self.compliance_tester.test_gdpr_compliance),
        ]

        for name, test_func in tests:
            logger.info(f"Running test: {name}")
            result = test_func()
            results["total_tests"] += 1
            if result["passed"]:
                results["passed_tests"] += 1
            else:
                results["failed_tests"] += 1
            results["test_results"].append({"test_name": name, "result": result})

        logger.info("✅ Security tests completed.")
        return results

    def generate_security_report(self) -> str:
        """Generate a comprehensive security report"""
        results = self.run_all_security_tests()
        report = f"""# Security Report

**Date:** {results['test_date']}

**Summary:**
- **Total Tests:** {results['total_tests']}
- **Passed:** {results['passed_tests']}
- **Failed:** {results['failed_tests']}

---

"""

        for test_result in results["test_results"]:
            name = test_result["test_name"]
            result = test_result["result"]
            status = "✅ PASSED" if result["passed"] else "❌ FAILED"
            report += f"## {name}: {status}\n\n"
            if not result["passed"]:
                report += "**Issues Found:**\n"
                for issue in result["issues"]:
                    report += f"- {issue}\n"
                report += "\n"

            report += "**Recommendations:**\n"
            for rec in result["recommendations"]:
                report += f"- {rec}\n"
            report += "\n---\n"

        return report