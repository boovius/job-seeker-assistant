# Planning

## Immediate Plan (Unblocked by Supabase DNS)

1. Validate the workflow pipeline locally (seed sources, enqueue, run worker, verify jobs).
1. Generate a sample config for sources (1–2 known Greenhouse/Lever companies).
1. update jobs nomenclature to something non-overloading term jobs, we are keeping track of "employment opportunities", let's use the term Opportunity instead of Job
1. don't want to force the user to define exact companies for Greenhouse/Lever/etc. but instead define types of Opportunities, i.e. keywords
1. want user to be able to provide a config probably a YAML that has data about what user is looking for, i.e. keywords
1. Add adapter tests using saved payload fixtures (no DB required).

## Major Change 1: Keyword-Based Discovery (Not Company Lists)
Goal: fetch opportunities by role/sector keywords (e.g., "technical product manager", "climate"), not by a hardcoded company list.

Steps:
1. Define a user-facing source config (YAML or DB JSON) that includes keyword queries, optional locations, and remote preference.
2. Update adapter interfaces to accept a `filters` object (keywords, locations, seniority) and incorporate them into fetch requests where supported.
3. Add a registry layer that maps keywords -> sources (e.g., Remotive supports keywords; Greenhouse/Lever do not).
4. Add a "search-first" source type (aggregators/boards) for keyword discovery, then resolve canonical URLs to ATS when possible.
5. Update dedupe rules to prioritize canonical ATS URLs when found from keyword sources.

Follow-on additions:
1. Add additional keyword sources (Adzuna, Jooble) as adapter plugins.
2. Switch config storage from env vars to a YAML config file (with optional DB overrides).

## Major Change 2: Periodic Pipeline (Scheduled Runs)
Goal: run the full discovery pipeline on a schedule (daily or a few times per week).

Scheduling options (summary):
1. Option 1: Local scheduler (CLI + cron).
   Pros: fast to implement, easy to test, minimal infra.
   Cons: schedule lives outside the app, no central audit, not hosted.
2. Option 2: Render Cron Job (HTTP trigger).
   Pros: hosted schedule, simple trigger.
   Cons: Render-specific, no per-user cadence without DB logic, limited audit.
3. Option 3: DB-backed schedule (policy in DB + trigger).
   Pros: central/auditable, multi-user, UI-configurable later.
   Cons: more schema/code, still needs a trigger.

Chosen now: Option 1 (local scheduler). Option 2/3 can be layered later.

Steps:
1. Add a `run-pipeline` CLI command that enqueues all sources then runs the worker loop.
2. Document a local cron example that runs `python scripts/cli.py run-pipeline`.
3. (Later) add `pipeline_runs` table for audit and run summaries.
4. (Later) add an API endpoint to kick off a full run.
5. (Later) add Render Cron or a scheduler service to trigger the endpoint.

## Notes

- This plan allows progress without external network dependencies.
- Once Supabase DNS resolves, switch the `DATABASE_URL` back and re-run migrations.

## Future: Resume Chunking + Embeddings
Goal: make resume text usable for RAG/scoring by chunking into semantic sections and storing embeddings.

Steps:
1. Add `user_resume_chunks` table (user_id, chunk_text, chunk_index, embedding, metadata).
2. Chunk resumes on save (by headings or max tokens).
3. Generate embeddings for chunks (provider: OpenAI or local).
4. Use top-k chunks for job fit scoring and query generation.

## Future: pgvector Adoption
Goal: move resume/job embeddings to native Postgres vector type for fast similarity search.

Steps:
1. Enable pgvector extension in Supabase.
2. Migrate embeddings from JSONB to vector columns.
3. Add indexes (IVFFlat/HNSW) for similarity queries.
4. Implement top-k retrieval queries for resume/job matching.

## Future: Top Rated Companies Alerts
Goal: monitor a curated list of top-rated companies for new openings and alert users.

Steps:
1. Store user’s top-rated companies list (manual input or imported source).
2. Run periodic checks for new openings at those companies.
3. Generate notifications across channels (email, SMS, WhatsApp, Signal, Slack).
4. Track alert delivery and user preferences.

## Maintenance Note
As this planning doc grows, consider restructuring into phases and grouped themes for readability.

## Completed

1. Run locally with a local Postgres (Docker or native) to validate the pipeline end-to-end.
