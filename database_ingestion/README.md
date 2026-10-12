# Database & Data Ingestion Module

Owns the PostgreSQL schema, pgvector setup and the seed data for Edunova.

## Contents

- `schema.sql` — full table definitions (13 tables including `questionnaire_responses`)
- `scripts/db.py` — cross-platform PostgreSQL bootstrap (cluster, roles, pgvector, schema)
- `scripts/populate.py` — seeds exams, schedules, eligibility rules, scholarships and sources
- `scripts/pgvector/vector--0.8.6.sql` — pgvector type install used by `db.py`

## Setup

Requires PostgreSQL binaries on PATH (or a standard install on Windows). Python
dependencies are only needed for seeding:

```
pip install -r database_ingestion/requirements.txt
python database_ingestion/scripts/db.py setup
python database_ingestion/scripts/populate.py
```

`db.py setup` is safe to re-run. Other commands: `start`, `stop`, `status`,
`psql`, `reset` (drops the app tables and re-applies the schema).

The cluster lives in `database_ingestion/.data/db` on port `5433` and never
touches a system PostgreSQL server. Connection details:

```
host=localhost port=5433 dbname=edunova_db user=edunova_user password=edunova_pass
```
