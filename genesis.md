Love this idea. This is exactly the kind of system that compounds your leverage over time.

Given your background (FastAPI + Supabase + React/React Native + LLM workflows), this is very within reach — and if designed right, it becomes a **personal job intelligence system**, not just a scraper.

Below is a thorough product plan built around:

- 🤖 Automated discovery
- ✍️ Manual URL ingestion (hybrid mode)
- 🧠 Company + role intelligence
- 🎯 Fit scoring + ranking
- 📄 Resume tailoring
- 📬 Daily decision digest
- 📊 Feedback loop to improve recommendations

---

# Product Plan: “Job Intelligence Agent”

## 1. Product Vision

> A personal AI job analyst that continuously discovers, evaluates, ranks, and helps tailor applications for high-fit roles — while learning from my preferences over time.

This is not an auto-apply bot.
This is a **high-quality filter + thinking partner**.

---

# 2. Core Modes

## Mode A: Automated Discovery

- Pull from APIs, RSS, career boards
- Normalize and dedupe
- Run scoring + enrichment
- Add to review queue

## Mode B: Hybrid Manual URL Mode (Critical)

You:

- Paste job URLs into a form
- Use a browser extension “Send to Job Agent”
- Or drop links into a Supabase table

System:

- Fetch page
- Extract structured role data
- Enrich company
- Score + tailor
- Add to queue

This avoids scraping arms races and keeps LinkedIn safe.

---

# 3. System Architecture

## High-Level Diagram (Logical Flow)

```
[SCHEDULER]
    ↓
[Ingestion Workers] ───────────────┐
    ↓                               │
[Normalized Jobs Table]             │
    ↓                               │
[Enrichment Worker]                 │
    ↓                               │
[Scoring Engine]                    │
    ↓                               │
[Shortlist Queue]                   │
    ↓                               │
[Tailoring Worker]                  │
    ↓                               │
[Digest Generator]                  │
                                     │
[Manual URL Input] ─────────────────┘
```

---

# 4. Technology Stack (Opinionated for You)

## Backend

- FastAPI (you already use this pattern)
- Supabase Postgres
- Supabase Storage (optional PDFs)
- Render Cron (nightly)
- Background workers via:

  - Celery + Redis OR
  - Supabase queue table pattern

## LLM Layer

- GPT-5.2 for:

  - Fit scoring
  - Resume tailoring

- Cheaper model for:

  - Job requirement extraction
  - Company summary

## Frontend

- Minimal React dashboard
- OR Expo app if you want this portable
- OR even Supabase + basic admin interface initially

---

# 5. Database Design (Production-Ready)

### `jobs`

| field         | type               |
| ------------- | ------------------ |
| id            | uuid               |
| canonical_url | text (unique)      |
| title         | text               |
| company_name  | text               |
| location      | text               |
| remote_flag   | boolean            |
| description   | text               |
| source_type   | enum (auto/manual) |
| date_posted   | timestamp          |
| status        | enum               |

---

### `manual_submissions`

Tracks manually pasted URLs.

| field        | type      |
| ------------ | --------- |
| id           | uuid      |
| url          | text      |
| notes        | text      |
| submitted_at | timestamp |
| status       | enum      |

---

### `companies`

| field               | type   |
| ------------------- | ------ |
| id                  | uuid   |
| name                | text   |
| website             | text   |
| climate_tags        | text[] |
| sector              | text   |
| funding_stage_guess | text   |
| company_summary     | text   |

---

### `enrichments`

| field                   | type   |
| ----------------------- | ------ |
| id                      | uuid   |
| job_id                  | uuid   |
| structured_requirements | jsonb  |
| extracted_tech_stack    | text[] |
| risks                   | text   |
| role_summary            | text   |

---

### `fit_scores`

| field            | type   |
| ---------------- | ------ |
| id               | uuid   |
| job_id           | uuid   |
| overall_score    | int    |
| dimension_scores | jsonb  |
| rationale        | text   |
| pitch_bullets    | text[] |

---

### `resume_variants`

| field            | type      |
| ---------------- | --------- |
| id               | uuid      |
| job_id           | uuid      |
| variant_markdown | text      |
| created_at       | timestamp |

---

### `user_preferences`

Stores learned filters + feedback.

