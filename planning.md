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

## Major Change 2: Periodic Pipeline (Scheduled Runs)
Goal: run the full discovery pipeline on a schedule (daily or a few times per week).

Steps:
1. Add a `pipeline_runs` table (run id, started_at, finished_at, status, summary).
2. Add a single API endpoint to kick off a full run (enqueue fetch_listings for all enabled sources).
3. Implement a top-level runner that:
   - starts a run
   - enqueues tasks for all enabled sources
   - waits for completion or returns a run id for monitoring
4. Add a scheduler (Render Cron) that calls the kickoff endpoint on a cadence (daily / 3x weekly).
5. Add observability:
   - list recent runs + counts (queued/succeeded/failed)
   - alert on repeated failures (email/Slack later)

## Notes

- This plan allows progress without external network dependencies.
- Once Supabase DNS resolves, switch the `DATABASE_URL` back and re-run migrations.

## Completed

1. Run locally with a local Postgres (Docker or native) to validate the pipeline end-to-end.
