# EduNova — AI-Driven Career Guidance & Examination Matching Platform

EduNova recommends the right Indian entrance exams for a student. A student
builds a profile (age, marks, degree, family income, career interests) and the
engine returns **ranked exam matches** — combining a *hard eligibility gate*
(age / percentage / degree / income) with *semantic similarity* (pgvector
cosine distance between the student's career statement and each exam's
embedding).

## How it works internally

```
 [scraping_sources] ──► Playwright scraper ──► raw_staging_payloads (raw HTML)
                                                │
                                                ▼
                                      parser.py (dates, fees, bounds)
                                                │
                       missing/odd data? ──► ingestion_anomaly_logs (audit)
                                                │
                                      embedder.py (1536-dim local / OpenAI)
                                                │
                          exams (catalog + embedding_vector vector(1536))
                                                ▲
 [student profile] ──► eligibility.py (binary gate) ──► scorer.py
                              │        (pgvector 1 - (embedding <=> interest))
                              ▼                     │
                    composite_score (0.6·semantic + 0.4·overlay) ──► ranked matches
                              │
                   recommendation_cache (fast reads)
```

1. **Ingestion** — an APScheduler job runs daily and uses Playwright
   (headless Chromium) to fetch the exam portals in `scraping_sources`. Raw
   HTML is staged first, then the parser normalizes it. Anything suspicious
   (missing mandatory fields, HTTP errors) is written to
   `ingestion_anomaly_logs` instead of being silently ignored.
2. **Embeddings** — each exam gets a 1536-dim vector. Default provider is a
   deterministic offline hasher; set `EMBEDDING_PROVIDER=openai` for real
   semantic embeddings (see `.env`).
3. **Match** — a two-stage engine. Stage 1 is a *binary eligibility gate* that
   only enforces the rules an exam actually defines. Stage 2 computes cosine
   similarity **inside PostgreSQL** with the pgvector operator
   `1 - (embedding_vector <=> interest)` and blends it with a
   field-preference overlay into a `composite_score` percentage.

## Repository layout

```
EduNova/
├── backend/                    # FastAPI service
│   ├── app/
│   │   ├── main.py             # app factory, router wiring, scheduler, CORS
│   │   ├── core/               # config (.env), async DB session, JWT security
│   │   ├── models/entities.py  # SQLAlchemy ORM (mirrors schema.sql)
│   │   ├── schemas/schemas.py  # Pydantic request/response models
│   │   └── modules/
│   │       ├── auth/           # register / login / me (JWT)
│   │       ├── student/        # profile, marks, preferences
│   │       ├── catalog/        # exams catalog + schedules
│   │       ├── ingestion/      # scraper, parser, embedder, scheduler, router
│   │       ├── matcher/        # eligibility, scorer, cache, router
│   │       └── scholarship/    # financial aid + exam mappings
│   ├── scripts/
│   │   ├── populate.py         # seeds real 2026 exam data + embeddings
│   │   ├── demo_match.py       # 4-profile semantic-matcher demo
│   │   ├── run_demo.sh         # one-shot demo runner
│   │   ├── api_verify.py       # end-to-end API smoke test
│   │   └── run_verify.sh       # one-shot verify runner
│   ├── requirements.txt
│   └── .env.example
├── scripts/
│   ├── setup_db.sh             # one-command DB bootstrap for fresh clones
│   ├── db.sh                   # start/stop/status/psql/reset/setup
│   └── pgvector/vector--0.8.6.sql  # bundled pgvector extension script
├── schema.sql                  # canonical schema (12 tables, pgvector)
└── frontend/                   # (React + TS + Tailwind SPA — in progress)
```

## Prerequisites

- **Python 3.12+** (developed on 3.14)
- **PostgreSQL binaries on PATH**: `pg_config`, `initdb`, `pg_ctl`, `psql`
  (`apt install postgresql`, `brew install postgresql@18`, etc.). The project
  does **not** need your system cluster — it creates its own on port **5433**.
- **Build tools** (first pgvector build only): `make`, `gcc`, `git`
  (Linux: the postgres server dev headers, e.g. `postgresql-server-dev-18`).
- **Node 20+/npm** (only for the frontend, which is in progress).

No sudo/root access is required anywhere.

## Database setup & migration

The project keeps a **private PostgreSQL cluster** in `.data/db` on port
**5433**, so it never touches (or conflicts with) a system postgres.
pgvector is built from source once and installed into the cluster.

### Fresh clone — one command

```bash
git clone <repo-url> edunova && cd edunova
./scripts/setup_db.sh
```

That single command, idempotently:
1. `initdb`s a cluster at `.data/db` (trust auth) if missing,
2. starts it on port `5433`,
3. creates roles `postgres` (superuser) and `edunova_user` and database
   `edunova_db`,
4. builds pgvector v0.8.6 (one-time, into `.data/pgvector`) and installs the
   `vector(1536)` type,
