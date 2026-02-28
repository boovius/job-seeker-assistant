# Planning

## Immediate Plan (Unblocked by Supabase DNS)
1. Run locally with a local Postgres (Docker or native) to validate the pipeline end-to-end.
2. Validate the workflow pipeline locally (seed sources, enqueue, run worker, verify jobs).
3. Generate a sample config for sources (1–2 known Greenhouse/Lever companies).
4. Add adapter tests using saved payload fixtures (no DB required).

## Notes
- This plan allows progress without external network dependencies.
- Once Supabase DNS resolves, switch the `DATABASE_URL` back and re-run migrations.
