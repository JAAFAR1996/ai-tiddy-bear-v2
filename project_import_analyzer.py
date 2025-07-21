#!/usr/bin/env python3
"""
Deep Import Analysis for AI Teddy Bear v5
يحلل المشاكل الهيكلية ويقترح حلول محددة
"""

import os
import ast
import re
from pathlib import Path
from collections import defaultdict
import json
from datetime import datetime

class DeepImportAnalyzer:
    def __init__(self):
        self.broken_imports = self._parse_broken_imports()
        self.existing_files = {}
        self.missing_definitions = defaultdict(list)
        
    def _parse_broken_imports(self):
        """Parse the 86 broken imports from paste.txt"""
        imports = []
        with open('paste.txt', 'r') as f:
            for line in f:
                match = re.match(r"(.*?):(\d+): '(.+?)' NOT FOUND in module '(.+?)'", line)
                if match:
                    imports.append({
                        'file': match.group(1),
                        'line': int(match.group(2)),
                        'symbol': match.group(3),
                        'module': match.group(4)
                    })
        return imports
    
    def analyze_di_container_issue(self):
        """تحليل مشكلة DI Container بالتفصيل"""
        # فحص ملف container.py
        container_path = Path('src/infrastructure/di/container.py')
        if container_path.exists():
            with open(container_path, 'r') as f:
                content = f.read()
                # هل يحتوي على Container class؟
                has_class = 'class Container' in content
                # هل يحتوي على container instance؟
                has_instance = 'container =' in content
                
                return {
                    'file_exists': True,
                    'has_Container_class': has_class,
                    'has_container_instance': has_instance,
                    'exports': self._extract_exports(content)
                }
        return {'file_exists': False}
    
    def analyze_constants_issue(self):
        """تحليل مشكلة الثوابت المفقودة"""
        missing_constants = defaultdict(list)
        
        for imp in self.broken_imports:
            if imp['module'].endswith('constants'):
                missing_constants[imp['module']].append(imp['symbol'])
        
        # فحص الثوابت الموجودة
        existing_constants = {}
        for const_file in ['src/common/constants.py', 'src/domain/constants.py']:
            if Path(const_file).exists():
                with open(const_file, 'r') as f:
                    content = f.read()
                    # استخراج كل الثوابت المعرفة
                    constants = re.findall(r'^([A-Z_]+)\s*=', content, re.MULTILINE)
                    existing_constants[const_file] = constants
        
        return {
            'missing': dict(missing_constants),
            'existing': existing_constants
        }
    
    def analyze_interfaces_issue(self):
        """تحليل مشكلة الواجهات"""
        interface_problems = []
        
        # فحص read_model_interfaces.py
        read_model_path = Path('src/application/interfaces/read_model_interfaces.py')
        if read_model_path.exists():
            with open(read_model_path, 'r') as f:
                content = f.read()
                # البحث عن interfaces التي لا تنتمي لـ read model
                write_interfaces = re.findall(r'class I(\w+).*?:', content)
                interface_problems.extend([
                    f"Potential write interface in read model: I{name}"
                    for name in write_interfaces
                    if any(keyword in name.lower() for keyword in ['write', 'command', 'event', 'consent'])
                ])
        
        return interface_problems
    
    def analyze_security_modules(self):
        """تحليل وحدات الأمان المفقودة"""
        required_security_modules = [
            'infrastructure/security/validation/sql_injection_protection.py',
            'infrastructure/validators/security/coppa_validator.py',
            'infrastructure/validators/security/path_validator.py',
            'infrastructure/validators/security/database_input_validator.py'
        ]
        
        missing_modules = []
        for module in required_security_modules:
            if not Path(f'src/{module}').exists():
                missing_modules.append(module)
        
        return missing_modules
    
    def _extract_exports(self, content):
        """استخراج الـ exports من ملف"""
        exports = []
        # __all__ exports
        all_match = re.search(r'__all__\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if all_match:
            exports = re.findall(r'["\'](\w+)["\']', all_match.group(1))
        return exports
    
    def generate_solutions(self):
        """توليد حلول محددة"""
        di_analysis = self.analyze_di_container_issue()
        constants_analysis = self.analyze_constants_issue()
        interface_problems = self.analyze_interfaces_issue()
        missing_security = self.analyze_security_modules()
        
        solutions = {
            'immediate_fixes': [],
            'architectural_fixes': [],
            'cli_commands': []
        }
        
        # حلول DI Container
        if di_analysis.get('file_exists'):
            if not di_analysis.get('has_container_instance'):
                solutions['immediate_fixes'].append({
                    'issue': 'DI Container instance missing',
                    'fix': 'Add "container = Container()" at module level in container.py',
                    'file': 'src/infrastructure/di/container.py'
                })
        
        # حلول الثوابت
        for module, constants in constants_analysis['missing'].items():
            solutions['immediate_fixes'].append({
                'issue': f'Missing constants in {module}',
                'fix': f'Add these constants: {", ".join(constants)}',
                'file': f'src/{module.replace(".", "/")}.py'
            })
        
        # حلول الواجهات
        if interface_problems:
            solutions['architectural_fixes'].append({
                'issue': 'Interface Segregation Violation',
                'fix': 'Move write interfaces from read_model_interfaces.py to command_interfaces.py',
                'interfaces': interface_problems
            })
        
        # حلول الأمان
        if missing_security:
            solutions['immediate_fixes'].append({
                'issue': 'Critical security modules missing',
                'fix': 'Create security validation modules',
                'modules': missing_security
            })
        
        return solutions

if __name__ == "__main__":
    analyzer = DeepImportAnalyzer()
    
    # تحليل شامل
    di_issue = analyzer.analyze_di_container_issue()
    constants_issue = analyzer.analyze_constants_issue()
    interfaces_issue = analyzer.analyze_interfaces_issue()
    security_issue = analyzer.analyze_security_modules()
    solutions = analyzer.generate_solutions()
    
    # توليد تقرير MD محدث
    report = f"""# AI Teddy Bear v5 - تقرير التحليل العميق
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## التشخيص النهائي

### 1. مشكلة DI Container
- الملف موجود: {di_issue.get('file_exists', False)}
- يحتوي على Container class: {di_issue.get('has_Container_class', False)}
- يحتوي على container instance: {di_issue.get('has_container_instance', False)}

### 2. الثوابت المفقودة
{json.dumps(constants_issue['missing'], indent=2)}

### 3. انتهاكات الواجهات
{chr(10).join(interfaces_issue)}

### 4. وحدات الأمان المفقودة
{chr(10).join(security_issue)}

## الحلول المقترحة

### حلول فورية (للتشغيل السريع)
{json.dumps(solutions['immediate_fixes'], indent=2)}

### حلول هيكلية (للاستدامة)
{json.dumps(solutions['architectural_fixes'], indent=2)}
"""
    
    with open('deep_analysis_report.md', 'w') as f:
        f.write(report)
    
    print("✅ التقرير المفصل جاهز: deep_analysis_report.md")