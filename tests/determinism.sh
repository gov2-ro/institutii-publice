#!/bin/sh
# Full-data check: consolidation must give the same CSV under two hash seeds.
# Needs the ignored inputs (see CLAUDE.md, Data flow) and uv. Run from the repo root: sh tests/determinism.sh
set -e
out=data/consolidated/institutii.csv
PYTHONHASHSEED=1 uv run scripts/consolidate.py 2>/dev/null && cp "$out" /tmp/institutii.seed1.csv
PYTHONHASHSEED=2 uv run scripts/consolidate.py 2>/dev/null && cp "$out" /tmp/institutii.seed2.csv
cmp /tmp/institutii.seed1.csv /tmp/institutii.seed2.csv && echo "deterministic: identical CSV under PYTHONHASHSEED=1 and 2"
