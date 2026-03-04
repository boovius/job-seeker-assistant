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
- `GET /sources` — list sources
- `GET /queue` — list queue items
- `GET /queue/failed` — list failed queue items

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

## Convenience Scripts
From repo root:
```bash
./scripts/start_api.sh
./scripts/start_api.sh remote
./scripts/start_web.sh
./scripts/start_web.sh remote
./scripts/start_worker.sh
./scripts/migrate.sh local "init"
./scripts/migrate.sh remote "init"
./scripts/get_jwt.sh <EMAIL> <PASSWORD>
```

## Processes (Local)
- API server (`uvicorn`) — serves HTTP endpoints used by the UI and CLI.
- Web UI (`vite`) — optional; provides manual URL intake and job list.
- Worker loop — separate process that pulls tasks from `workflow_queue` and processes them.

You typically run **three separate processes** in parallel: API, Web, Worker.

Note: the CLI currently connects directly to the DB for listing/queue commands. We may switch it to call the API instead for a stricter API-only workflow.

## Local Dev (API + Supabase)
1. Create a Supabase project and note the database connection string.
2. Set `DATABASE_URL` in `.env` to your Supabase Postgres connection string. Supabase requires SSL, so include `sslmode=require`.
   Example:
   `postgresql+psycopg://postgres:<PASSWORD>@db.<PROJECT_REF>.supabase.co:5432/postgres?sslmode=require`
3. IPv4 note: the direct `db.<PROJECT_REF>.supabase.co` hostname may not resolve on IPv4-only networks. If you see DNS errors, use the Supabase **Session Pooler** connection string from Project Settings -> Database -> Connection string -> Session Pooler.
4. Create the initial migration (one-time):
```bash
export $(cat ./.env | xargs)
PYTHONPATH=packages alembic -c packages/db/alembic.ini revision --autogenerate -m "init"
```
5. Run migrations:
```bash
export $(cat ./.env | xargs)
PYTHONPATH=packages alembic -c packages/db/alembic.ini upgrade head
```
Note: `revision --autogenerate` creates the migration file; `upgrade head` applies it to the database. Alembic is used alongside SQLAlchemy to keep schema changes in Python and version-controlled in-repo.
To confirm migrations:
```bash
PYTHONPATH=packages alembic -c packages/db/alembic.ini current
PYTHONPATH=packages alembic -c packages/db/alembic.ini history
```

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

## Source Configuration (YAML)
Source settings now live in `config/sources.yaml` (instead of env vars). Update it to control search profiles (role + sector + location) and enabled sources.

## Source Config in UI
Use the web UI to edit and save `config/sources.yaml`-style YAML. The API stores this per-user in the database and applies it to `sources`/`user_sources`.

Example `config/sources.yaml`:
```yaml
version: 1

sources:
  remotive:
    adapter: remotive_api_v1
    kind: job_board
    base_url: https://remotive.com
    enabled: true
    config:
      endpoint: https://remotive.com/api/remote-jobs
      search_profiles:
        - role_keywords: ["technical product manager"]
          sector_keywords: ["climate"]
          location: Los Angeles, CA
          remote: true
```

UI workflow:
1. Start the API and web UI.
2. Open the app in your browser.
3. Paste your YAML into the “Source Config” editor.
4. Click “Save Config”.

Override the file path via:
```
SOURCES_CONFIG=/path/to/sources.yaml
```

## Testing Automated Discovery (Developer)
1. Set env vars in `.env`:
   - `DATABASE_URL`
   - `SUPABASE_USER_ID`
2. Edit `config/sources.yaml` with your desired sources and search profiles.
3. Seed sources for your user:
```bash
export $(cat ./.env | xargs)
PYTHONPATH=packages python scripts/seed_sources.py
```
Or via CLI:
```bash
export $(cat ./.env | xargs)
python scripts/cli.py seed-sources
```
4. (Optional) Seed via API:
```bash
curl -X POST http://localhost:8000/sources/upsert \
  -H "Authorization: Bearer <SUPABASE_JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "remotive",
    "adapter": "remotive_api_v1",
    "kind": "job_board",
    "base_url": "https://remotive.com",
    "default_config": {"search_profiles": [{"role_keywords": ["technical product manager"], "sector_keywords": ["climate"], "location": "Los Angeles, CA"}]}
  }'
```
5. Enqueue a fetch:
```bash
curl -X POST http://localhost:8000/workflows/enqueue-fetch-listings \
  -H "Authorization: Bearer <SUPABASE_JWT>" \
  -H "Content-Type: application/json" \
  -d '{"source_slug":"remotive"}'
```
6. Or enqueue all enabled sources for the user:
```bash
export $(cat ./.env | xargs)
PYTHONPATH=packages python scripts/enqueue_all_sources.py
```
Or via CLI:
```bash
export $(cat ./.env | xargs)
python scripts/cli.py enqueue-all
```
7. Run the worker loop (processes `fetch_listings` and `fetch_detail` tasks):
```bash
export $(cat ./.env | xargs)
python scripts/run_worker.py
```
Or via CLI:
```bash
export $(cat ./.env | xargs)
python scripts/cli.py run-worker
```
8. Or run a full local pipeline (enqueue + worker) in one command:
```bash
export $(cat ./.env | xargs)
python scripts/cli.py run-pipeline --max-cycles 20
```
9. Verify jobs are created:
```bash
curl -H "Authorization: Bearer <SUPABASE_JWT>" http://localhost:8000/jobs
```

