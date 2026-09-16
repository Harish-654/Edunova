#!/usr/bin/env bash
# Cross-platform DB management shim. Real logic: scripts/db.py
# Usage: scripts/db.sh {setup|start|stop|status|psql|reset} [args...]
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$DIR/db.py" "$@"