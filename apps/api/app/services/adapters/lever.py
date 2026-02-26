from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from app.services.adapters.base import FetchCursor, NormalizedJob, RawJobDetail, RawListing, SourceAdapter, SourceRegistryEntry


class LeverAdapter(SourceAdapter):
    slug = "lever"

    def __init__(self, client: httpx.Client | None = None) -> None:
        self.client = client or httpx.Client(timeout=30)

    def fetch_listings(
        self,
        registry: SourceRegistryEntry,
        cursor: FetchCursor,
    ) -> tuple[list[RawListing], FetchCursor]:
        companies = registry.config.get("companies", [])
        listings: list[RawListing] = []
        now = datetime.now(timezone.utc)

        for company in companies:
            url = f"https://api.lever.co/v0/postings/{company}?mode=json"
            resp = self.client.get(url)
            resp.raise_for_status()
            payload = resp.json()
            for job in payload:
                listings.append(
                    RawListing(
                        source_slug=self.slug,
                        discovered_at=now,
                        url=job.get("hostedUrl") or "",
                        external_id=str(job.get("id")) if job.get("id") is not None else None,
                        title_hint=job.get("text"),
                        company_hint=company,
                        location_hint=_location_from_categories(job.get("categories", {})),
                        posted_at_hint=_parse_datetime(job.get("createdAt")),
                        raw_payload={"job": job, "company": company},
                    )
                )

        return listings, cursor

    def fetch_job_detail(self, listing: RawListing, registry: SourceRegistryEntry) -> RawJobDetail:
        now = datetime.now(timezone.utc)
        if listing.raw_payload and "job" in listing.raw_payload:
            job = listing.raw_payload["job"]
            text = job.get("descriptionPlain") or job.get("description") or ""
            return RawJobDetail(
                source_slug=self.slug,
                fetched_at=now,
                url=listing.url,
                external_id=listing.external_id,
                html=job.get("description"),
                text=text,
                structured={"job": job, "company": listing.raw_payload.get("company")},
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
        title = job.get("text") or (listing.title_hint if listing else "")
        company = detail.structured.get("company") or (listing.company_hint if listing else "")
        location = _location_from_categories(job.get("categories", {})) or (listing.location_hint if listing else None)

        description = detail.text or ""
        workplace = job.get("workplaceType")

        return NormalizedJob(
            source_slug=self.slug,
            canonical_url=detail.url,
            source_url=detail.url,
            external_id=detail.external_id,
            title=title or "Unknown Title",
            company_name=company or "Unknown Company",
            location=location,
            remote_flag=_is_remote(workplace, location),
            employment_type=None,
            seniority=None,
            description_text=description,
            date_posted=_parse_datetime(job.get("createdAt")) or (listing.posted_at_hint if listing else None),
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
        return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc)
    except (ValueError, TypeError):
        return None


def _location_from_categories(categories: dict[str, Any]) -> str | None:
    if not categories:
        return None
    return categories.get("location")


def _is_remote(workplace: str | None, location: str | None) -> bool:
    if workplace and workplace.lower() in {"remote", "hybrid"}:
        return True
    if location and "remote" in location.lower():
        return True
    return False
