"""Security Testing Module for AI Teddy Bear

This module provides comprehensive security testing capabilities.
"""
from .security_tests.authentication_tests import AuthenticationTester
from .security_tests.compliance_tests import ComplianceTester
from .security_tests.encryption_tests import EncryptionTester
from .security_tests.injection_tests import InjectionTester
from .security_tests.security_tester import SecurityTester

# Re-export main classes for backward compatibility
__all__ = [
    "SecurityTester",
    "InjectionTester",
    "AuthenticationTester",
    "EncryptionTester",
    "ComplianceTester"
]

# Main entry point for security testing
def run_security_tests(base_path: str = ".") -> dict:
    """Run all security tests and return results"""
    tester = SecurityTester(base_path)
    return tester.run_all_security_tests()

def generate_security_report(base_path: str = ".") -> str:
    """Generate comprehensive security report"""
    tester = SecurityTester(base_path)
    return tester.generate_security_report()