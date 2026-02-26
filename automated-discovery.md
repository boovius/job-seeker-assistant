# Job-Seeker Automated Discovery

There are a few **“sweet spot” sources** that are both (a) high-signal and (b) realistically ingestible without playing whack-a-mole with anti-bot systems. They fall into three buckets:

1. **ATS / careers-page providers with public job-feed APIs** (best quality / easiest)
2. **Job boards with public APIs / feeds** (good coverage)
3. **Fallback scraping** (last resort; Playwright only when necessary)

Below is a practical map of what’s out there + how I’d implement Mode A.

---

## 1) The best “APIs” are actually ATS job-board feeds

A huge % of tech companies host jobs on an ATS that exposes structured listings. Instead of scraping each company’s HTML, you build **one connector per ATS**.

### Greenhouse (Job Board API)

Greenhouse provides a “Job Board API” that returns a JSON representation of published jobs. ([Greenhouse Developers][1])

**Why it’s great:** stable, structured, no browser automation required.

### Lever (Postings API + XML feed)

Lever has a “Postings API” for building custom careers sites, plus an XML feed option. ([hire.lever.co][2])

**Why it’s great:** also stable, and many startups use Lever.

### Ashby (Public Job Posting API)

Ashby offers a public job posting API for their hosted job boards. ([Ashby][3])

**Why it’s great:** increasingly common with startups; consistent.

### SmartRecruiters (Posting / Job Board APIs)

SmartRecruiters documents public posting endpoints (search postings, get posting details). ([The SmartRecruiters API Platform][4])

**Why it’s great:** structured posting search/detail endpoints.

**Pattern:** these are not “universal job APIs” across all companies—each company has its own board—but they’re consistent enough that you can ingest at scale once you know the company’s ATS.

---

## 2) True job-board / aggregator APIs (broad coverage)

These can help you cast a wide net, then let your system do the ranking.

### Remotive (remote jobs API)

Remotive provides a public API of listings (with terms about attribution/backlinking). ([Remotive][5])

### USAJOBS (federal roles)

USAJOBS provides a REST API for searching open job announcements (requires an API key). ([USAJOBS Developer Portal][6])

### Adzuna (job search API)

Adzuna provides a REST API for job ads/search. ([Adzuna API][7])

### Jooble (job search API)

Jooble has a REST API intended for embedding job search results. ([Jooble][8])

**Important tradeoff:** Aggregators can include duplicates, sometimes stale posts, and sometimes partial descriptions. They’re best as _discovery_—then you canonicalize to the original posting URL and enrich from the original source.

---

## 3) RSS feeds & “feeds without RSS”

Many job boards don’t give RSS, but they give JSON endpoints (or stable HTML pages) you can poll.

### What to look for

- RSS/Atom links in page `<head>` (rare but exists in some boards/newsletters)
- “jobs.json” / “postings” endpoints (common in ATS-hosted sites)
- XML feeds (some ATS/job boards provide these; Lever explicitly does) ([hire.lever.co][2])

**Practical tip:** Treat RSS as just another “source adapter.” If it’s RSS, you parse it. If it’s Greenhouse/Lever/Ashby, you call JSON. If neither exists, you scrape HTML.

---

## 4) If you _must_ scrape: how to go about it (and when to use Playwright)

### Golden rule

**Default to HTTP fetch + HTML parse** (requests/httpx + BeautifulSoup / readability) and only use Playwright when:

- The job content is rendered client-side and isn’t present in initial HTML
- The site blocks non-browser clients but allows normal browser loads
- You need to click “show more” to reveal the full description

### What I’d build (source adapter strategy)

Create a `SourceAdapter` interface with three implementations:

1. `ApiAdapter` (Greenhouse, Lever, Ashby, SmartRecruiters)
2. `FeedAdapter` (RSS/Atom/XML)
3. `WebAdapter`:

   - `HttpWebAdapter` (plain fetch + parse)
   - `PlaywrightWebAdapter` (only for the handful that need it)

### Playwright hygiene checklist

If you do browser automation, keep it “polite and boring”:

- Rate limit heavily (e.g., 1–3 pages/min per domain)
- Respect robots.txt where appropriate
- Cache responses; don’t refetch unchanged pages nightly
- Avoid logins (especially LinkedIn); prefer manual URL mode for those
- Save only what you need (text + canonical URL + metadata)
- Make runs idempotent (job_hash prevents duplicates)

