import os
from collections import defaultdict

report_file = "flake8_report.txt"
output_file = "flake8_report_grouped.txt"

# تجميع النتائج
problems_by_dir = defaultdict(list)

with open(report_file, encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        # مثال: src/presentation/api/endpoints/children/create_child.py:29:9: F821 undefined name 'Provide'
        parts = line.split(":")
        if len(parts) < 4:
            continue
        filepath = parts[0].strip()
        folder = os.path.dirname(filepath)
        problems_by_dir[folder].append(line.strip())

# كتابة التقرير الجديد بشكل مرتب حسب المجلد
with open(output_file, "w", encoding="utf-8") as f:
    for folder in sorted(problems_by_dir):
        f.write(f"\n=== {folder} ===\n")
        f.writelines(problem + "\n" for problem in problems_by_dir[folder])
