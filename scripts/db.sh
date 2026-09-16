#!/usr/bin/env bash
# Manage the project-owned PostgreSQL cluster (port 5433).
# Usage: scripts/db.sh {start|stop|status|psql|reset|setup}
#
#   start   - start the cluster (creates it on first use)
#   stop    - stop the cluster
#   status  - is it running?
#   psql    - open a psql shell as edunova_user
#   reset   - drop all app tables and re-apply schema.sql (wipes data)
#   setup   - full bootstrap (alias of scripts/setup_db.sh)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="$ROOT/.data/db"
LOG_FILE="$DATA_DIR/pg.log"
PORT=5433

case "${1:-}" in
  start)
    if [[ ! -f "$DATA_DIR/PG_VERSION" ]]; then
      "$ROOT/scripts/setup_db.sh"
    fi
    pg_ctl -D "$DATA_DIR" -l "$LOG_FILE" \
      -o "-p $PORT -c unix_socket_directories=/tmp" -w start
    ;;
  stop)
    pg_ctl -D "$DATA_DIR" -m fast -w stop
    ;;
  status)
    pg_ctl -D "$DATA_DIR" status
    ;;
  psql)
    shift || true
    psql -h localhost -p "$PORT" -U edunova_user -d edunova_db "$@"
    ;;
  reset)
    DROP_SQL=""
    for t in scholarship_exam_mappings scholarships ingestion_anomaly_logs \
             raw_staging_payloads scraping_sources recommendation_cache \
             eligibility_rules exam_schedules exams student_marks \
             student_preferences students; do
      DROP_SQL+="DROP TABLE IF EXISTS public.$t CASCADE; "
    done
    psql -h localhost -p "$PORT" -U edunova_user -d edunova_db \
      -v ON_ERROR_STOP=1 -q -c "$DROP_SQL"
    psql -h localhost -p "$PORT" -U edunova_user -d edunova_db \
      -v ON_ERROR_STOP=1 -q -f "$ROOT/schema.sql"
    echo "Schema reset complete (data wiped)."
    ;;
  setup)
    "$ROOT/scripts/setup_db.sh" "${@:2}"
    ;;
  *)
    echo "Usage: $0 {start|stop|status|psql|reset|setup}" >&2
    exit 1
    ;;
esac