### “Hybrid mode” is your safety valve

For the restricted sources (LinkedIn, some aggregators), lean on:

- Manual URL submission (your Mode B)
- Browser extension “Send to Agent” later (best of both worlds)

---

## 5) A sane Mode A roadmap (what I’d implement first)

### Phase 1: ATS connectors (high ROI)

- Greenhouse Job Board API ([Greenhouse Developers][1])
- Lever Postings API ([GitHub][9])
- Ashby public job posting API ([Ashby][3])
- SmartRecruiters posting endpoints ([The SmartRecruiters API Platform][4])

This alone can cover a _lot_ of climate/AI startups.

### Phase 2: Add 1–2 aggregator APIs for breadth

- Remotive (remote) ([Remotive][5])
- Adzuna or Jooble (broad) ([Adzuna API][7])

### Phase 3: Selective scraping (small whitelist)

Only for high-value boards with no API/feed.

---

## 6) How your system discovers a company’s ATS automatically

This is a big unlock:

When you see a job URL, classify the ATS by pattern:

- `boards.greenhouse.io/<company>` → Greenhouse
- `jobs.lever.co/<company>` → Lever
- `jobs.ashbyhq.com/<company>` → Ashby ([Ashby][3])
- `jobs.smartrecruiters.com/<company>` → SmartRecruiters

Then route to the correct adapter.

---

## 7) The “best practice” design choice for you

Given you want a nightly job:

- **Mode A**: pull from ATS APIs + a couple clean aggregators
- **Mode B**: manual URL input for everything brittle/restricted
- **Playwright**: only a small, whitelisted set of domains

This keeps maintenance low and avoids ToS/account headaches.

---

[1]: https://developers.greenhouse.io/job-board.html?utm_source=chatgpt.com "Introduction – Job Board API"
[2]: https://hire.lever.co/developer?utm_source=chatgpt.com "Lever Developer"
[3]: https://developers.ashbyhq.com/docs/public-job-posting-api?utm_source=chatgpt.com "Ashby Job Postings API"
[4]: https://developers.smartrecruiters.com/docs/endpoints?utm_source=chatgpt.com "Endpoints"
[5]: https://remotive.com/remote-jobs/api?utm_source=chatgpt.com "Remote Jobs API"
[6]: https://developer.usajobs.gov/api-reference/?utm_source=chatgpt.com "USAJOBS - API Reference"
[7]: https://developer.adzuna.com/docs/search?utm_source=chatgpt.com "Search ads"
[8]: https://jooble.org/api/about?utm_source=chatgpt.com "Jooble REST API"
[9]: https://github.com/lever/postings-api?utm_source=chatgpt.com "lever/postings-api: API documentation and examples for ..."

---

# Adding Climatebase to Mode A (Automated Discovery)

## First: Important constraint

Climatebase does **not** currently provide a widely documented public jobs API.

That means:

- No official open REST endpoint (like Greenhouse/Lever).
- Most listings are rendered via web frontend.
- Scraping must respect their ToS.
- Logged-in scraping is risky.
- Browser automation should be minimal and polite.

So the right approach is:

> Prefer public search pages + structured parsing
> Avoid account-required scraping
> Lean on hybrid mode when necessary

---

# Climatebase Integration Strategy

We’ll design this as a first-class SourceAdapter:

```
SourceAdapter
 ├── ATSAdapter (Greenhouse, Lever, etc.)
 ├── AggregatorAdapter (Remotive, etc.)
 ├── ClimatebaseAdapter  ← NEW
 └── ManualURLAdapter
```

---

# Climatebase Ingestion Plan

## Step 1: Public Search Fetch

Most climate job boards have search endpoints like:

```
/jobs?search=...
/jobs?location=...
/jobs?category=...
```

You:

- Use HTTP fetch (httpx)
- Avoid login cookies
- Respect rate limits
- Only fetch paginated listing pages

No Playwright initially.

---

## Step 2: Extract Listing URLs

From search results page:

- Extract job title
- Company
- Location
- URL
- Date posted (if available)

Store minimal metadata.

---

## Step 3: Fetch Individual Job Page

For each new job URL:

- Fetch HTML via HTTP (no browser)
- Extract:

  - Full job description
  - Company link
  - Tags (climate sector)
  - Remote flag
  - Salary (if present)

