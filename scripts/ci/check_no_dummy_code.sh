#!/usr/bin/env bash
set -e
echo "Running dummy/mocks/fake code scan..."
rg -i 'dummy|mock|stub|fake|placeholder|testdata|hardcoded|TODO|FIXME' src/ > reports/dummy_references.log || true
if test -s reports/dummy_references.log; then
    echo "❌ DUMMY FOUND"
    cat reports/dummy_references.log
    exit 1
else
    echo "✅ No dummy code found"
fi
