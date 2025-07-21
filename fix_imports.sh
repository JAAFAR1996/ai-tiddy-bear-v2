#!/bin/bash
# AI Teddy Bear v5 - Import Fix Script
# Generated automatically based on analysis

set -e  # Exit on error

echo "🔧 Starting import fixes..."

# 1. Fix __init__.py files
echo "📝 Fixing __init__.py exports..."

cat > src/common/__init__.py << 'EOF'
"""Common module exports."""
from .constants import *

__all__ = [
    # Re-export all constants
    'API_PREFIX_AUTH',
    'API_PREFIX_CHATGPT', 
    'API_PREFIX_DASHBOARD',
    'API_PREFIX_ESP32',
    'API_PREFIX_HEALTH',
    'API_TAG_AUTH',
    'API_TAG_CHATGPT',
    'API_TAG_DASHBOARD',
    'API_TAG_ESP32',
    'API_TAG_HEALTH',
    'OPENAPI_TITLE',
    'OPENAPI_VERSION',
    'OPENAPI_DESCRIPTION',
    'OPENAPI_SERVERS',
    'OPENAPI_TAGS',
    'OPENAPI_EXTERNAL_DOCS',
    'OPENAPI_LICENSE_INFO',
    'OPENAPI_CONTACT_INFO',
    'OPENAPI_COMMON_RESPONSES',
    'OPENAPI_BEARER_DESCRIPTION',
    'SENSITIVE_LOG_INTERACTION_KEYS',
]

EOF

cat > src/infrastructure/di/__init__.py << 'EOF'
"""Dependency Injection exports."""
from .application_container import ApplicationContainer
from .container import container

# Legacy compatibility
Container = ApplicationContainer

__all__ = [
    'ApplicationContainer',
    'Container',  # Alias for backward compatibility
    'container',
]

EOF

# 2. Ensure all constants are defined
echo "📊 Checking constants..."

# Add any missing constants to common/constants.py
if ! grep -q "SENSITIVE_LOG_INTERACTION_KEYS" src/common/constants.py; then
    echo "SENSITIVE_LOG_INTERACTION_KEYS = ['password', 'token', 'secret', 'auth']" >> src/common/constants.py
fi

# Add any missing constants to domain/constants.py  
if ! grep -q "MAX_NEGATIVE_INDICATORS" src/domain/constants.py; then
    echo "MAX_NEGATIVE_INDICATORS = 3" >> src/domain/constants.py
fi

if ! grep -q "MAX_RESPONSE_LENGTH" src/domain/constants.py; then
    echo "MAX_RESPONSE_LENGTH = 500" >> src/domain/constants.py
fi

if ! grep -q "MINIMUM_CHILD_AGE" src/domain/constants.py; then
    echo "MINIMUM_CHILD_AGE = 3" >> src/domain/constants.py
fi

# 4. Fix imports in affected files
echo "🔄 Updating import statements..."

# This would need to be done file by file based on the errors
# For now, we'll create a mapping file for manual updates

cat > import_fixes.txt << 'EOF'
# Import fixes needed:
# Replace these imports in the specified files:

# In files importing IEventBus, IConsentManager, IExternalAPIClient:
# OLD: from application.interfaces.read_model_interfaces import IEventBus
# NEW: from application.interfaces.command_interfaces import IEventBus

# In files importing Container:
# OLD: from infrastructure.di.container import Container  
# NEW: from infrastructure.di.container import ApplicationContainer as Container
EOF

echo "✅ Fix script completed!"
echo "⚠️  Please review import_fixes.txt for manual import updates needed"
