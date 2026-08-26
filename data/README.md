# Job Seeker Assistant Data

This directory stores local source-of-truth job search data.

## Structure

- `experience/` — canonical experience database and source material derived from resumes, LinkedIn exports, and notes
- `stars/` — reusable STAR (Situation, Task, Action, Result) stories for interviews and applications
- `job-search-knowledge-map.md` — quick index explaining which job-search knowledge file to use for facts, narrative framing, or STAR stories
- `resumes/source/` — job-targeted resume source files in Markdown
- `resumes/exports/` — generated PDFs and other export artifacts

## Current Files

- `experience/experience-database.md`
- `experience/experience-repository.md`
- `stars/stars-database.md`
- `job-search-knowledge-map.md`
- `resumes/source/joshua-book-inaturalist-resume.md`
- `resumes/source/joshua-book-acco-resume.md`
- `resumes/source/joshua-book-acco-resume-brief.md`
- `resumes/source/joshua-book-pearl-resume.md`
- `resumes/exports/joshua-book-pearl-resume-202608.pdf`

## Next Step

Add a minimal export pipeline so Markdown resume sources can be rendered into PDF outputs reproducibly.
