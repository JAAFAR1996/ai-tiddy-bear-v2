#!/usr/bin/env python3
"""
Interface Finder - يجد الواجهات الفعلية ويحدد المسارات الصحيحة
"""

import os
import re
from pathlib import Path
from collections import defaultdict

class InterfaceFinder:
    def __init__(self):
        self.interfaces_map = {}
        self.usage_map = defaultdict(list)
        
    def find_all_interfaces(self):
        """البحث عن كل الواجهات في المشروع"""
        for py_file in Path('src').rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # البحث عن تعريفات الواجهات
                interface_matches = re.findall(
                    r'class\s+(I[A-Z]\w*)\s*(?:\([^)]+\))?\s*:',
                    content
                )
                
                for interface in interface_matches:
                    module_path = str(py_file.relative_to('src')).replace('/', '.').replace('.py', '')
                    self.interfaces_map[interface] = {
                        'file': str(py_file),
                        'module': module_path
                    }
                    
                # البحث عن استخدامات الواجهات
                for interface in ['IEventBus', 'IExternalAPIClient', 'IConsentManager']:
                    if interface in content and 'NOT FOUND' not in content:
                        self.usage_map[interface].append(str(py_file))
                        
            except Exception as e:
                pass
                
    def analyze_missing_interfaces(self):
        """تحليل الواجهات المفقودة"""
        missing = ['IEventBus', 'IExternalAPIClient', 'IConsentManager']
        results = {}
        
        for interface in missing:
            if interface in self.interfaces_map:
                results[interface] = {
                    'status': 'FOUND',
                    'location': self.interfaces_map[interface],
                    'correct_import': f"from {self.interfaces_map[interface]['module']} import {interface}"
                }
            else:
                # ربما بأسماء مختلفة؟
                similar = [name for name in self.interfaces_map.keys() 
                          if interface[1:].lower() in name.lower()]
                results[interface] = {
                    'status': 'NOT_FOUND',
                    'similar': similar,
                    'used_in': self.usage_map.get(interface, [])
                }
                
        return results
    
    def suggest_fixes(self, analysis):
        """اقتراح إصلاحات غير ترقيعية"""
        fixes = []
        
        for interface, data in analysis.items():
            if data['status'] == 'FOUND':
                # الواجهة موجودة - فقط نحتاج تصحيح المسار
                fixes.append({
                    'type': 'UPDATE_IMPORT',
                    'interface': interface,
                    'from': f"from application.interfaces.read_model_interfaces import {interface}",
                    'to': data['correct_import']
                })
            else:
                # الواجهة غير موجودة
                if data['similar']:
                    fixes.append({
                        'type': 'POSSIBLE_RENAME',
                        'interface': interface,
                        'similar_found': data['similar'],
                        'action': 'Check if one of these is the correct interface'
                    })
                else:
                    fixes.append({
                        'type': 'MISSING_INTERFACE',
                        'interface': interface,
                        'used_in': data['used_in'],
                        'action': 'Interface needs to be properly designed and implemented'
                    })
                    
        return fixes

if __name__ == "__main__":
    finder = InterfaceFinder()
    finder.find_all_interfaces()
    
    print("🔍 البحث عن الواجهات...")
    analysis = finder.analyze_missing_interfaces()
    
    print("\n📊 نتائج التحليل:")
    for interface, data in analysis.items():
        print(f"\n{interface}:")
        print(f"  Status: {data['status']}")
        if data['status'] == 'FOUND':
            print(f"  Location: {data['location']['file']}")
            print(f"  Correct import: {data['correct_import']}")
        else:
            if data['similar']:
                print(f"  Similar interfaces found: {', '.join(data['similar'])}")
            if data['used_in']:
                print(f"  Used in {len(data['used_in'])} files")
    
    print("\n💡 الحلول المقترحة:")
    fixes = finder.suggest_fixes(analysis)
    for i, fix in enumerate(fixes, 1):
        print(f"\n{i}. {fix['type']}:")
        if fix['type'] == 'UPDATE_IMPORT':
            print(f"   Replace: {fix['from']}")
            print(f"   With: {fix['to']}")
        else:
            print(f"   Interface: {fix['interface']}")
            print(f"   Action: {fix['action']}")