5. applies `schema.sql` (the **12 tables**) — only if not already applied.

Re-run any time; it detects what exists. `./scripts/setup_db.sh --reset`
drops and re-applies the schema (wipes data).

### Migration workflow

`schema.sql` is the source of truth for structure. Two ways to apply a change:

- **Local reset (deletes data):** after editing `schema.sql`, run
  `./scripts/db.sh reset` — drops the 12 app tables in dependency order and
  re-applies `schema.sql`. pgvector types are untouched.
- **Incremental (keeps data):** append an `ALTER TABLE ...` to
  `scripts/migrations/NNN_name.sql` and apply it:

  ```bash
  psql -h localhost -p 5433 -U edunova_user -d edunova_db -f scripts/migrations/001_whatever.sql
  ```

### Day-to-day cluster management

```bash
./scripts/db.sh start      # start (.data/db, port 5433)
./scripts/db.sh stop       # stop
./scripts/db.sh status     # running?
./scripts/db.sh psql       # interactive shell as edunova_user
./scripts/db.sh reset      # drop tables + re-apply schema.sql
```

## Running the backend API

```bash
cd backend
python3 -m venv ../.venv && source ../.venv/bin/activate   # or reuse existing .venv
pip install -r requirements.txt
python -m playwright install chromium        # once, for the scraper
cp .env.example .env                          # adjust as needed

# (fresh DB) seed real exam data + embeddings:
python scripts/populate.py

# run the API (rebuild on save):
uvicorn app.main:app --reload                 # http://localhost:8000
# interactive docs: http://localhost:8000/docs
```

Environment (`backend/.env`, copy of `.env.example`):

| Variable | Default | Meaning |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://edunova_user:edunova_pass@localhost:5433/edunova_db` | asyncpg DSN |
| `JWT_SECRET` | `edunova-dev-secret-change-me` | change in production |
| `EMBEDDING_PROVIDER` | `local` | `local` (offline hashing) or `openai` |
| `EMBEDDING_DIMENSIONS` | `1536` | vector width (must match schema) |
| `SEMANTIC_WEIGHT` / `PREFERENCE_WEIGHT` | `0.6` / `0.4` | composite formula |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | frontend dev origin |

## API reference (`/api/v1`)

All ids are UUIDv4. Auth: pass `Authorization: Bearer <access_token>` where
marked 🔒.

### Auth

| Method | Path | Body / params | Returns |
|---|---|---|---|
| `POST` | `/auth/register` | `{full_name, email, password, age, category?, state_of_residence?, annual_family_income?}` | `201 {access_token, token_type, user{student_id,…}}` |
| `POST` | `/auth/login` | `{email, password}` | `200 {access_token, …}` |
| `GET` | `/auth/me` 🔒 | header | `{student_id, full_name, email, age, category, state_of_residence, annual_family_income}` |

### Student profile

| Method | Path | Body | Notes |
|---|---|---|---|
| `PUT` | `/students/{id}/profile` | `{age?, category?, state_of_residence?, annual_family_income?}` | patch demographics |
| `PUT` | `/students/{id}/marks` | `{qualifying_degree, overall_percentage, graduation_year}` | replaces marks |
| `PUT` | `/students/{id}/preferences` | `{preferred_fields[], preferred_locations[], career_interest_statement}` | drives matching |

### Catalog

| Method | Path | Query | Returns |
|---|---|---|---|
| `GET` | `/exams` | `limit`, `offset`, `q`, `level`, `conducting_body` | `{count, data:[{exam_id, exam_code, exam_name, exam_level, conducting_body, application_fee, official_url}]}` |
| `GET` | `/exams/{id}` | — | detail with schedules + eligibility rule |
| `GET` | `/exams/{id}/schedules` | — | `[{application_start_date, application_end_date, exam_date, academic_year}]` |

### Match engine

| Method | Path | Returns |
|---|---|---|
| `POST` | `/match/student/{id}/compute` | recompute + return `MatchResponse` |
| `GET` | `/match/student/{id}/recommendations` | cached (or live) results |

`MatchResponse` = `{student_id, results:[{exam, schedule?, deterministic_eligible, semantic_match_score?, composite_score?, eligibility{age,percentage,degree,income,detail}, scholarships[]}]}` —
sorted by `composite_score` descending.

### Scholarships

| Method | Path | Returns |
|---|---|---|
| `GET` | `/scholarships` | `[{scholarship_id, title, provider_name, max_amount, max_income_limit}]` |
| `GET` | `/scholarships/exam/{exam_id}` | scholarships mapped to that exam |

### Ingestion

