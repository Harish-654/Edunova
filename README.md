# Edunova

Edunova matches students to exams and scholarships. A student answers a short
questionnaire, the backend scores every exam against those preferences and
eligibility rules, and the UI shows the ranked results. An admin monitors the
data crawlers and maintains scholarship records.

## Structure

- `frontend/`: React + Vite + TypeScript UI (Frontend team)
- `filter_engine/`: FastAPI core, auth & matching logic (Filter Engine team)
- `database_ingestion/`: PostgreSQL + pgvector schema, setup and ingestion scripts (Database team)

## Roles

- **Student**: questionnaire, matched exams, exam dates, scholarships.
- **Admin**: system overview, crawl sources and payloads, anomalies, scholarships.

## Quick start

Run each step from the repository root.

### 1. Database

```bash
python -m venv .venv
.venv/bin/pip install -r database_ingestion/requirements.txt
.venv/bin/python database_ingestion/scripts/db.py setup
.venv/bin/python database_ingestion/scripts/populate.py
```

This downloads/builds pgvector, creates a local PostgreSQL cluster under
`database_ingestion/.data/`, applies `schema.sql`, then seeds sample data.
See `database_ingestion/README.md` for `start`, `stop`, `status`, `psql` and
`reset`.

### 2. Backend

```bash
.venv/bin/pip install -r filter_engine/requirements.txt
cp filter_engine/.env.example filter_engine/.env
cd filter_engine
../.venv/bin/python create_admin.py admin@edunova.app admin123
../.venv/bin/uvicorn app.main:app --reload
```

API on <http://localhost:8000>, docs at `/docs`.

### 3. Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

App on <http://localhost:5173>. Log in as the admin account above, or register a
new student.
