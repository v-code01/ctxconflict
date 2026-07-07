#!/usr/bin/env bash
# Analyze and independently verify every ctxconflict claim from the committed
# results/gen.jsonl. No server needed. To regenerate raw outputs, run:
#   python tools/run_gen.py name=URL [name2=URL2]
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python; [ -x "$PY" ] || PY=python3
$PY tools/analyze.py
$PY tools/verify.py
