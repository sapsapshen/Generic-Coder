#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

PYTHON=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1; then
    PYTHON="$candidate"
    break
  fi
done

if [ -z "$PYTHON" ]; then
  echo "Error: Python not found" >&2
  exit 1
fi

HOST="${GENERIC_CODER_HOST:-127.0.0.1}"
PORT="${GENERIC_CODER_PORT:-8765}"

echo "[Generic Coder] Starting..."
"$PYTHON" "$SCRIPT_DIR/frontends/generic_coder_web.py" --host "$HOST" --port "$PORT"