| Method | Path | Body | Returns |
|---|---|---|---|
| `GET` | `/ingestion/sources` | — | scraping sources + cron |
| `POST` | `/ingestion/sources` | `{target_name, target_url, cron_expression?}` | `201` source |
| `POST` | `/ingestion/trigger` | `{source_id?}` (omit = all active) | `{triggered, scheduled}` |
| `POST` | `/ingestion/embed-all` | — | re-embeds all exams |
| `GET` | `/ingestion/anomalies` | `limit` | audit log of crawl/validation errors |

### Misc

| Method | Path | Returns |
|---|---|---|
| `GET` | `/health` | `{status:"ok", db:"ok"}` |
| `GET` | `/` | app banner |

## What data is present and how to query it

Seeded by `scripts/populate.py` (before or alongside live crawling):

- **10 exams** with real 2026 bulletin data: JEE-Main, NEET-UG, CUET-UG,
  NCHM-JEE, NCET-2026, CMAT, CAT-2026, GATE-2026, UGC-NET, CSIR-NET
- **10 schedules**, **10 eligibility rules**, **25 scholarship→exam mappings**, **7 scholarships**
- **9 scraping sources** (NTA + agency portals) and a few audit entries if the
  live crawler has hit sites (403s etc. land in `ingestion_anomaly_logs`)

Useful queries (via `./scripts/db.sh psql` or any SQL client on `:5433`):

```sql
-- the full exam catalog with deadlines
SELECT e.exam_name, e.exam_level, e.conducting_body,
       s.application_end_date, s.exam_date, e.embedding_vector IS NOT NULL AS embedded
FROM exams e LEFT JOIN exam_schedules s ON s.exam_id = e.exam_id;

-- hardest gate each exam imposes
SELECT e.exam_name, COALESCE(r.max_age::text,'-')  AS max_age,
       COALESCE(r.min_qualifying_percentage::text,'-') AS min_pct,
       COALESCE(r.required_degree,'-') AS degree,
       COALESCE(r.max_family_income::text,'-') AS max_income
FROM exams e LEFT JOIN eligibility_rules r ON r.exam_id = e.exam_id;

-- which scholarships apply to NEET-style exams
SELECT e.exam_name, s.title
FROM scholarship_exam_mappings m
JOIN scholarships s  ON s.scholarship_id = m.scholarship_id
JOIN exams e         ON e.exam_id = m.exam_id;

-- all recent ingestion anomalies (crawl/validation audit trail)
SELECT a.logged_at, a.error_code, a.missing_fields, t.target_name
FROM ingestion_anomaly_logs a
LEFT JOIN raw_staging_payloads r ON r.payload_id = a.payload_id
LEFT JOIN scraping_sources t     ON t.source_id = r.source_id
ORDER BY a.logged_at DESC;

-- students already registered + their latest preference statement
SELECT s.full_name, p.career_interest_statement
FROM students s
JOIN student_preferences p USING (student_id);

-- does anything violate a hard gate in the cache?
SELECT st.full_name, e.exam_name, rc.deterministic_eligible, rc.composite_score
FROM recommendation_cache rc
JOIN students st ON st.student_id = rc.student_id
JOIN exams e     ON e.exam_id  = rc.exam_id
ORDER BY rc.composite_score DESC NULLS LAST;
```

## Demos & verification

```bash
# (1) semantic matcher demo — 4 students with different interests, tables of
#     top-ranked exams; proves the engine picks different exams per profile
cd backend && ./scripts/run_demo.sh            # port via arg: ./scripts/run_demo.sh 8002

# (2) end-to-end API smoke test (register→profile→compute→scholarships→audit)
cd backend && ./scripts/run_verify.sh
```

## What is real vs seed data

| Data | Source |
|---|---|
| Exam names, deadlines, fees, age/percentage/income gates | **real 2026** values from official **NTA Information Bulletins** and agency portals, curated in `populate.py` |
| Live-crawl pipeline | hits real portals (`jeemain.nta.nic.in`, `neet.nta.nic.in`, `cuet.nta.nic.in`, `ugcnet.nta.nic.in`, `iimcat.ac.in`, `gate2026.iisc.ac.in`, …). NTA blocks bots — those failures are recorded as anomalies, not errors |
| Embeddings | default **local deterministic hashing**; set `EMBEDDING_PROVIDER=openai` to use `text-embedding-3-small` for better semantic quality |
| Scholarships | real common schemes (Pragati, Saksham, Central Sector, Post-Matric, NEST, JRF) with typical published values — **validate against scholarships.gov.in before production** |

## Status / roadmap

- [x] Ingestion pipeline (scraper, staging, parser, anomaly audit, embeddings, scheduler)
- [x] Hybrid match engine (gate + pgvector semantic + composite + cache)
- [x] Auth, student profile, catalog, scholarships APIs
- [x] Real 2026 data seeding + one-command DB setup with pgvector
- [ ] Frontend SPA (React + TypeScript + Tailwind) — **in progress**
- [ ] OpenAI embeddings toggle verification, CI, Dockerfile