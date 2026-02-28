from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from app.services.adapters.base import FetchCursor, NormalizedJob, RawJobDetail, RawListing, SourceAdapter, SourceRegistryEntry


class JoobleAdapter(SourceAdapter):
    slug = "jooble"

    def __init__(self, client: httpx.Client | None = None) -> None:
        self.client = client or httpx.Client(timeout=30)

    def fetch_listings(
        self,
        registry: SourceRegistryEntry,
        cursor: FetchCursor,
    ) -> tuple[list[RawListing], FetchCursor]:
        api_key = registry.config.get("api_key")
        keywords = registry.config.get("keywords", [])
        location = registry.config.get("location")
        page = registry.config.get("page", 1)

        if not api_key:
            raise ValueError("Missing Jooble api_key")

        listings: list[RawListing] = []
        now = datetime.now(timezone.utc)

        for kw in keywords or [""]:
            payload = {"keywords": kw, "page": page}
            if location:
                payload["location"] = location

            url = f"https://jooble.org/api/{api_key}"
            resp = self.client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

            for job in data.get("jobs", []):
                listings.append(
                    RawListing(
                        source_slug=self.slug,
                        discovered_at=now,
                        url=job.get("link") or "",
                        external_id=str(job.get("id")) if job.get("id") is not None else None,
                        title_hint=job.get("title"),
                        company_hint=job.get("company"),
                        location_hint=job.get("location"),
                        posted_at_hint=_parse_datetime(job.get("updated")),
                        raw_payload={"job": job},
                    )
                )

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
            description = job.get("snippet") or ""
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
        company = job.get("company") or (listing.company_hint if listing else "")
        location = job.get("location") or (listing.location_hint if listing else None)
        description = detail.text or ""

        return NormalizedJob(
            source_slug=self.slug,
            canonical_url=detail.url,
            source_url=detail.url,
            external_id=detail.external_id,
            title=title or "Unknown Title",
            company_name=company or "Unknown Company",
            location=location,
            remote_flag=_is_remote(location, title),
            employment_type=None,
            seniority=None,
            description_text=description,
            date_posted=_parse_datetime(job.get("updated")) or (listing.posted_at_hint if listing else None),
            tags=[],
            tech_stack=[],
            discovered_at=listing.discovered_at if listing else None,
            fetched_at=detail.fetched_at,
            raw_fingerprint=None,
        )


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _is_remote(location: str | None, title: str | None) -> bool:
    for item in (location or "", title or ""):
        if "remote" in item.lower():
            return True
    return False
