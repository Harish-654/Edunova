#!/usr/bin/env bash
# Cross-platform DB setup shim. Real logic: scripts/db.py
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$DIR/db.py" setup "$@"