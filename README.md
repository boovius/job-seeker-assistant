# Job Culler

Phase 1 scaffold for the Job Intelligence Agent.

## Summary
Job Culler is a personal job intelligence system that ingests roles (manual URLs + automated discovery), normalizes them into a canonical `jobs` table, and runs server-side workflows for enrichment and scoring. The core pipeline uses a workflow queue to drive ingestion and processing, with adapters for ATS/job-board sources like Greenhouse and Lever. A minimal React UI supports manual URL intake and job review.

**API surface (current)**
- `POST /jobs/manual` — manual URL intake
- `GET /jobs` — list jobs
- `GET /manual-submissions` — list manual intake records
- `POST /workflows/enqueue-fetch-listings` — enqueue automated discovery
- `POST /workflows/run-once` — run one workflow task
- `POST /sources/upsert` — upsert source definitions

## Structure
- `apps/api`: FastAPI backend
- `apps/web`: React frontend (Vite)
- `packages/db`: SQLAlchemy models + Alembic migrations

## Local Dev (API)
```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Ensure env vars (see .env.example)
export $(cat ../../.env | xargs)

# Run API
PYTHONPATH=../../packages uvicorn app.main:app --reload --port 8000
```
Note: the API server must be running for the web UI and worker CLI to work.

## Run Order (Local)
1. Start the API server.
2. Start the web UI (optional).
3. Run the worker loop when you want ingestion to process queued tasks.

## Local Dev (API + Supabase)
1. Create a Supabase project and note the database connection string.
2. Set `DATABASE_URL` in `.env` to your Supabase Postgres connection string. Supabase requires SSL, so include `sslmode=require`.
   Example:
   `postgresql+psycopg://postgres:<PASSWORD>@db.<PROJECT_REF>.supabase.co:5432/postgres?sslmode=require`
3. Create the initial migration (one-time):
```bash
export $(cat ./.env | xargs)
PYTHONPATH=packages alembic -c packages/db/alembic.ini revision --autogenerate -m "init"
```
4. Run migrations:
```bash
export $(cat ./.env | xargs)
PYTHONPATH=packages alembic -c packages/db/alembic.ini upgrade head
```
Note: `revision --autogenerate` creates the migration file; `upgrade head` applies it to the database.

## Local Dev (API + Local Postgres via Docker)
```bash
docker compose up -d db
```
Set `.env`:
```
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/job_culler
```
Run migrations:
```bash
set -a; source ./.env; set +a
PYTHONPATH=packages alembic -c packages/db/alembic.ini upgrade head
```

## Local Dev (Web)
```bash
cd apps/web
npm install
npm run dev
```

## Testing Automated Discovery (Developer)
1. Set env vars in `.env`:
   - `DATABASE_URL`
   - `SUPABASE_USER_ID`
   - `GREENHOUSE_BOARD_TOKENS` (comma-separated)
   - `LEVER_COMPANIES` (comma-separated)
2. Seed sources for your user:
```bash
export $(cat ./.env | xargs)
PYTHONPATH=packages python scripts/seed_sources.py
```
Or via CLI:
```bash
export $(cat ./.env | xargs)
python scripts/cli.py seed-sources
```
3. (Optional) Seed via API:
```bash
curl -X POST http://localhost:8000/sources/upsert \
  -H "Authorization: Bearer <SUPABASE_JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "greenhouse",
    "adapter": "greenhouse_job_board_v1",
    "kind": "ats_api",
    "base_url": "https://boards.greenhouse.io",
    "default_config": {"board_tokens": ["company_token"]}
  }'
```
4. Enqueue a fetch:
```bash
curl -X POST http://localhost:8000/workflows/enqueue-fetch-listings \
  -H "Authorization: Bearer <SUPABASE_JWT>" \
  -H "Content-Type: application/json" \
  -d '{"source_slug":"greenhouse"}'
```
5. Or enqueue all enabled sources for the user:
```bash
export $(cat ./.env | xargs)
PYTHONPATH=packages python scripts/enqueue_all_sources.py
```
Or via CLI:
```bash
export $(cat ./.env | xargs)
python scripts/cli.py enqueue-all
```
6. Run the worker loop (processes `fetch_listings` and `fetch_detail` tasks):
```bash
export $(cat ./.env | xargs)
python scripts/run_worker.py
```
Or via CLI:
```bash
export $(cat ./.env | xargs)
python scripts/cli.py run-worker
```
7. Verify jobs are created:
```bash
curl -H "Authorization: Bearer <SUPABASE_JWT>" http://localhost:8000/jobs
```

## Supabase Auth (JWKS) Setup
1. In Supabase, go to Project Settings -> API and note:
   - Project ref
   - JWKS URL
2. Set `SUPABASE_PROJECT_REF` in `.env`.
3. The API will use the JWKS URL derived from `SUPABASE_PROJECT_REF` to verify tokens (ES256).
4. `SUPABASE_JWT_SECRET` is legacy HS256 and only used if JWKS is not configured.

## Automated Discovery Sources (Phase 1)
We currently support Greenhouse and Lever adapters. These are public job board endpoints and do not require API keys for reading job listings. You will need each company's board token (Greenhouse) or account name (Lever) to query their postings.

Examples:
- Greenhouse: `https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true`
- Lever: `https://api.lever.co/v0/postings/{company}`

Configuration notes:
- Store these identifiers in the `sources.default_config` JSON for each source.
- Example: Greenhouse `default_config` includes `board_tokens: ["company_token"]`
- Example: Lever `default_config` includes `companies: ["company_name"]`

## First-Time Setup Checklist
Accounts / services:
- Supabase (Postgres + Auth)
- (Optional later) Email/Slack provider for digest delivery
- (Optional later) LLM provider for enrichment/scoring

Environment variables to set in `.env`:
- `DATABASE_URL` (Supabase Postgres connection string)
- `SUPABASE_PROJECT_REF`
- `SUPABASE_JWT_SECRET` (deprecated once JWKS verification is wired)
- `API_PORT` (optional)
- `API_ENV` (optional)
- `VITE_API_BASE_URL` (for web)

## Alembic
```bash
export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/job_culler
PYTHONPATH=packages alembic -c packages/db/alembic.ini revision --autogenerate -m "init"
PYTHONPATH=packages alembic -c packages/db/alembic.ini upgrade head
```
