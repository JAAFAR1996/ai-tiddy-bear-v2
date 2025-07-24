#!/usr/bin/env python3
"""Security verification script for AI Teddy Bear project."""

import os
import sys
from pathlib import Path

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment only")

print("🔍 Security Verification Check\n")

# Check 1: Environment variables
print("📋 Checking required environment variables...")
env_vars = ["SECRET_KEY", "JWT_SECRET_KEY", "COPPA_ENCRYPTION_KEY"]
missing = [var for var in env_vars if not os.getenv(var)]

if missing:
    print(f"❌ Missing environment variables: {missing}")
    print("💡 Please create .env file with required variables")
    print("📄 Use .env.example as a template")
    print("🔑 Generate secure keys with: python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
    sys.exit(1)
else:
    print("✅ All security environment variables present")

# Check 2: Validate key lengths
print("\n🔐 Validating security key lengths...")
secret_key = os.getenv("SECRET_KEY", "")
jwt_secret_key = os.getenv("JWT_SECRET_KEY", "")
coppa_key = os.getenv("COPPA_ENCRYPTION_KEY", "")

validation_errors = []

if len(secret_key) < 32:
    validation_errors.append(f"SECRET_KEY too short ({len(secret_key)} chars, minimum 32)")

if len(jwt_secret_key) < 32:
    validation_errors.append(f"JWT_SECRET_KEY too short ({len(jwt_secret_key)} chars, minimum 32)")

if len(coppa_key) < 44:
    validation_errors.append(f"COPPA_ENCRYPTION_KEY too short ({len(coppa_key)} chars, minimum 44)")

if validation_errors:
    print("❌ Key length validation failed:")
    for error in validation_errors:
        print(f"   • {error}")
    sys.exit(1)
else:
    print("✅ All security keys meet minimum length requirements")

# Check 3: No hardcoded secrets in settings file
print("\n🔍 Scanning for hardcoded secrets...")
settings_file = Path("src/infrastructure/config/security/security_settings.py")

if not settings_file.exists():
    print(f"❌ Settings file not found: {settings_file}")
    sys.exit(1)

with open(settings_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Check for dangerous patterns (excluding validation code)
dangerous_patterns = [
    "DEVELOPMENT_SECRET_KEY",
    "DEVELOPMENT_JWT_SECRET", 
    "DEVELOPMENT_COPPA_KEY",
    "dev-secret-key",
    "jwt-dev-secret",
    "dev-db-encryption",
    "123456789"
]

# Don't flag patterns in validation/check code
validation_context_lines = [
    "dev_indicators",
    "dangerous_patterns", 
    "Found hardcoded",
    "appears to contain development"
]

found_patterns = []
lines = content.split('\n')
for i, line in enumerate(lines):
    for pattern in dangerous_patterns:
        if pattern in line:
            # Check if this is in validation context
            is_validation_context = any(
                ctx in line or 
                (i > 0 and ctx in lines[i-1]) or 
                (i < len(lines)-1 and ctx in lines[i+1])
                for ctx in validation_context_lines
            )
            if not is_validation_context:
                found_patterns.append(pattern)
if found_patterns:
    print(f"❌ Found hardcoded development secrets: {found_patterns}")
    print("⚠️  These must be removed from production code!")
    sys.exit(1)
else:
    print("✅ No hardcoded development secrets found")

# Check 4: Validate development key indicators
print("\n🔒 Validating production-ready keys...")
dev_indicators = [
    "DEVELOPMENT",
    "DEV",
    "TEST", 
    "CHANGE_IN_PRODUCTION",
    "123456",
    "example",
    "placeholder"
]

for key_name, key_value in [
    ("SECRET_KEY", secret_key),
    ("JWT_SECRET_KEY", jwt_secret_key), 
    ("COPPA_ENCRYPTION_KEY", coppa_key)
]:
    if any(indicator.upper() in key_value.upper() for indicator in dev_indicators):
        print(f"⚠️  Warning: {key_name} appears to contain placeholder values")
        print(f"   Value preview: {key_value[:10]}...")
        print(f"   Please ensure this is a secure production key")
    else:
        print(f"✅ {key_name} appears to be production-ready")

print("\n✅ Security verification PASSED!")
print("🎉 All critical security checks completed successfully!")
print("\n📝 Next steps:")
print("   1. Ensure .env file is never committed to version control")
print("   2. Use different keys for different environments")
print("   3. Rotate keys regularly in production")
print("   4. Monitor for any security alerts")
