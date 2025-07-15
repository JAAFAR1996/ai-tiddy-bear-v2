#!/usr/bin/env python3
"""
Security Hardening Tool for AI Teddy Bear
Simplified version of security_hardening.py with modular architecture
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from infrastructure.security.hardening import (
    SecurityVulnerabilityFixer,
    SecureEnvironmentConfig,
    get_secure_settings,
    get_coppa_compliance,
    run_security_tests
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point for security hardening"""
    
    print("🔒 AI Teddy Bear - Security Hardening Tool")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Step 1: Fix security vulnerabilities
        print("\n🚨 Step 1: Fixing Security Vulnerabilities...")
        vulnerability_fixer = SecurityVulnerabilityFixer()
        vulnerability_fixer.fix_all_vulnerabilities()
        
        # Step 2: Create secure environment configuration
        print("\n🔧 Step 2: Creating Secure Environment Configuration...")
        env_config = SecureEnvironmentConfig()
        env_config.create_secure_env_template()
        
        # Step 3: Validate current settings
        print("\n✅ Step 3: Validating Security Settings...")
        validation_result = env_config.validate_environment()
        
        if validation_result["valid"]:
            print("✅ Environment validation passed")
        else:
            print("❌ Environment validation failed:")
            for error in validation_result["errors"]:
                print(f"  - {error}")
        
        # Step 4: Check COPPA compliance
        print("\n👶 Step 4: Checking COPPA Compliance...")
        coppa = get_coppa_compliance()
        audit_result = coppa.audit_compliance()
        print(f"✅ COPPA compliance status: {audit_result['compliance_status']}")
        
        # Step 5: Run security tests
        print("\n🔍 Step 5: Running Security Tests...")
        test_results = run_security_tests()
        print(f"✅ Security tests completed. Pass rate: {test_results['pass_rate']:.1f}%")
        
        # Step 6: Generate security keys
        print("\n🔑 Step 6: Generating Secure Keys...")
        secure_keys = env_config.generate_secure_keys()
        print("✅ Secure keys generated (save these to your .env file)")
        
        # Summary
        print("\n📋 Security Hardening Summary:")
        print(f"• Fixed vulnerabilities in {len(vulnerability_fixer.fixed_files)} files")
        print(f"• Environment validation: {'✅ PASSED' if validation_result['valid'] else '❌ FAILED'}")
        print(f"• COPPA compliance: ✅ {audit_result['compliance_status'].upper()}")
        print(f"• Security tests: {test_results['passed_tests']}/{test_results['total_tests']} passed")
        print("• Secure environment template created")
        print("• New secure keys generated")
        
        # Recommendations
        print("\n🚀 Next Steps:")
        print("1. Review and update .env file with secure values")
        print("2. Address any failed security tests")
        print("3. Implement recommended security measures")
        print("4. Run regular security audits")
        print("5. Monitor for new vulnerabilities")
        
        # Generate reports
        print("\n📊 Generating Security Reports...")
        
        # Vulnerability report
        vuln_report = vulnerability_fixer.generate_security_report()
        with open("SECURITY_VULNERABILITY_REPORT.md", 'w') as f:
            f.write(vuln_report)
        
        # Test report
        from infrastructure.security.hardening.security_tests import SecurityTester
        tester = SecurityTester()
        test_report = tester.generate_security_report(test_results)
        with open("SECURITY_TEST_REPORT.md", 'w') as f:
            f.write(test_report)
        
        print("✅ Security reports generated:")
        print("  - SECURITY_VULNERABILITY_REPORT.md")
        print("  - SECURITY_TEST_REPORT.md")
        
        print("\n🎯 Security hardening completed successfully!")
        
    except Exception as e:
        logger.error(f"Security hardening failed: {e}")
        print(f"\n❌ Security hardening failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())