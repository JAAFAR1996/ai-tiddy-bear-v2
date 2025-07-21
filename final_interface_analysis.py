#!/usr/bin/env python3
"""
Final Interface Analysis - تحليل نهائي للواجهات المفقودة
"""

import ast
from pathlib import Path

def analyze_interface_usage(interface_name):
    """تحليل كيفية استخدام واجهة معينة"""
    usage_patterns = []
    
    # الملفات التي تستخدم الواجهة
    files_map = {
        'IExternalAPIClient': ['src/application/services/content/dynamic_content_service.py'],
        'IConsentManager': ['src/application/use_cases/generate_ai_response.py']
    }
    
    if interface_name in files_map:
        for file_path in files_map[interface_name]:
            if Path(file_path).exists():
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        # البحث عن استخدام الواجهة في type hints
                        if isinstance(node, ast.FunctionDef):
                            for arg in node.args.args:
                                if arg.annotation:
                                    annotation_str = ast.unparse(arg.annotation)
                                    if interface_name in annotation_str:
                                        usage_patterns.append({
                                            'file': file_path,
                                            'function': node.name,
                                            'parameter': arg.arg,
                                            'type': 'parameter_type'
                                        })
                                        
                        # البحث عن استدعاءات
                        if isinstance(node, ast.Call):
                            if hasattr(node.func, 'attr'):
                                call_str = ast.unparse(node)
                                if any(param in call_str for param in ['api_client', 'consent_manager']):
                                    usage_patterns.append({
                                        'file': file_path,
                                        'call': call_str[:100],
                                        'type': 'method_call'
                                    })
                except:
                    pass
                    
    return usage_patterns

if __name__ == "__main__":
    missing_interfaces = ['IExternalAPIClient', 'IConsentManager']
    
    print("🔍 تحليل استخدام الواجهات المفقودة...")
    
    for interface in missing_interfaces:
        print(f"\n{interface}:")
        usage = analyze_interface_usage(interface)
        
        if usage:
            print(f"  مستخدمة في {len(usage)} موضع")
            for u in usage:
                print(f"  - {u}")
        else:
            print("  لا توجد استخدامات")
            
    print("\n💡 التوصية النهائية:")
    print("بناءً على التحليل، يجب:")
    print("1. تصميم وتنفيذ الواجهات المفقودة في infrastructure_services.py")
    print("2. أو إزالة استخدامها إذا لم تعد مطلوبة")
    print("3. أو استبدالها بواجهات موجودة إذا كان هناك بدائل")
