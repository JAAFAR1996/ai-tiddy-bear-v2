#!/bin/bash
set -e

mkdir -p reports

# يبحث عن الكلمات المشبوهة ويكتب النتائج في تقرير مفصل
rg --line-number --with-filename "dummy|mock|pass|TODO" src/ > reports/dummy_references.log || true

if [ -s reports/dummy_references.log ]; then
  echo "Dummy code found! See reports/dummy_references.log"
  echo "========== DUMMY CODE REFERENCES =========="
  cat reports/dummy_references.log
  echo "==========================================="
  exit 1
else
  echo "No dummy code found."
  exit 0
fi