| field           | type  |
| --------------- | ----- |
| id              | uuid  |
| preference_type | text  |
| value           | jsonb |

---

# 6. Fit Scoring Model

You should not rely purely on LLM vibes.

## Scoring Dimensions (Weighted)

| Dimension          | Weight |
| ------------------ | ------ |
| Mission Alignment  | 20%    |
| Tech Stack Overlap | 20%    |
| Seniority Match    | 15%    |
| Scope & Ownership  | 15%    |
| Compensation Fit   | 10%    |
| Climate Sector Fit | 10%    |
| Gap Risk           | -10%   |

---

## Scoring Method

1. Deterministic scoring:

   - Keyword overlap
   - Seniority detection
   - Location match
   - Comp threshold

2. LLM scoring:

   - Compare structured resume summary vs job
   - Generate dimension scores
   - Generate rationale

3. Combine weighted result

This makes it explainable.

---

# 7. Hybrid Manual URL Flow (Detailed)

## Option 1: Simple Paste Form

You paste a job URL into dashboard.

System:

- Fetch page
- Extract clean text
- Store snapshot
- Trigger enrichment + scoring

---

## Option 2: Browser Extension (Later Phase)

You:

- Click “Send to Job Agent”

Extension:

- Sends URL + page HTML to your API
- Avoids scraping entirely
- Keeps auth local to browser

This is extremely powerful and low risk.

---

# 8. Enrichment Phase

For each job:

1. Extract:

   - Responsibilities
   - Must-haves
   - Nice-to-haves
   - Tech stack signals

2. Company research:

   - Homepage summary
   - Climate signal detection
   - Stage detection (funded? bootstrapped?)

3. Risk detection:

   - Unrealistic requirements
   - Vague mission
   - Seniority mismatch

---

# 9. Resume Tailoring Engine

Only runs on shortlist.

Input:

- Your base resume structured
- Job structured requirements
- Company summary

Output:

- Updated professional summary
- Rewritten bullets (truthful, no fabrication)
- Keyword alignment list
- Gap warnings

You should store resume as structured JSON, not just text.

---

# 10. Daily Digest Design

Sent via email or Slack.

Example:

```
Top 3 High-Fit Roles (80+)

1. Senior Climate Data Engineer – Company X
   Score: 87
   Why:
   - Strong overlap in Django + Postgres
   - Direct climate analytics alignment
   - Ownership scope matches your PM + Eng hybrid background

2. …

5 New Mid-Fit Roles (60–75)

2 Roles Rejected Automatically:
   - Junior level
   - Hardware-heavy
```

---

# 11. Feedback Loop (Critical)

When reviewing a job:

- Accept
- Reject (choose reason)

  - Too junior
  - Too enterprise
  - Too climate-light
  - Too sales-heavy
  - Compensation too low
  - Tech mismatch

These feed into next scoring run.

You are essentially training your own recommendation engine.

---

# 12. Phased Development Plan

## Phase 1 (1–2 weeks)

- DB schema
- Manual URL ingestion
- Job parsing
- Fit scoring
- Basic dashboard list
- Email digest

No scraping yet.

---

## Phase 2

- Add automated ingestion from 2 sources
- Add company enrichment
- Add structured resume storage
- Add tailoring generation

---

## Phase 3

- Add browser extension
- Add preference learning
- Add analytics dashboard

---

# 13. Risks & Mitigations

### Risk: Over-automation

Mitigation:

- Human-in-the-loop review always required

### Risk: LLM hallucination

Mitigation:

- Structured extraction first
- Never fabricate experience
- Strict prompt instructions

### Risk: Cost blowout

Mitigation:

- Funnel architecture
- Only tailor top 3–5 daily

---

# 14. Strategic Insight

This system could become:

- A SaaS product
- A climate-specific job intelligence platform
- A “Founder Mode Job Hunter” tool

But initially — build it for you.

Given your career crossroads and interest in climate + AI + facilitation, this also becomes a **living reflection engine**:

- What jobs do you consistently reject?
- What mission themes excite you?
- Where are your real gaps?

---

# 15. My Strategic Recommendation

Start with:

✅ Manual URL ingestion
✅ Enrichment
✅ Fit scoring
❌ No scraping initially
❌ No PDF storage initially

Then layer automation.

This keeps you focused on:

- Quality over volume
- Better decision-making
- Faster tailoring

---
