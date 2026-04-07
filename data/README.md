# Job Seeker Assistant Data

This directory stores local source-of-truth job search data.

## Structure

- `experience/` — canonical experience database and source material derived from resumes, LinkedIn exports, and notes
- `stars/` — reusable STAR (Situation, Task, Action, Result) stories for interviews and applications
- `resumes/source/` — job-targeted resume source files in Markdown
- `resumes/exports/` — generated PDFs and other export artifacts

## Current Files

- `experience/experience-database.md`
- `stars/stars-database.md`
- `resumes/source/joshua-book-inaturalist-resume.md`

## Next Step

Add a minimal export pipeline so Markdown resume sources can be rendered into PDF outputs reproducibly.
