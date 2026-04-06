from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from html import unescape
from typing import Any
from urllib.parse import quote_plus

import httpx

from app.services.adapters.base import FetchCursor, NormalizedJob, RawJobDetail, RawListing, SourceAdapter, SourceRegistryEntry
from app.services.adapters.query_utils import build_queries

_NEXT_DATA_RE = re.compile(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.DOTALL)


class ClimatebaseAdapter(SourceAdapter):
    slug = "climatebase"

    def __init__(self, client: httpx.Client | None = None) -> None:
        self.client = client or httpx.Client(timeout=30, follow_redirects=True)

    def fetch_listings(
        self,
        registry: SourceRegistryEntry,
        cursor: FetchCursor,
    ) -> tuple[list[RawListing], FetchCursor]:
        query_sets = build_queries(registry.config)
        if not query_sets:
            query_sets = [{"keywords": "", "location": None, "remote": None}]

        listings: list[RawListing] = []
        now = datetime.now(timezone.utc)

        for query in query_sets:
            url = _build_search_url(query)
            html = self._fetch_html(url)
            jobs = _extract_jobs_from_next_data(html)
            for job in jobs:
                listings.append(
                    RawListing(
                        source_slug=self.slug,
                        discovered_at=now,
                        url=_build_listing_url(job.get("id")),
                        external_id=_string(job.get("id")),
                        title_hint=job.get("title") or "Unknown Title",
                        company_hint=job.get("name_of_employer") or "Unknown Company",
                        location_hint=_first(job.get("locations")),
                        posted_at_hint=_parse_datetime(job.get("activation_date")),
                        raw_payload={
                            "job": job,
                            "search_url": url,
                        },
                    )
                )

        deduped: list[RawListing] = []
        seen_ids: set[str] = set()
        for listing in listings:
            dedupe_key = listing.external_id or listing.url
            if dedupe_key in seen_ids:
                continue
            seen_ids.add(dedupe_key)
            deduped.append(listing)

        return deduped, cursor

    def fetch_job_detail(self, listing: RawListing, registry: SourceRegistryEntry) -> RawJobDetail:
        now = datetime.now(timezone.utc)
        job = (listing.raw_payload or {}).get("job", {})
        search_url = (listing.raw_payload or {}).get("search_url")
        structured = {
            "job": job,
            "search_url": search_url,
        }
        return RawJobDetail(
            source_slug=self.slug,
            fetched_at=now,
            url=listing.url,
            external_id=listing.external_id,
            html=None,
            text=_description_from_summary(job),
            structured=structured,
        )

    def normalize(self, detail: RawJobDetail, listing: RawListing | None = None) -> NormalizedJob:
        job: dict[str, Any] = detail.structured.get("job", {}) if detail.structured else {}
        title = job.get("title") or (listing.title_hint if listing else "") or "Unknown Title"
        company = job.get("name_of_employer") or (listing.company_hint if listing else "") or "Unknown Company"
        location = _first(job.get("locations")) or (listing.location_hint if listing else None)
        remote_preferences = _string_list(job.get("remote_preferences"))
        sectors = _string_list(job.get("sectors"))
        job_types = _string_list(job.get("job_types"))
        summary = _description_from_summary(job)

        tags = [*sectors, *remote_preferences, *job_types]

        return NormalizedJob(
            source_slug=self.slug,
            canonical_url=detail.url,
            source_url=detail.url,
            external_id=detail.external_id,
            title=title,
            company_name=company,
            location=location,
            remote_flag=_is_remote(location, remote_preferences),
            employment_type=_first(job_types),
            seniority=None,
            description_text=summary,
            date_posted=_parse_datetime(job.get("activation_date")) or (listing.posted_at_hint if listing else None),
            tags=tags,
            tech_stack=[],
            discovered_at=listing.discovered_at if listing else None,
            fetched_at=detail.fetched_at,
            raw_fingerprint=None,
        )

    def _fetch_html(self, url: str) -> str:
        resp = self.client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        return resp.text


def _build_search_url(query: dict[str, Any]) -> str:
    params: list[str] = []
    keywords = (query.get("keywords") or "").strip()
    location = (query.get("location") or "").strip()
    remote = query.get("remote")

    if keywords:
        params.append(f"query={quote_plus(keywords)}")
    if location:
        params.append(f"location={quote_plus(location)}")
    if remote:
        params.append("remote=true")

    if not params:
        return "https://climatebase.org/jobs"
    return f"https://climatebase.org/jobs?{'&'.join(params)}"


def _build_listing_url(job_id: Any) -> str:
    if job_id in (None, ""):
        return "https://climatebase.org/jobs"
    return f"https://climatebase.org/jobs#job-{job_id}"


def _extract_jobs_from_next_data(html: str) -> list[dict[str, Any]]:
    match = _NEXT_DATA_RE.search(html)
    if not match:
        raise ValueError("Climatebase page did not contain __NEXT_DATA__ payload")

    payload = json.loads(unescape(match.group(1)))
    page_props = ((payload.get("props") or {}).get("pageProps") or {})
    jobs = page_props.get("jobs") or []
    if not isinstance(jobs, list):
        return []
    return [job for job in jobs if isinstance(job, dict)]


def _description_from_summary(job: dict[str, Any]) -> str:
    bits: list[str] = []
    summary = (job.get("employer_short_description") or "").strip()
    if summary:
        bits.append(summary)

    sectors = _string_list(job.get("sectors"))
    if sectors:
        bits.append(f"Sectors: {', '.join(sectors)}")

    locations = _string_list(job.get("locations"))
    if locations:
        bits.append(f"Locations: {', '.join(locations)}")

    remote_preferences = _string_list(job.get("remote_preferences"))
    if remote_preferences:
        bits.append(f"Remote preferences: {', '.join(remote_preferences)}")

    job_types = _string_list(job.get("job_types"))
    if job_types:
        bits.append(f"Job types: {', '.join(job_types)}")

    compensation = _compensation_text(job)
    if compensation:
        bits.append(compensation)

    return "\n".join(bits).strip() or "Climatebase listing metadata only. Full job description was not available in the public server-rendered jobs payload."


def _compensation_text(job: dict[str, Any]) -> str | None:
    salary_from = job.get("salary_from")
    salary_to = job.get("salary_to")
    period = job.get("salary_period")
    if salary_from in (None, "") and salary_to in (None, ""):
        return None

    def fmt(value: Any) -> str:
        text = str(value).strip()
        if not text:
            return text
        if text.startswith("-"):
            text = text[1:]
        if text.isdigit():
            return f"${int(text):,}"
        return text

    parts = [part for part in [fmt(salary_from), fmt(salary_to)] if part]
    if not parts:
        return None
    prefix = "Compensation: "
    if len(parts) == 2:
        prefix += f"{parts[0]} - {parts[1]}"
    else:
        prefix += parts[0]
    if period:
        prefix += f" per {period.rstrip('ly')}"
    return prefix


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _string(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value)


def _first(values: Any) -> str | None:
    if isinstance(values, list) and values:
        first = values[0]
        return str(first) if first not in (None, "") else None
    if isinstance(values, str) and values:
        return values
    return None


def _string_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    cleaned: list[str] = []
    for value in values:
        if value in (None, ""):
            continue
        cleaned.append(str(value))
    return cleaned


def _is_remote(location: str | None, remote_preferences: list[str]) -> bool:
    remote_tokens = [item.lower() for item in remote_preferences]
    if any(token in {"remote", "hybrid"} for token in remote_tokens):
        return True
    if location and "remote" in location.lower():
        return True
    return False
