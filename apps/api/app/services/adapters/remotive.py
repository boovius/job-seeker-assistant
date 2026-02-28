from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from app.services.adapters.base import FetchCursor, NormalizedJob, RawJobDetail, RawListing, SourceAdapter, SourceRegistryEntry
from app.services.adapters.query_utils import build_queries


class RemotiveAdapter(SourceAdapter):
    slug = "remotive"

    def __init__(self, client: httpx.Client | None = None) -> None:
        self.client = client or httpx.Client(timeout=30)

    def fetch_listings(
        self,
        registry: SourceRegistryEntry,
        cursor: FetchCursor,
    ) -> tuple[list[RawListing], FetchCursor]:
        base_url = registry.config.get("endpoint", "https://remotive.com/api/remote-jobs")
        keywords = registry.config.get("keywords", [])
        categories = registry.config.get("categories", [])
        profiles = build_queries(registry.config)

        listings: list[RawListing] = []
        now = datetime.now(timezone.utc)

        # Profile-based keyword searches
        if profiles:
            for profile in profiles:
                query = profile.get("keywords", "")
                if not query:
                    continue
                payload = self._fetch(base_url, {"search": query})
                listings.extend(self._to_listings(payload, now))
        elif keywords or categories:
            for kw in keywords:
                payload = self._fetch(base_url, {"search": kw})
                listings.extend(self._to_listings(payload, now))

            for cat in categories:
                payload = self._fetch(base_url, {"category": cat})
                listings.extend(self._to_listings(payload, now))
        else:
            payload = self._fetch(base_url, {})
            listings.extend(self._to_listings(payload, now))

        # Deduplicate by URL
        seen: set[str] = set()
        deduped: list[RawListing] = []
        for item in listings:
            if item.url in seen:
                continue
            seen.add(item.url)
            deduped.append(item)

        return deduped, cursor

    def fetch_job_detail(self, listing: RawListing, registry: SourceRegistryEntry) -> RawJobDetail:
        now = datetime.now(timezone.utc)
        if listing.raw_payload and "job" in listing.raw_payload:
            job = listing.raw_payload["job"]
            description = job.get("description") or ""
            return RawJobDetail(
                source_slug=self.slug,
                fetched_at=now,
                url=listing.url,
                external_id=listing.external_id,
                html=description,
                text=description,
                structured={"job": job},
            )

        return RawJobDetail(
            source_slug=self.slug,
            fetched_at=now,
            url=listing.url,
            external_id=listing.external_id,
            html=None,
            text=None,
            structured={},
        )

    def normalize(self, detail: RawJobDetail, listing: RawListing | None = None) -> NormalizedJob:
        job: dict[str, Any] = detail.structured.get("job", {}) if detail.structured else {}
        title = job.get("title") or (listing.title_hint if listing else "")
        company = job.get("company_name") or (listing.company_hint if listing else "")
        location = job.get("candidate_required_location") or (listing.location_hint if listing else None)
        description = detail.text or ""

        return NormalizedJob(
            source_slug=self.slug,
            canonical_url=detail.url,
            source_url=detail.url,
            external_id=detail.external_id,
            title=title or "Unknown Title",
            company_name=company or "Unknown Company",
            location=location,
            remote_flag=True,
            employment_type=None,
            seniority=None,
            description_text=description,
            date_posted=_parse_datetime(job.get("publication_date")),
            tags=job.get("tags", []) or [],
            tech_stack=[],
            discovered_at=listing.discovered_at if listing else None,
            fetched_at=detail.fetched_at,
            raw_fingerprint=None,
        )

    def _fetch(self, base_url: str, params: dict[str, Any]) -> dict[str, Any]:
        resp = self.client.get(base_url, params=params)
        resp.raise_for_status()
        return resp.json()

    def _to_listings(self, payload: dict[str, Any], now: datetime) -> list[RawListing]:
        jobs = payload.get("jobs", [])
        listings: list[RawListing] = []
        for job in jobs:
            listings.append(
                RawListing(
                    source_slug=self.slug,
                    discovered_at=now,
                    url=job.get("url") or "",
                    external_id=str(job.get("id")) if job.get("id") is not None else None,
                    title_hint=job.get("title"),
                    company_hint=job.get("company_name"),
                    location_hint=job.get("candidate_required_location"),
                    posted_at_hint=_parse_datetime(job.get("publication_date")),
                    raw_payload={"job": job},
                )
            )
        return listings


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
