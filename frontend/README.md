# Frontend Module

Simple React + Vite + TypeScript interface for Edunova. Plain CSS, no extra
UI framework.

## Setup

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

The app runs at <http://localhost:5173>. It expects the API from
`filter_engine/` at `http://localhost:8000` (change `VITE_API_URL` in `.env`
if you run it elsewhere).

## Screens

**Students** (create an account from the Log in page):

1. **Questionnaire** — personal and career questions; answers drive the filter
   engine.
2. **My matches** — exams ranked by match score, with eligibility and reasons.
3. **Exams** — exam dates, eligibility and fees.
4. **Scholarships** — aid available.

**Admin** (log in with an account created by `create_admin.py`):

1. **Overview** — live counts of students, exams, payloads and anomalies.
2. **Crawling** — sources, run/fetch controls, anomalies and raw payloads.
3. **Scholarships** — create, edit and delete scholarship records.

## Build

```bash
npm run build
```

Output goes to `frontend/dist/`.