Only fall back to Playwright if:

- Description text not present in initial HTML
- Page loads empty without JS

In most cases, modern boards include the text in HTML.

---

# Rate Limiting Strategy

Very important to not look like a scraper bot.

For Climatebase:

- Max 1 request per 3–5 seconds
- Cache previously fetched URLs
- Only re-fetch if last seen > 24h
- Use ETag / Last-Modified if available
- Identify with clear user-agent string

Example:

```
User-Agent: JoshuaBook-JobAgent/1.0 (contact: your-email)
```

This signals good faith.

---

# When to Use Playwright

Only if:

- Search pages render zero job listings without JS
- Individual job descriptions require JS execution

If needed:

- Headless
- Low concurrency
- No login
- 1 browser context per run
- Close cleanly

Playwright should be a small helper, not the default ingestion engine.

---

# Climatebase Adapter Design

### Adapter responsibilities:

```
fetch_search_pages()
parse_listing_urls()
fetch_job_detail(url)
normalize_to_job_schema()
```

---

# Normalized Job Object (Example)

```python
class NormalizedJob(BaseModel):
    source: str
    canonical_url: str
    title: str
    company: str
    location: Optional[str]
    remote_flag: bool
    description: str
    date_posted: Optional[datetime]
    climate_tags: list[str]
```

Climatebase-specific tags like:

- Carbon Removal
- Climate SaaS
- Energy
- AgTech
- Climate Finance

These feed directly into your scoring dimension:
`Climate Sector Fit`.

---

# Hybrid Mode Integration

Climatebase will often show:

- “Apply via company site”
- “Apply on Climatebase”

If a role looks strong:

You:

- Paste the original company job URL into Manual Mode

This ensures:

- You score the canonical posting
- You tailor against the real ATS version
- You avoid duplications

---

# De-duplication Strategy

Climatebase listings often mirror:

- Greenhouse
- Lever
- Ashby

So dedupe using:

1. Canonical URL
2. Title + company fuzzy match
3. Job hash of first 500 characters

If Climatebase listing links to Greenhouse, prefer the Greenhouse URL.

---

# Climatebase in Your Weighted Model

Add a slight source boost:

```
if source == "climatebase":
    mission_alignment += 5
```

Not too much — but enough to reflect higher base relevance.

---

# Legal / Ethical Guardrails

- No login scraping
- No bulk crawling entire site
- Only query filtered search URLs relevant to you
- Store minimal data needed
- Respect robots.txt
- If they publish API later → migrate

If you ever want to productize this, you'd want to reach out for permission.

---

# Suggested Mode A Stack (With Climatebase)

### Tier 1: ATS APIs (Most Stable)

- Greenhouse
- Lever
- Ashby
- SmartRecruiters

### Tier 2: Climate-Focused Aggregation

- Climatebase (public ingestion)
- Remotive (remote roles)

### Tier 3: Selective Scraping

- Only whitelisted domains
- Only public pages
- Only when no API exists

### Tier 4: Manual URL (Hybrid Mode)

- LinkedIn
- Indeed
- Direct referrals
- VC portfolio job pages

---

# What This Gives You

With Climatebase integrated:

- Daily climate-native pipeline
- Strong sector tagging
- Higher baseline mission alignment
- Less noise than Indeed/LinkedIn

And critically:
You still remain in control.

---

Here’s a concrete Mode A spec you can implement with FastAPI + Supabase + (optional) Redis, with:

1. **source_registry format** (DB rows + YAML equivalent)
2. **adapter contracts** (Pydantic models + interfaces)
3. **pipeline diagram** with **fetch → normalize → dedupe → enrich** + **retry/lease semantics**
4. **ClimatebaseAdapter pseudo-implementation**
5. **example YAML source_registry**
6. how to make it configurable + recommendation/weighting system for future users

This is opinionated toward reliability + low-maintenance.

---

## 1) Source registry format

### Option A: DB tables (recommended for production)

This lets you enable/disable sources per user, change weights without redeploying, and store per-source cursor state.

**Tables**

- `sources` — global definitions (Climatebase, Greenhouse, Remotive, etc.)
- `user_sources` — per-user enablement + weights + filters
- `source_cursors` — per-user per-source pagination/cursor state (optional)

**`sources`**

