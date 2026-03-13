# Scoring Plan (Draft)

## Goals
- Produce a fit score per job on the `jobs` record.
- Make scoring logic explicit, inspectable, and adjustable.
- Use **ideal job descriptions** as a strong signal when available.
- Keep scoring as a separate task (`score_job`) for isolation and fault tolerance.

## Inputs

User profile inputs:
- Core preferences (location, work_mode, salary, sector, target_role, company_size)
- Values + dream job description
- Resume text + chunks
- Ideal job submissions (only when `page_text` is present)

Job inputs:
- Title
- Company
- Location / remote flag
- Description text
- Source metadata

## Ideal Job Submissions (Planned Model Update)

We should adjust the ideal job data model to focus on:
- `job_description` (required)
- `explanation` (required)

Reason: if scraping fails, users can paste the job description. Scoring should **only** use ideal jobs when job description text is present.

## Scoring Output (Planned)

Store on `jobs`:
- `fit_score` (integer 0–100)
- `fit_payload` (JSONB with breakdown, matched keywords, and rationale)
- `fit_updated_at` (timestamp)

## Scoring Strategy (Initial, Transparent Heuristic)

We will start with a rule-based score to be explicit and debuggable.
Each component is additive, with hard caps.

Proposed weights (total 100):
- Role/Sector match: 30
- Location/Remote alignment: 20
- Skills overlap (resume vs job description): 25
- Values/Dream Job alignment: 15
- Ideal Job similarity: 10

Notes:
- Ideal Job similarity only applies when at least one ideal job has `job_description`.
- If no ideal jobs are available, the score should re-normalize or leave the unused weight unassigned.

## Ideal Job Similarity (High Signal)

If ideal job descriptions exist, we should compare:
- Keywords/phrases in ideal job descriptions vs current job description.
- Role title similarity.
- Domain keywords (climate/energy/policy/etc).

This component should be **stronger** than any single preference match, and we should ensure it can move the score meaningfully.

## Exclusions and Filters

We should allow an explicit exclusion list (`exclude_keywords`) that can:
- Reduce score
- Or fully disqualify a job if a hard exclusion is matched

## Task Flow (Planned)

1. `fetch_detail` task upserts the job.
2. `score_job` task runs after details are available.
3. `score_job` writes `fit_score` + `fit_payload` + `fit_updated_at` on the job.

## Open Questions

- Should weights re-normalize when inputs are missing?
- Do we introduce a minimum text length before scoring?
- Should scoring include company size or seniority matching?
