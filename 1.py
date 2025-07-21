#!/usr/bin/env python3
"""
Smart Import Fixer for AI Teddy Bear v5
يصلح مسارات الاستيراد بناءً على التحليل
"""

import os
import re
from pathlib import Path
from collections import defaultdict

class SmartImportFixer:
    def __init__(self):
        self.import_fixes = {
            # DI Container fixes
            "from infrastructure.di.container import Container": 
                "from infrastructure.di.application_container import ApplicationContainer as Container",
            
            "from infrastructure.di.container import container":
                "from infrastructure.di.container import container",  # هذا صحيح بالفعل
            
            # Missing interfaces in read_model_interfaces
            "from application.interfaces.read_model_interfaces import IEventBus":
                "from domain.interfaces.event_bus_interface import IEventBus",
                
            "from application.interfaces.read_model_interfaces import IExternalAPIClient":
                "from domain.interfaces.external_service_interfaces import IExternalAPIClient",
                
            "from application.interfaces.read_model_interfaces import IConsentManager":
                "from application.interfaces.consent_manager import IConsentManager",
        }
        
        self.missing_exports = defaultdict(list)
        
    def analyze_init_files(self):
        """تحليل ملفات __init__.py للتأكد من الـ exports"""
        critical_inits = [
            'src/common/__init__.py',
            'src/domain/__init__.py',
            'src/infrastructure/di/__init__.py',
            'src/application/interfaces/__init__.py',
        ]
        
        results = {}
        for init_file in critical_inits:
            if Path(init_file).exists():
                with open(init_file, 'r') as f:
                    content = f.read()
                    
                # Check for __all__ exports
                has_all = '__all__' in content
                
                # Check for specific imports
                imports = re.findall(r'from .* import .*', content)
                
                results[init_file] = {
                    'has_all': has_all,
                    'imports': imports,
                    'is_empty': len(content.strip()) == 0
                }
        
        return results
    
    def suggest_init_fixes(self, init_analysis):
        """اقتراح إصلاحات لملفات __init__.py"""
        fixes = []
        
        # Fix for common/__init__.py
        if init_analysis.get('src/common/__init__.py', {}).get('is_empty'):
            fixes.append({
                'file': 'src/common/__init__.py',
                'content': '''"""Common module exports."""
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
'''
            })
        
        # Fix for domain/__init__.py
        if init_analysis.get('src/domain/__init__.py', {}).get('is_empty'):
            fixes.append({
                'file': 'src/domain/__init__.py',
                'content': '''"""Domain module exports."""
from .constants import *

__all__ = [
    # Domain constants
    'MAX_NEGATIVE_INDICATORS',
    'MAX_RESPONSE_LENGTH',
    'COPPA_AGE_THRESHOLD',
    'MINIMUM_CHILD_AGE',
    'COPPA_MAX_RETENTION_DAYS',
    'RATE_LIMIT_RETRY_AFTER_SECONDS',
]
'''
            })
            
        # Fix for infrastructure/di/__init__.py
        fixes.append({
            'file': 'src/infrastructure/di/__init__.py',
            'content': '''"""Dependency Injection exports."""
from .application_container import ApplicationContainer
from .container import container

# Legacy compatibility
Container = ApplicationContainer

__all__ = [
    'ApplicationContainer',
    'Container',  # Alias for backward compatibility
    'container',
]
'''
        })
        
        return fixes
    
    def analyze_interface_segregation(self):
        """تحليل مشكلة فصل الواجهات"""
        read_model_path = Path('src/application/interfaces/read_model_interfaces.py')
        
        if read_model_path.exists():
            with open(read_model_path, 'r') as f:
                content = f.read()
                
            # Extract all interface definitions
            interfaces = re.findall(r'class (I\w+).*?:', content)
            
            # Categorize interfaces
            read_interfaces = []
            write_interfaces = []
            
            for interface in interfaces:
                if any(word in interface.lower() for word in ['query', 'read', 'get', 'fetch']):
                    read_interfaces.append(interface)
                elif any(word in interface.lower() for word in ['command', 'write', 'update', 'delete', 'event', 'consent']):
                    write_interfaces.append(interface)
                else:
                    # Ambiguous - need manual review
                    write_interfaces.append(interface)
            
            return {
                'read_interfaces': read_interfaces,
                'write_interfaces': write_interfaces,
                'needs_refactoring': len(write_interfaces) > 0
            }
        
        return None
    
    def generate_fix_script(self):
        """توليد سكريبت bash للإصلاحات"""
        init_analysis = self.analyze_init_files()
        init_fixes = self.suggest_init_fixes(init_analysis)
        interface_analysis = self.analyze_interface_segregation()
        
        script = '''#!/bin/bash
# AI Teddy Bear v5 - Import Fix Script
# Generated automatically based on analysis

set -e  # Exit on error

echo "🔧 Starting import fixes..."

# 1. Fix __init__.py files
echo "📝 Fixing __init__.py exports..."
'''
        
        for fix in init_fixes:
            script += f'''
cat > {fix['file']} << 'EOF'
{fix['content']}
EOF
'''
        
        # 2. Add missing constants if needed
        script += '''
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
'''
        
        # 3. Create missing interface files
        if interface_analysis and interface_analysis['needs_refactoring']:
            script += '''
# 3. Create command interfaces file if needed
echo "🔀 Separating read/write interfaces..."

if [ ! -f src/application/interfaces/command_interfaces.py ]; then
    cat > src/application/interfaces/command_interfaces.py << 'EOF'
"""Command/Write interfaces - separated from read interfaces."""
from abc import ABC, abstractmethod
from typing import Optional

class IEventBus(ABC):
    """Event bus for domain events."""
    @abstractmethod
    async def publish(self, event): pass

class IConsentManager(ABC):
    """Consent management interface."""
    @abstractmethod
    async def check_consent(self, child_id: str) -> bool: pass
    
class IExternalAPIClient(ABC):
    """External API client interface."""
    @abstractmethod
    async def call_api(self, endpoint: str, data: dict) -> dict: pass
EOF
fi
'''
        
        script += '''
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
'''
        
        return script

if __name__ == "__main__":
    fixer = SmartImportFixer()
    
    # Generate fix script
    fix_script = fixer.generate_fix_script()
    
    with open('fix_imports.sh', 'w') as f:
        f.write(fix_script)
    
    os.chmod('fix_imports.sh', 0o755)
    
    print("✅ Fix script generated: fix_imports.sh")
    print("🏃 Run: ./fix_imports.sh")
    
    # Also generate detailed analysis
    analysis = {
        'init_files': fixer.analyze_init_files(),
        'interfaces': fixer.analyze_interface_segregation()
    }
    
    import json
    with open('import_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print("📊 Detailed analysis saved: import_analysis.json")