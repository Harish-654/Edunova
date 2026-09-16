#!/usr/bin/env bash
# One-shot bootstrap for a fresh EduNova clone.
# Creates a project-owned PostgreSQL cluster, roles/database, installs
# pgvector into .data/pgvector, and applies schema.sql.
#
# Requirements: pg_config/initdb/pg_ctl/psql on PATH (any single-user Postgres
# install works; e.g. `apt install postgresql` or brew postgresql). Build tools
# (make, gcc) + the PG dev headers are needed the first time pgvector is built.
#
# Idempotent: safe to re-run. Existing data is preserved unless --reset is given.
#
# Usage: scripts/setup_db.sh [--reset]

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="$ROOT/.data/db"
PGVEC_DIR="$ROOT/.data/pgvector"
LOG_FILE="$DATA_DIR/pg.log"
PORT=5433
DB_USER=edunova_user
DB_PASS=edunova_pass
DB_NAME=edunova_db

RESET=0
if [[ "${1:-}" == "--reset" ]]; then RESET=1; fi

say()  { printf '\033[1;34m[setup]\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31m[setup] ERROR:\033[0m %s\n' "$*" >&2; exit 1; }

for bin in pg_config initdb pg_ctl psql; do
  command -v "$bin" >/dev/null || die "missing '$bin' on PATH"
done

PG_MAJOR="$(pg_config --version | sed -E 's/^PostgreSQL ([0-9]+).*/\1/')"
say "PostgreSQL tools: $(pg_config --version)"

# ---------------------------------------------------------------- cluster
if [[ -f "$DATA_DIR/PG_VERSION" ]]; then
  CLUSTER_PG="$(cat "$DATA_DIR/PG_VERSION")"
  say "Cluster exists (.data/db, PG $CLUSTER_PG)"
else
  say "Initializing cluster at .data/db ..."
  mkdir -p "$(dirname "$DATA_DIR")"
  initdb -D "$DATA_DIR" --auth=trust --username=postgres \
    --no-locale --encoding=UTF8 -q
  CLUSTER_PG="$(cat "$DATA_DIR/PG_VERSION")"
fi

if [[ "$PG_MAJOR" != "$CLUSTER_PG" ]]; then
  die "pg_config on PATH is PG $PG_MAJOR but cluster was built with PG $CLUSTER_PG. Use matching tools."
fi

# ---------------------------------------------------------------- pgvector
if [[ ! -f "$PGVEC_DIR/vector.so" ]]; then
  say "pgvector not built yet. Building from source (one time)..."
  command -v make >/dev/null || die "missing 'make'"
  command -v gcc  >/dev/null || die "missing 'gcc'"
  mkdir -p "$PGVEC_DIR"
  BUILD_DIR="$ROOT/.data/build/pgvector"
  if [[ ! -d "$BUILD_DIR" ]]; then
    git clone --quiet --branch v0.8.6 --depth 1 \
      https://github.com/pgvector/pgvector.git "$BUILD_DIR"
  fi
  ( cd "$BUILD_DIR" && make -s PG_CONFIG="$(command -v pg_config)" )
  cp "$BUILD_DIR"/src/vector.so "$PGVEC_DIR/vector.so"
  say "pgvector shared object -> $PGVEC_DIR/vector.so"
fi

# ---------------------------------------------------------------- run/roles/db
if pg_ctl -D "$DATA_DIR" status >/dev/null 2>&1; then
  say "Cluster already running on port $PORT."
else
  say "Starting cluster on port $PORT ..."
  pg_ctl -D "$DATA_DIR" -l "$LOG_FILE" \
    -o "-p $PORT -c unix_socket_directories=/tmp" -w start
fi

ensure_roles() {
  psql -h localhost -p "$PORT" -U postgres -d postgres -v ON_ERROR_STOP=1 <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'postgres') THEN
    CREATE ROLE postgres LOGIN SUPERUSER;
  END IF;
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${DB_USER}') THEN
    CREATE ROLE ${DB_USER} LOGIN PASSWORD '${DB_PASS}';
  END IF;
END
\$\$;
SQL
}
ensure_db() {
  psql -h localhost -p "$PORT" -U postgres -d postgres -tAc \
    "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'" | grep -q 1 || \
  psql -h localhost -p "$PORT" -U postgres -d postgres -c \
    "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER}"
}
say "Ensuring roles + database ..."
ensure_roles
ensure_db

# ---------------------------------------------------------------- vector types
say "Installing pgvector types into ${DB_NAME} ..."
if psql -h localhost -p "$PORT" -U "$DB_USER" -d "$DB_NAME" -tAc \
     "SELECT 1 FROM pg_type WHERE typname='vector'" | grep -q 1; then
  say "  vector type already present."
else
  # base types require a superuser; postgres is created in ensure_roles above
  sed "s|MODULE_PATHNAME|$PGVEC_DIR/vector|g" \
    "$ROOT/scripts/pgvector/vector--0.8.6.sql" > "$PGVEC_DIR/vector_install.sql"
  psql -h localhost -p "$PORT" -U postgres -d "$DB_NAME" -q \
    -f "$PGVEC_DIR/vector_install.sql"
  say "  vector type installed."
fi

# ---------------------------------------------------------------- schema
if [[ "$RESET" == "1" ]]; then
  say "--reset: dropping all app tables ..."
  DROP_SQL=""
  for t in scholarship_exam_mappings scholarships ingestion_anomaly_logs \
           raw_staging_payloads scraping_sources recommendation_cache \
           eligibility_rules exam_schedules exams student_marks \
           student_preferences students; do
    DROP_SQL+="DROP TABLE IF EXISTS public.$t CASCADE; "
  done
  psql -h localhost -p "$PORT" -U "$DB_USER" -d "$DB_NAME" -q -c "$DROP_SQL"
fi

if psql -h localhost -p "$PORT" -U "$DB_USER" -d "$DB_NAME" -tAc \
     "SELECT 1 FROM pg_tables WHERE schemaname='public' AND tablename='exams'" | grep -q 1; then
  say "Schema already applied (exams exists) — skipping."
else
  say "Applying schema.sql ..."
  psql -h localhost -p "$PORT" -U "$DB_USER" -d "$DB_NAME" -q -f "$ROOT/schema.sql"
fi

say "Done. Connect with: psql -h localhost -p $PORT -U $DB_USER -d $DB_NAME"
say "Next: cp backend/.env.example backend/.env  &&  cd backend && ../.venv/bin/pip install -r requirements.txt"
say "      then seed data:  cd backend && ../.venv/bin/python scripts/populate.py"