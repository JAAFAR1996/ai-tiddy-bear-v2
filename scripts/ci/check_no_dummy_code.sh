#!/bin/bash
rg "dummy|mock|pass|TODO" src/ > dummy_report.txt
if [ -s dummy_report.txt ]; then
  echo "Dummy code found!"
  exit 1
else
  echo "No dummy code found."
fi
