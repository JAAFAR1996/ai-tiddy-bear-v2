#!/usr/bin/env python3
import os
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

REPORT = []
SEP = "\n---\n"
EXCLUDES = [".venv", "venv", "__pycache__", "build", "dist", ".mypy_cache", "node_modules", ".git"]

# إضافة ملف تكوين لتخصيص الفحوصات
CONFIG = {
    "basic_checks": True,
    "security_checks": True,
    "quality_checks": True,
    "documentation_checks": True,
    "advanced_checks": True,
    "ai_specific_checks": True,  # للمشاريع التي تستخدم AI
}

def check_tool_installed(tool_name):
    """فحص ما إذا كانت الأداة مثبتة"""
    try:
        subprocess.run([tool_name, "--version"], 
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def exclude_dirs_find():
    return " ".join([f"-not -path './{d}/*'" for d in EXCLUDES])

def exclude_dirs_grep():
    return " ".join([f"--exclude-dir={d}" for d in EXCLUDES])

def exclude_dirs_tool(option):
    return " ".join([f"{option} {d}" for d in EXCLUDES])

def run(cmd, desc, required_tool=None, config_key=None):
    """تشغيل أمر مع فحص التبعيات والتكوين"""
    
    # فحص إعدادات التكوين
    if config_key and not CONFIG.get(config_key, True):
        print(f"⏭️ تم تخطي: {desc} (معطل في التكوين)")
        return
    
    # فحص الأدوات المطلوبة
    if required_tool and not check_tool_installed(required_tool):
        print(f"⚠️ تم تخطي: {desc} - الأداة {required_tool} غير مثبتة")
        REPORT.append(f"## {desc}\n⚠️ **تم التخطي:** الأداة `{required_tool}` غير مثبتة\n{SEP}")
        return
    
    print(f"\n🔹 بدأ: {desc}")
    REPORT.append(f"## {desc}\n```bash\n{cmd}\n```\n")
    start = time.time()
    
    try:
        out = subprocess.check_output(
            cmd, shell=True, text=True, stderr=subprocess.STDOUT, 
            encoding="utf-8", errors="replace", timeout=300  # timeout 5 دقائق
        )
        elapsed = time.time() - start
        print(f"✅ انتهى: {desc} (استغرق: {elapsed:.2f} ثانية)")
        
        # تحليل النتائج وإضافة ملخص
        result_summary = analyze_output(out, desc)
        REPORT.append(f"```\n{out or '_No results._'}\n```\n")
        if result_summary:
            REPORT.append(f"**ملخص النتائج:** {result_summary}\n")
        REPORT.append(f"⏱️ الوقت المستغرق: {elapsed:.2f} ثانية\n")
        
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        print(f"⏱️ انتهت مهلة {desc} (أكثر من 5 دقائق)")
        REPORT.append(f"_انتهت المهلة الزمنية._\n")
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start
        print(f"❌ خطأ في {desc}: {e} (استغرق: {elapsed:.2f} ثانية)")
        REPORT.append(f"_Error or No results._\n```\n{e.output}\n```\n")
    
    REPORT.append(f"⏱️ الوقت المستغرق: {elapsed:.2f} ثانية\n")
    REPORT.append(SEP)

def analyze_output(output, check_type):
    """تحليل مخرجات الأوامر وإعطاء ملخص"""
    if not output.strip():
        return "لا توجد مشاكل"
    
    lines = output.strip().split('\n')
    count = len(lines)
    
    if "مكرر" in check_type:
        return f"تم العثور على {count} عنصر مكرر"
    elif "أمان" in check_type or "Security" in check_type:
        return f"تم العثور على {count} مشكلة أمنية محتملة"
    elif "TODO" in check_type:
        return f"تم العثور على {count} مهمة غير مكتملة"
    else:
        return f"تم العثور على {count} نتيجة"

def create_summary_report():
    """إنشاء تقرير ملخص بالمشاكل الرئيسية"""
    summary = ["# 📊 ملخص تقرير الفحص\n"]
    
    # يمكن تطوير هذا ليحلل النتائج ويعطي أولويات
    summary.append("## الأولويات العالية ⚠️")
    summary.append("- مشاكل الأمان")
    summary.append("- الكود الميت")
    summary.append("- التكرار الزائد\n")
    
    summary.append("## الأولويات المتوسطة 📋")
    summary.append("- جودة التوثيق")
    summary.append("- تنسيق الكود")
    summary.append("- تعقيد الشفرة\n")
    
    return '\n'.join(summary)

def main():
    global_start = time.time()
    start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # إنشاء header للتقرير
    REPORT.append(f"# 🚨 تقرير تدقيق المشروع AI Teddy Bear v5 — {start}\n")
    REPORT.append(f"**مسار المشروع:** `{os.getcwd()}`\n")
    REPORT.append(f"**نظام التشغيل:** `{os.name}`\n{SEP}")

    print("🧸 بدء فحص مشروع AI Teddy Bear v5...")

    # الفحوصات الأساسية
    if CONFIG.get("basic_checks", True):
        print("\n📋 الفحوصات الأساسية...")
        
        run(f"grep -rh --include='*.py' {exclude_dirs_grep()} '^class ' src | awk '{{print $2}}' | sort | uniq -d",
            "الكلاسات المكررة", config_key="basic_checks")
        
        run(f"grep -rh --include='*.py' {exclude_dirs_grep()} '^def ' src | awk '{{print $2}}' | cut -d'(' -f1 | sort | uniq -d",
            "الدوال المكررة", config_key="basic_checks")
        
        run(f"find src -type f -empty {exclude_dirs_find()}",
            "الملفات الفارغة", config_key="basic_checks")
        
        run(f"grep -rIn --include='*.py' {exclude_dirs_grep()} -E 'TODO|HACK|FIXME|PLACEHOLDER' src",
            "كود شبه نهائي / TODO", config_key="basic_checks")

    # فحوصات الأمان
    if CONFIG.get("security_checks", True):
        print("\n🔒 فحوصات الأمان...")
        
        run(f"bandit -r src/ --exclude {','.join(EXCLUDES)}",
            "أمان المشروع (Bandit)", "bandit", "security_checks")
        
        run("safety check", "فحص الحزم المثبتة (Safety)", 
            "safety", "security_checks")
        
        run("pip-audit", "تحقق أمان الحزم (pip-audit)", 
            "pip-audit", "security_checks")
        
        run("detect-secrets scan", "كشف الأسرار والمعلومات الحساسة", 
            "detect-secrets", "security_checks")

    # فحوصات جودة الكود
    if CONFIG.get("quality_checks", True):
        print("\n⚡ فحوصات جودة الكود...")
        
        run(f"ruff check src/ --exclude {' '.join(EXCLUDES)}", 
            "تنظيف سريع للكود (Ruff)", "ruff", "quality_checks")
        
        run(f"mypy src/ --exclude {'|'.join(EXCLUDES)}", 
            "التحقق من أنواع البيانات (MyPy)", "mypy", "quality_checks")
        
        run(f"vulture src {' '.join([f'--exclude {d}' for d in EXCLUDES])}", 
            "الـ dead code (Vulture)", "vulture", "quality_checks")
        
        run(f"radon cc -s src/ --exclude {','.join(EXCLUDES)}", 
            "تعقيد الشفرة (Radon)", "radon", "quality_checks")

    # فحوصات التوثيق والتنسيق
    if CONFIG.get("documentation_checks", True):
        print("\n📚 فحوصات التوثيق والتنسيق...")
        
        run(f"black --check src/ --exclude {'|'.join(EXCLUDES)}", 
            "التحقق من تنسيق الكود (Black)", "black", "documentation_checks")
        
        run(f"isort --check-only src/ --skip {' '.join(EXCLUDES)}", 
            "ترتيب الاستيرادات (isort)", "isort", "documentation_checks")
        
        run(f"pydocstyle src/ --ignore={' '.join(EXCLUDES)}", 
            "فحص جودة التوثيق (pydocstyle)", "pydocstyle", "documentation_checks")

    # فحوصات متقدمة خاصة بـ AI
    if CONFIG.get("ai_specific_checks", True):
        print("\n🤖 فحوصات خاصة بمشاريع الذكاء الاصطناعي...")
        
        # فحص استخدام المتغيرات البيئية للمفاتيح
        run(f"grep -rn --include='*.py' {exclude_dirs_grep()} -E 'api_key|API_KEY|secret_key' src",
            "فحص مفاتيح API المكشوفة", config_key="ai_specific_checks")
        
        # فحص استخدام المكتبات الشائعة في AI
        run(f"grep -rn --include='*.py' {exclude_dirs_grep()} -E 'import (torch|tensorflow|openai|anthropic)' src",
            "فحص مكتبات الذكاء الاصطناعي المستخدمة", config_key="ai_specific_checks")
        
        # فحص معالجة الأخطاء في استدعاءات API
        run(f"grep -rn --include='*.py' {exclude_dirs_grep()} -A5 -B5 'requests\\.|aiohttp\\.|httpx\\.' src",
            "فحص معالجة استدعاءات API", config_key="ai_specific_checks")

    # تغطية الاختبارات
    if os.path.exists('.coverage'):
        run('coverage report', "تغطية الاختبارات")
    else:
        REPORT.append("## تغطية الاختبارات\n⚠️ **لم تُشغّل** — شغّل `coverage run -m pytest` أولاً.\n" + SEP)

    # إنشاء ملف التقرير الرئيسي
    report_content = '\n'.join(REPORT)
    
    # إضافة الملخص في البداية
    summary = create_summary_report()
    final_report = summary + "\n" + report_content
    
    # حفظ التقرير
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f'audit_report_ai_teddy_{timestamp}.md'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(final_report)

    # إنشاء تقرير JSON للمعالجة الآلية
    json_report = {
        "timestamp": timestamp,
        "project": "AI Teddy Bear v5",
        "total_checks": len([r for r in REPORT if r.startswith("##")]),
        "config": CONFIG
    }
    
    with open(f'audit_summary_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(json_report, f, ensure_ascii=False, indent=2)

    total_time = time.time() - global_start
    print(f"\n✅ 🧸 تحليل مشروع AI Teddy Bear v5 اكتمل!")
    print(f"📄 افتح {report_file} للمراجعة التفصيلية")
    print(f"📊 افتح audit_summary_{timestamp}.json للبيانات المنظمة")
    print(f"⏱️ الوقت الكلي: {total_time:.2f} ثانية (≈ {total_time/60:.2f} دقيقة)")

if __name__ == '__main__':
    main()