- `id` (uuid)
- `slug` (text unique) e.g. `climatebase`
- `adapter` (text) e.g. `climatebase_v1`
- `kind` (enum: `ats_api`, `job_board`, `rss`, `search`, `scrape`)
- `base_url` (text)
- `default_config` (jsonb) (rate limits, parser rules)
- `created_at`, `updated_at`

**`user_sources`**

- `id` (uuid)
- `user_id` (uuid)
- `source_id` (uuid)
- `enabled` (bool)
- `weight` (float, default 1.0)
- `filters` (jsonb) (query terms, locations, remote-only, etc.)
- `schedule` (jsonb) (nightly vs hourly, etc.)

**`source_cursors`**

- `id` (uuid)
- `user_id`, `source_id`
- `cursor` (jsonb) (page number, last_seen_date, etc.)
- `etag` (text nullable)
- `last_modified` (text nullable)
- `updated_at`

### Option B: YAML (excellent for MVP)

YAML can be loaded at boot and/or stored in Supabase as a blob.

---

## 2) Adapter contracts (Pydantic + “interfaces”)

### Core normalized types

```python
from __future__ import annotations
from typing import Any, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field

SourceKind = Literal["ats_api", "job_board", "rss", "search", "scrape"]
FetchMode = Literal["http", "playwright"]

class SourceRegistryEntry(BaseModel):
    slug: str
    adapter: str
    kind: SourceKind
    base_url: HttpUrl
    enabled: bool = True
    weight: float = 1.0

    # How to fetch
    fetch_mode: FetchMode = "http"
    rate_limit_rps: float = 0.2  # 1 req / 5s default
    concurrency: int = 2

    # Source-specific config
    config: dict[str, Any] = Field(default_factory=dict)

class UserSourceOverrides(BaseModel):
    enabled: Optional[bool] = None
    weight: Optional[float] = None
    filters: dict[str, Any] = Field(default_factory=dict)

class FetchCursor(BaseModel):
    # flexible cursor so adapters can store what they need
    state: dict[str, Any] = Field(default_factory=dict)

class RawListing(BaseModel):
    """
    A lightweight result from a source search page/feed.
    """
    source_slug: str
    discovered_at: datetime
    url: HttpUrl
    external_id: Optional[str] = None

    title_hint: Optional[str] = None
    company_hint: Optional[str] = None
    location_hint: Optional[str] = None
    posted_at_hint: Optional[datetime] = None

    # helpful to debug parsing changes
    raw_snippet: Optional[str] = None
    raw_payload: Optional[dict[str, Any]] = None

class RawJobDetail(BaseModel):
    """
    Detailed job page data extracted by the adapter (still source-shaped).
    """
    source_slug: str
    fetched_at: datetime
    url: HttpUrl
    external_id: Optional[str] = None
    html: Optional[str] = None
    text: Optional[str] = None
    structured: dict[str, Any] = Field(default_factory=dict)

class NormalizedJob(BaseModel):
    """
    Canonical schema used by downstream pipeline.
    """
    source_slug: str
    canonical_url: HttpUrl
    source_url: HttpUrl
    external_id: Optional[str] = None

    title: str
    company_name: str
    location: Optional[str] = None
    remote_flag: bool = False
    employment_type: Optional[str] = None
    seniority: Optional[str] = None

    description_text: str
    date_posted: Optional[datetime] = None

    # signals / tags
    tags: list[str] = Field(default_factory=list)
    tech_stack: list[str] = Field(default_factory=list)

    # provenance
    discovered_at: datetime
    fetched_at: datetime
    raw_fingerprint: Optional[str] = None  # e.g. hash of description
```

### Adapter “interface”

Python doesn’t need formal interfaces, but define a base class contract:

```python
from abc import ABC, abstractmethod
from typing import Iterable

class SourceAdapter(ABC):
    slug: str

    @abstractmethod
    def fetch_listings(
        self,
        registry: SourceRegistryEntry,
        user_overrides: UserSourceOverrides,
        cursor: FetchCursor,
    ) -> tuple[list[RawListing], FetchCursor]:
        """
        Returns new candidate listing URLs + updated cursor.
        Must be idempotent and safe to rerun.
        """

    @abstractmethod
    def fetch_job_detail(
        self,
        listing: RawListing,
        registry: SourceRegistryEntry,
    ) -> RawJobDetail:
        """
        Fetches and extracts details for a single listing URL.
        """

    @abstractmethod
    def normalize(
        self,
        detail: RawJobDetail,
        listing: Optional[RawListing] = None,
    ) -> NormalizedJob:
        """
        Map source-shaped detail into NormalizedJob.
        """
```