## Local Scheduling (Option 1)
Use your system cron to run the full pipeline on a cadence. Example (daily at 6am):
```bash
0 6 * * * cd /path/to/job-culler && export $(cat ./.env | xargs) && python scripts/cli.py run-pipeline --max-cycles 20 >> ./pipeline.log 2>&1
```
Notes:
- Adjust `--max-cycles` and `WORKER_POLL_SECONDS` based on how long you want the worker to run.
- Each cycle runs one `run_once()` then sleeps for `WORKER_POLL_SECONDS` (default 5s).
- This is a local-only scheduler; hosted scheduling can be added later.

## Supabase Auth (JWT Verification)
1. In Supabase, go to Project Settings -> API and note:
   - Project ref
   - Project URL
   - Anon public key
2. Set `SUPABASE_PROJECT_REF`, `SUPABASE_URL`, and `SUPABASE_ANON_KEY` in `.env`.
3. The API will try to verify JWTs via JWKS (`<SUPABASE_URL>/auth/v1/keys`).
4. If the JWKS endpoint is unavailable or blocked, the API falls back to validating the token via `auth/v1/user` (requires `SUPABASE_ANON_KEY`).
5. `SUPABASE_JWT_SECRET` is legacy HS256 and only used if JWKS is not configured.

## Web Auth (Supabase)
The web UI uses Supabase Auth to sign in and obtains a JWT for API requests.
1. Set `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` in `.env`.
2. Start the web UI and use the Sign In form.
3. Use Sign Up to create a new account (Supabase may require email confirmation).
4. Use “Send Reset Link” to request a password reset email.
5. After clicking the reset link, use the “Set New Password” form in the UI.
6. The UI will attach the JWT to API requests automatically.

## Automated Discovery Sources (Phase 1)
We currently support Greenhouse, Lever, Remotive, Adzuna, and Jooble adapters. Greenhouse/Lever use company slugs; Remotive/Adzuna/Jooble support keyword discovery.

Examples:
- Greenhouse: `https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true`
- Lever: `https://api.lever.co/v0/postings/{company}`
- Remotive: `https://remotive.com/api/remote-jobs?search={keyword}`
- Adzuna: `https://api.adzuna.com/v1/api/jobs/{country}/search/1?what={keyword}`
- Jooble: `https://jooble.org/api/{api_key}` (POST body includes keywords)

Configuration notes:
- Source settings live in `config/sources.yaml` or the DB-backed UI editor.
- Secrets (Adzuna/Jooble keys) are read from `.env` and merged at save/seed time.
- Use `search_profiles` to combine role + sector keywords with an optional location.

## First-Time Setup Checklist
Accounts / services:
- Supabase (Postgres + Auth)
- (Optional later) Email/Slack provider for digest delivery
- (Optional later) LLM provider for enrichment/scoring

Environment variables to set in `.env`:
- `DATABASE_URL` (Supabase Postgres connection string)
- `SUPABASE_PROJECT_REF`
- `SUPABASE_URL` (Supabase project URL for web auth)
- `SUPABASE_JWT_SECRET` (deprecated once JWKS verification is wired)
- `SUPABASE_JWT_AUDIENCE` (optional; default `authenticated`)
- `SUPABASE_ANON_KEY` (used by API to fetch JWKS on some networks)
- `SUPABASE_JWKS_URL` (optional override for JWKS URL)
- If JWKS fetch fails, the API falls back to validating the token via `auth/v1/user` (requires `SUPABASE_ANON_KEY`).
- `API_PORT` (optional)
- `API_ENV` (optional)
- `API_LOCAL_DEBUG` (optional; when true disables auth and opens CORS for local UI)
- `API_LOCAL_DEBUG_USER_ID` (optional; default `local-debug-user`)
- `VITE_API_BASE_URL` (for web)
- `VITE_SUPABASE_URL` (for web auth)
- `VITE_SUPABASE_ANON_KEY` (for web auth)
