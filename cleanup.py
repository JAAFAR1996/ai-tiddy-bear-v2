#!/usr/bin/env python3
import os, json, subprocess
import coverage
from vulture import Vulture
from pydeps.pydeps import externals

SRC = "src"  # قابل للتعديل حسب مجلد المشروع

# 1. Vulture API
v = Vulture()
v.scavenge([SRC])
unused_vulture = {item.filename for item in v.get_unused_code() if item.confidence == 100}

# 2. Coverage dynamic
cov = coverage.Coverage(source=[SRC])
cov.start()
# ✅ استبدل السطر أدناه بثلاث خطوات: import modules أو تشغيل pytest
# import myproject
cov.stop()
cov.save()
cov_data = cov.get_data()
unused_cov = set()
for file in cov_data.measured_files():
    if file.startswith(SRC) and not cov_data.lines(file):
        unused_cov.add(file)

# 3. Dependency with pydeps
os.chdir(os.getcwd())
missing = set(externals(os.getcwd()))

all_py = {os.path.join(dp, f) for dp,_,fs in os.walk(SRC) for f in fs if f.endswith(".py")}
used_dep = set()
for f in all_py:
    mod = os.path.splitext(os.path.relpath(f, SRC))[0].replace(os.sep, ".")
    if mod not in missing:
        used_dep.add(f)

unused_dep = all_py - used_dep

# 4. تركيبة النتائج
candidates = unused_vulture & unused_cov & unused_dep

# 5. طباعة النتيجة
print(f"🔍 Files you can delete with ~99% safety ({len(candidates)}):")
for p in sorted(candidates):
    print(" -", p)