---

## 3) Pipeline: fetch → normalize → dedupe → enrich + retry/lease semantics

### High-level pipeline diagram

```
┌─────────────────────────────┐
│ Scheduler (nightly)         │
└──────────────┬──────────────┘
               │ creates PipelineRun + enqueues jobs
               v
┌─────────────────────────────┐
│ FETCH_LISTINGS (per source) │  (lease + retries)
└──────────────┬─────────────┘
               │ RawListing[]
               v
┌─────────────────────────────┐
│ FETCH_DETAIL (per listing)  │  (lease + retries)
└──────────────┬──────────────┘
               │ RawJobDetail
               v
┌─────────────────────────────┐
│ NORMALIZE                   │  (deterministic)
└──────────────┬──────────────┘
               │ NormalizedJob
               v
┌─────────────────────────────┐
│ DEDUPE / CANONICALIZE        │  (idempotent upsert)
└──────────────┬──────────────┘
               │ job_id
               v
┌────────────────────────────┐
│ ENRICH (LLM + web fetch)     │  (lease + retries)
└──────────────┬──────────────┘
               │ enrichment rows
               v
┌─────────────────────────────┐
│ SCORE + SHORTLIST            │
└─────────────────────────────┘
```

### Queue model + lease semantics (works in Postgres)

You can implement a durable queue using a table like `work_items`.

**`work_items` fields**

- `id` uuid
- `run_id` uuid
- `step` enum (`fetch_listings`, `fetch_detail`, `enrich`, `score`, `tailor`)
- `payload` jsonb (source_slug, url, job_id, etc.)
- `status` enum (`queued`, `leased`, `succeeded`, `failed`, `dead`)
- `attempts` int
- `lease_expires_at` timestamp
- `last_error` text
- `created_at`, `updated_at`

**Lease algorithm (single SQL pattern)**

- Worker “claims” a job by atomically updating one queued item:

  - `status='leased'`
  - `lease_expires_at = now() + interval '5 minutes'`
  - increments `attempts`

- If worker dies, lease expires, another worker can reclaim.

Pseudo-SQL:

```sql
WITH cte AS (
  SELECT id FROM work_items
  WHERE status IN ('queued', 'leased')
    AND (status = 'queued' OR lease_expires_at < now())
    AND step = $1
  ORDER BY created_at
  LIMIT 1
  FOR UPDATE SKIP LOCKED
)
UPDATE work_items
SET status = 'leased',
    lease_expires_at = now() + interval '5 minutes',
    attempts = attempts + 1,
    updated_at = now()
WHERE id IN (SELECT id FROM cte)
RETURNING *;
```

### Retry policy (practical)

- attempts 1–3: exponential backoff (e.g., 1m, 5m, 30m)
- after 5 attempts: mark `dead` and record last error
- distinguish:

  - 404 → “succeeded but removed” (don’t retry)
  - 429/503 → retry
  - parse error → retry once, then dead (likely parser mismatch)

### Dedupe / canonicalization strategy

You want deterministic upserts so reruns are safe.

Store in `jobs` with a unique constraint on `canonical_url`.

Canonical URL rules:

- strip tracking params (`utm_*`, `gh_src`, etc.)
- if Climatebase links to greenhouse/lever/etc., prefer the ATS URL as canonical
- fallback to the source URL

Also compute:

- `description_hash = sha256(normalized_description_text)`
- `job_key = sha256(company + title + location + first_500_chars)`

Use these for fuzzy dedupe when canonical_url differs.

---

## 4) Concrete ClimatebaseAdapter pseudo-implementation

This assumes:

- You’ll try HTTP first.
- Fall back to Playwright only if the search page doesn’t expose listing links or the detail page is empty.

