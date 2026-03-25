# Architecture and Product Definition Assessment

## Issue
#1 — Clarify job-seeker-assistant architecture and product definition

## Purpose
Provide a clearer source of truth for what this project should be, what its core workflow is, and how the current implementation should be approached going forward.

---

## Current Assessment
The project already has useful infrastructure in place:
- backend API
- Supabase auth and database
- Render deployment path
- slim frontend for user input/review

That means this is **not** an empty or useless foundation.

At the same time, the current shape feels more complex and conceptually blurry than the underlying problem really requires.

The main issue is not that the project has no value.
The main issue is that the product center of gravity is not yet defined clearly enough.

---

## Recommended Product Definition
The clearest near-term definition of this system is:

> a job opportunity gathering, scoring, review, and tracking tool designed around Josh’s specific role targets, preferences, and evaluation criteria.

In short, the core loop should be:

## Gather → Score → Review → Track

This is the most useful framing because it matches the real user need without turning the project into a vague “AI job platform.”

---

## Core User Loop

### 1. Gather
Collect candidate opportunities from selected sources.

Examples:
- manual entry
- imported job postings
- search results from selected sites
- future scheduled research runs

### 2. Score
Evaluate each opportunity against Josh’s actual criteria.

This is where the real differentiation should live.
The scoring system should be informed by:
- Josh’s climate-role target
- his company-fit preferences
- his job scorecard
- his actual taste profile, not generic job-search logic

### 3. Review
Present scored jobs in a way that makes it easier to:
- compare them
- see why they rank well or poorly
- decide what deserves energy

### 4. Track
Track job/application status over time.

Examples:
- saved
- interested
- applied
- interviewing
- rejected
- archived

---

## Why This Product Definition Is Better
This framing avoids several traps.

### It avoids becoming too many products at once
Without a clear core loop, the project risks becoming a mix of:
- job board
- CRM
- scoring engine
- assistant shell
- automation pipeline
- generic productivity tool

That makes the architecture feel confusing even when the individual parts are not bad.

### It emphasizes the actual high-value function
The valuable thing is not merely storing jobs.
The valuable thing is helping Josh:
- identify better-fit roles
- filter out weak fits
- spend energy more intelligently
- make the job search less noisy and more strategic

---

## Current Architecture: What Seems Worth Keeping
The existing stack appears useful enough that a total rewrite is probably not the best move.

### Worth preserving
- Supabase-backed persistence/auth foundation
- backend API surface
- simple frontend shell
- existing deployment path
- the general idea of a structured opportunity pipeline

This means the repo likely has enough real infrastructure to build on.

---

## What Feels Weak or Confusing

### 1. Product scope feels blurry
The system seems to be trying to be several things at once, which makes it harder to understand what the most important workflow is.

### 2. The scoring/evaluation center may not yet be tied strongly enough to Josh’s actual criteria
This is a major problem if true.
The scoring system should be driven by:
- Josh’s real role thesis
- real company-fit preferences
- real taste profile

If it is too generic, the system loses much of its value.

### 3. Architecture may be ahead of product clarity
The app has infrastructure, but the conceptual model of the workflow does not yet feel crisp enough.
That creates the feeling of a system with real parts but not enough obvious center.

---

## Recommended Direction

## Do not throw it away
There is enough real infrastructure here that starting from zero is likely unnecessary.

## Do not keep building it unchanged
That would risk deepening the current conceptual confusion.

## Best path: simplify and refocus
Use the current repo as a base, but refocus it around the core loop:

### Gather → Score → Review → Track

That likely means:
- simplifying the product definition
- clarifying the data model
- centering the scoring logic around Josh’s actual criteria
- making the review workflow more legible

---

## Recommended Conceptual Model
A likely useful near-term model would revolve around a small number of core entities.

### Candidate core entities
- **Opportunity / Job**
- **Score / Evaluation**
- **Application / Tracking State**

Potential optional supporting entities:
- source / ingestion run
- notes / reasoning
- company profile

But the goal should be to keep the conceptual center small and clear.

---

## Near-Term Architecture Recommendation

### Backend
Keep the backend, but make sure it serves the clearer loop.

### Frontend
Keep the frontend lightweight.
At this stage it should mainly support:
- review
- triage
- scoring visibility
- status updates

### Avoid overbuilding the UI
The value of the tool is not a fancy interface.
The value is a better opportunity pipeline and better judgment support.

---

## Most Important Strategic Input
This project should be strongly informed by newer planning artifacts already created outside the repo, especially:
- Josh’s job scorecard
- role-targeting work
- company-fit preferences
- the actual target company set from Notion

Without that, the system risks becoming a generic tool instead of a highly useful personal system.

---

## Recommendation on Next Work
A good next phase after this assessment would be:

### 1. Align the scoring model with Josh’s real criteria
Make sure scoring reflects actual role/company fit.

### 2. Clarify the core entities/data model
Simplify around the real workflow.

### 3. Improve the review/triage experience
Make it easier to see why jobs are promising or weak fits.

### 4. Design recurring research around this core
Once the system center is clear, scheduled job-research automation becomes much easier to design sensibly.

---

## Recommended Conclusion
The best current path is:

> **build on top of the current repo, but simplify and re-center it around a clearer product definition**.

Not:
- throw it away
- keep building it as-is
- turn it into a huge generic job platform

Instead:
- keep the useful infrastructure
- simplify the architecture mentally and conceptually
- align the scoring model with Josh’s actual needs
- orient the whole thing around gather → score → review → track

---

## Summary
This project is worth continuing.
But it likely needs **refinement of purpose more than expansion of scope**.

That is the key conclusion.

---

Prepared for issue #1 as a source-of-truth assessment.