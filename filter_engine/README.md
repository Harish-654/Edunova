# Filter Engine Module

FastAPI backend for Edunova: authentication with roles, exam and scholarship
catalog, the personal questionnaire, the **filter engine** that matches students
to exams, and the admin/ingestion tools.

## Roles

| Role | Can do |
|------|--------|
| `student` | Register, take the questionnaire, view exam dates and scholarship dates, see their matched exams |
| `admin` | Monitor crawling/data ingestion, view raw payloads and anomalies, create and edit scholarships |

## Setup

```bash
pip install -r filter_engine/requirements.txt
cp filter_engine/.env.example filter_engine/.env
```

The database must already exist (see `database_ingestion/`).

Create an admin account:

```bash
cd filter_engine
python create_admin.py admin@edunova.app admin123
```

Run the API (from inside `filter_engine/`):

```bash
uvicorn app.main:app --reload
```

Open <http://localhost:8000/docs> for the interactive API docs.

## Endpoints

All routes are prefixed with `/api/v1`.

| Area | Endpoints |
|------|-----------|
| Auth | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| Student | `GET/PUT /students/me/profile`, `GET/PUT /students/me/marks`, `GET/PUT /students/me/preferences` |
| Catalog | `GET /exams`, `GET /exams/{id}`, `GET /scholarships`, `GET /scholarships/exam/{id}` |
| Questionnaire | `GET /questionnaire/questions`, `POST /questionnaire/submit`, `GET /questionnaire/me` |
| Match (filter engine) | `GET /match/my`, `POST /match/run` |
| Ingestion (admin) | `GET/POST /ingestion/sources`, `POST /ingestion/run`, `GET /ingestion/payloads`, `GET /ingestion/anomalies` |
| Admin | `GET /admin/overview`, `POST /admin/scholarships`, `PUT/DELETE /admin/scholarships/{id}`, `POST/DELETE /admin/scholarships/{id}/exams/{exam_id}` |

## How the filter engine ranks exams

1. **Hard eligibility gate** — age, marks, degree and family income are checked
   against each exam's `eligibility_rules`. A student who fails any rule is
   marked ineligible and the reason is returned. Missing profile data does not
   block a rule (it is skipped).
2. **Semantic match** — the student's career statement and preferred fields are
   embedded and compared to each exam embedding with pgvector
   (`1 - (embedding <=> student)`), giving a 0..1 similarity.
3. **Field overlap** — the fraction of the student's preferred fields that appear
   in the exam text.
4. **Composite score** — `(0.6 * semantic + 0.4 * field overlap) * 100`, sorted so
   eligible exams come first. Results are cached in `recommendation_cache`.

The default embedder is a deterministic local hasher (no API key needed). The
same algorithm is used by `database_ingestion/scripts/populate.py` so exam and
student vectors are comparable.