```python
import re
import hashlib
from datetime import datetime, timezone
from typing import Optional
from bs4 import BeautifulSoup
import httpx

TRACKING_PARAMS = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"}

def canonicalize_url(url: str) -> str:
    # very small canonicalizer; you’ll probably want a real one
    # strip known tracking query params
    from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
    parts = urlsplit(url)
    q = [(k, v) for k, v in parse_qsl(parts.query) if k not in TRACKING_PARAMS]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(q), ""))

def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

class ClimatebaseAdapter(SourceAdapter):
    slug = "climatebase"

    def __init__(self, client: httpx.Client):
        self.client = client

    def fetch_listings(self, registry, user_overrides, cursor):
        """
        Strategy: fetch a filtered search/list page, parse job links.
        cursor.state could store page number or last_seen_url set.
        """
        filters = user_overrides.filters or {}
        queries = filters.get("queries", [""])
        locations = filters.get("locations", [])
        remote_only = filters.get("remote_only", False)

        page = int(cursor.state.get("page", 1))
        max_pages = int(registry.config.get("max_pages_per_run", 3))

        discovered: list[RawListing] = []
        now = datetime.now(timezone.utc)

        for q in queries:
            # NOTE: This URL shape is illustrative—adapt to the real Climatebase URL pattern you target.
            # Keep config-driven so you can change without code deploy.
            template = registry.config.get("search_url_template")
            if not template:
                raise ValueError("Missing config.search_url_template for climatebase")
            for p in range(page, page + max_pages):
                url = template.format(query=q, page=p)
                if locations:
                    # you can incorporate location into template or add query args
                    pass
                if remote_only:
                    pass

                html = self._http_get_text(url, registry)
                links = self._parse_listing_links(html, registry)

                for link in links:
                    discovered.append(RawListing(
                        source_slug=self.slug,
                        discovered_at=now,
                        url=link,
                    ))

        # Update cursor: advance page (simple). Better: store last_seen_date if available.
        cursor.state["page"] = page + max_pages
        return discovered, cursor

    def fetch_job_detail(self, listing, registry):
        now = datetime.now(timezone.utc)
        html = self._http_get_text(str(listing.url), registry)

        # If page is JS-rendered and html contains no content, fallback to playwright (optional)
        if self._looks_empty(html, registry) and registry.fetch_mode == "playwright":
            html = self._playwright_get_html(str(listing.url), registry)

        text = self._extract_job_text(html, registry)
        structured = self._extract_job_structured(html, registry)

        return RawJobDetail(
            source_slug=self.slug,
            fetched_at=now,
            url=listing.url,
            html=html,
            text=text,
            structured=structured,
        )

    def normalize(self, detail, listing=None):
        s = detail.structured

        title = s.get("title") or (listing.title_hint if listing else None) or "Unknown Title"
        company = s.get("company") or (listing.company_hint if listing else None) or "Unknown Company"
        location = s.get("location") or (listing.location_hint if listing else None)
        remote_flag = bool(s.get("remote_flag", False))
        date_posted = s.get("date_posted")

        description = detail.text or ""
        description_clean = self._clean_text(description)
        fingerprint = sha256_text(description_clean[:2000]) if description_clean else None

        source_url = str(detail.url)
        canonical = canonicalize_url(source_url)

        return NormalizedJob(
            source_slug=self.slug,
            source_url=source_url,
            canonical_url=canonical,
            external_id=s.get("external_id"),
            title=title.strip(),
            company_name=company.strip(),
            location=location,
            remote_flag=remote_flag,
            employment_type=s.get("employment_type"),
            seniority=s.get("seniority"),
            description_text=description_clean,
            date_posted=date_posted,
            tags=s.get("tags", []),
            tech_stack=s.get("tech_stack", []),
            discovered_at=(listing.discovered_at if listing else detail.fetched_at),
            fetched_at=detail.fetched_at,
            raw_fingerprint=fingerprint,
        )

    # -----------------
    # Helpers
    # -----------------
    def _http_get_text(self, url: str, registry) -> str:
        resp = self.client.get(
            url,
            headers={"User-Agent": registry.config.get("user_agent", "JobAgent/1.0")},
            timeout=registry.config.get("timeout_s", 30),
            follow_redirects=True,
        )
        resp.raise_for_status()
        return resp.text

    def _parse_listing_links(self, html: str, registry) -> list[str]:
        soup = BeautifulSoup(html, "html.parser")

        # Config-driven selector is key; you’ll update this if the site changes.
        selector = registry.config.get("listing_link_selector", "a")
        anchors = soup.select(selector)

        urls: list[str] = []
        for a in anchors:
            href = a.get("href")
            if not href:
                continue
            if self._is_job_link(href, registry):
                urls.append(self._to_absolute(href, str(registry.base_url)))
        return list(dict.fromkeys(urls))  # preserve order, dedupe

    def _is_job_link(self, href: str, registry) -> bool:
        # config regex for job links
        pat = registry.config.get("job_url_regex")
        if not pat:
            return "/jobs/" in href  # fallback heuristic
        return re.search(pat, href) is not None

    def _extract_job_text(self, html: str, registry) -> str:
        soup = BeautifulSoup(html, "html.parser")

        # Try a configured container first
        desc_sel = registry.config.get("description_selector")
        if desc_sel:
            node = soup.select_one(desc_sel)
            if node:
                return node.get_text("\n", strip=True)

        # Fallback: whole page text (not ideal, but workable)
        return soup.get_text("\n", strip=True)

    def _extract_job_structured(self, html: str, registry) -> dict:
        soup = BeautifulSoup(html, "html.parser")

        # Config-driven selectors
        title_sel = registry.config.get("title_selector")
        company_sel = registry.config.get("company_selector")
        location_sel = registry.config.get("location_selector")

        title = soup.select_one(title_sel).get_text(strip=True) if title_sel and soup.select_one(title_sel) else None
        company = soup.select_one(company_sel).get_text(strip=True) if company_sel and soup.select_one(company_sel) else None
        location = soup.select_one(location_sel).get_text(strip=True) if location_sel and soup.select_one(location_sel) else None

        tags = []
        tag_sel = registry.config.get("tag_selector")
        if tag_sel:
            tags = [n.get_text(strip=True) for n in soup.select(tag_sel)]

        # Remote heuristic
        remote_flag = False
        if location and "remote" in location.lower():
            remote_flag = True

        return {
            "title": title,
            "company": company,
            "location": location,
            "remote_flag": remote_flag,
            "tags": tags,
        }

    def _looks_empty(self, html: str, registry) -> bool:
        # simplistic; you can check for “enable javascript” boilerplate etc.
        min_len = int(registry.config.get("min_html_len", 1500))
        return len(html or "") < min_len

    def _playwright_get_html(self, url: str, registry) -> str:
        # pseudo: you’d implement in a separate module to avoid heavy deps everywhere
        raise NotImplementedError("Playwright fetch not implemented in pseudo")

    def _to_absolute(self, href: str, base_url: str) -> str:
        from urllib.parse import urljoin
        return urljoin(base_url, href)

    def _clean_text(self, text: str) -> str:
        # normalize whitespace, remove repeated blank lines
        lines = [ln.strip() for ln in text.splitlines()]
        lines = [ln for ln in lines if ln]
        return "\n".join(lines)
```

