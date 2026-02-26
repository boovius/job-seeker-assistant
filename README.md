# Job Culler

Phase 1 scaffold for the Job Intelligence Agent.

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

## Local Dev (API + Supabase)
1. Create a Supabase project and note the database connection string.
2. Set `DATABASE_URL` in `.env` to your Supabase Postgres connection string.
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

## Local Dev (Web)
```bash
cd apps/web
npm install
npm run dev
```

## Supabase Auth (JWKS) Setup
1. In Supabase, go to Project Settings -> API and note:
   - Project ref
   - JWKS URL
2. Set `SUPABASE_PROJECT_REF` in `.env`.
3. The API will use the JWKS URL derived from `SUPABASE_PROJECT_REF` to verify tokens.

## Automated Discovery Sources (Phase 1)
We currently support Greenhouse and Lever adapters. These are public job board endpoints and do not require API keys for reading job listings. You will need each company's board token (Greenhouse) or account name (Lever) to query their postings.citeturn0search0turn0search7

Examples:
- Greenhouse: `https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true`citeturn0search0
- Lever: `https://api.lever.co/v0/postings/{company}`citeturn0search7

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
