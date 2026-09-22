#!/bin/bash
# Start the API on a throwaway port, run the end-to-end smoke test, stop the API.
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$(cd .. && pwd)"

PORT="${1:-8001}"
URL="http://localhost:${PORT}/api/v1"

"$ROOT/.venv/bin/uvicorn" app.main:app --port "$PORT" > /tmp/opencode/verify_uvicorn.log 2>&1 &
UVPID=$!
trap 'kill -9 "$UVPID" 2>/dev/null || true' EXIT
sleep 4

"$ROOT/.venv/bin/python" scripts/api_verify.py "$URL"