Key design choices:

- **Selectors/regex live in config** so a site change is a config update, not code redeploy.
- Keep Playwright isolated.

---

## 5) Draft YAML `source_registry` config

Here’s an MVP YAML that supports:

- ATS APIs (Greenhouse/Lever/Ashby)
- Climatebase via scrape/http
- Remotive via API
- Source weights + per-user overrides conceptually

```yaml
version: 1

defaults:
  user_agent: "JoshuaBook-JobAgent/1.0"
  timeout_s: 30

sources:
  - slug: climatebase
    adapter: climatebase_v1
    kind: job_board
    base_url: "https://climatebase.org"
    enabled: true
    weight: 1.25
    fetch_mode: http
    rate_limit_rps: 0.2
    concurrency: 2
    config:
      user_agent: "JoshuaBook-JobAgent/1.0 (contact: you@example.com)"
      timeout_s: 30
      max_pages_per_run: 3

      # These are intentionally config-driven:
      # You'll tune them to the actual Climatebase pages you target.
      search_url_template: "https://climatebase.org/jobs?query={query}&page={page}"
      job_url_regex: "/job/|/jobs/"
      listing_link_selector: "a"
      title_selector: "h1"
      company_selector: "[data-testid='company-name'], a[href*='/company/'], .company"
      location_selector: "[data-testid='job-location'], .location"
      description_selector: "[data-testid='job-description'], .job-description, article"
      tag_selector: "[data-testid='job-tag'], .tag"

  - slug: greenhouse
    adapter: greenhouse_job_board_v1
    kind: ats_api
    base_url: "https://boards.greenhouse.io"
    enabled: true
    weight: 1.1
    fetch_mode: http
    rate_limit_rps: 1.0
    concurrency: 5
    config:
      # Example: you may keep a list of target companies or discover them via other sources
      companies:
        - "climeworks"
        - "watershed"
      job_board_endpoint_template: "https://boards-api.greenhouse.io/v1/boards/{company}/jobs"

  - slug: lever
    adapter: lever_postings_v1
    kind: ats_api
    base_url: "https://jobs.lever.co"
    enabled: true
    weight: 1.1
    fetch_mode: http
    rate_limit_rps: 1.0
    concurrency: 5
    config:
      companies:
        - "patch"
        - "charmindustrial"
      postings_endpoint_template: "https://api.lever.co/v0/postings/{company}?mode=json"

  - slug: ashby
    adapter: ashby_public_postings_v1
    kind: ats_api
    base_url: "https://jobs.ashbyhq.com"
    enabled: true
    weight: 1.05
    fetch_mode: http
    rate_limit_rps: 1.0
    concurrency: 5
    config:
      companies:
        - "heirloom"
      # You’ll configure the correct endpoint shape for Ashby’s public postings per their docs

  - slug: remotive
    adapter: remotive_api_v1
    kind: job_board
    base_url: "https://remotive.com"
    enabled: true
    weight: 0.9
    fetch_mode: http
    rate_limit_rps: 2.0
    concurrency: 5
    config:
      endpoint: "https://remotive.com/api/remote-jobs"
      categories:
        - "software-dev"
      keywords:
        - "climate"
        - "sustainability"
        - "carbon"
```

