#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$PWD"
PY="${ROOT}/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  echo "Missing venv. From the api/ folder run:"
  echo "  python3 -m venv .venv"
  echo "  ./.venv/bin/python -m pip install -e \".[dev]\""
  exit 1
fi
exec "${ROOT}/.venv/bin/uvicorn" app.main:app --reload --host 0.0.0.0 --port 8000