In production, you’d store “companies” and user filters in DB rather than YAML.

---

## 6) Making sources configurable + “recommended weighting” for future users

You want **two layers**:

### Layer 1: Source quality weights (system defaults)

You (the product) maintain recommended defaults:

- `source_weight_default`
- `confidence_modifier` (how reliable the metadata is)
- `freshness_modifier` (if a source is often stale)
- `dedupe_priority` (prefer ATS canonical URLs)

Example defaults:

- Greenhouse/Lever/Ashby: **1.10** (high quality)
- Climatebase: **1.25** (high relevance but might duplicate ATS)
- Broad aggregators: **0.85** (lots of duplicates/noise)

### Layer 2: User preference weights + per-source enablement

Each user can:

- enable/disable sources
- set weights (simple slider)
- optionally specify “trusted sources” and “avoid sources”

### How weights actually affect output (clean + explainable)

Use weights as a multiplier in scoring:

`final_score = base_fit_score * source_weight * freshness_weight * confidence_weight`

Where:

- `freshness_weight` boosts newly posted jobs
- `confidence_weight` penalizes sources with partial info (e.g. aggregator with no full description)

### Recommendations engine for “which sources to focus on”

As users interact, compute per-source performance:

- accept rate (shortlisted / seen)
- apply rate (applied / seen)
- interview rate (interviews / applied)
- time-to-yes (optional)

Then suggest:

- “Climatebase is producing high-fit roles for you. Increase weight from 1.0 → 1.3”
- “Aggregator X has low yield and high duplicates. Consider disabling.”

This becomes a personalized source strategy over time.

### UI idea (simple, powerful)

A “Sources” settings page:

For each source:

- Enabled toggle
- Weight slider (0.0–2.0)
- “Recommended” badge (system)
- “Your yield” stats (accept/apply/interview)

---

## Implementation notes that will save you pain

- Keep **adapters pure + deterministic**. No LLM inside adapters. Adapters produce `NormalizedJob`.
- All **LLM happens in Enrich / Score** stages only.
- Put **selectors/regex in config**. Sites change; code shouldn’t.
- Use **lease-based work_items** in Postgres unless you _really_ need Redis.

---

# Plan-Of-Action (Concise)
1. Add source registry tables (`sources`, `user_sources`, `source_cursors`) to support configurable ingestion.
2. Add adapter interface + registry so new sources can be plugged in without touching pipeline logic.
3. Add workflow task types for `fetch_listings` and `fetch_detail`, using the queue runner.
4. Implement first two adapters (Greenhouse + Lever) and test with a short company allowlist.
5. Add dedupe + upsert logic into `jobs` and enqueue enrichment/scoring.

## Execution Status
- Completed: Step 1 and Step 2 scaffolding.
- Completed: Step 3 workflow task support (`fetch_listings`, `fetch_detail`).
- In progress: Step 4 adapters (Greenhouse + Lever).
