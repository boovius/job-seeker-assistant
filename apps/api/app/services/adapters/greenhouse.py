from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from app.services.adapters.base import FetchCursor, NormalizedJob, RawJobDetail, RawListing, SourceAdapter, SourceRegistryEntry


class GreenhouseAdapter(SourceAdapter):
    slug = "greenhouse"

    def __init__(self, client: httpx.Client | None = None) -> None:
        self.client = client or httpx.Client(timeout=30)

    def fetch_listings(
        self,
        registry: SourceRegistryEntry,
        cursor: FetchCursor,
    ) -> tuple[list[RawListing], FetchCursor]:
        board_tokens = registry.config.get("board_tokens", [])
        listings: list[RawListing] = []
        now = datetime.now(timezone.utc)

        for token in board_tokens:
            url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
            resp = self.client.get(url)
            resp.raise_for_status()
            payload = resp.json()
            jobs = payload.get("jobs", [])
            for job in jobs:
                listings.append(
                    RawListing(
                        source_slug=self.slug,
                        discovered_at=now,
                        url=job.get("absolute_url") or "",
                        external_id=str(job.get("id")) if job.get("id") is not None else None,
                        title_hint=job.get("title"),
                        company_hint=token,
                        location_hint=(job.get("location") or {}).get("name"),
                        posted_at_hint=_parse_datetime(job.get("updated_at")),
                        raw_payload={"job": job, "board_token": token},
                    )
                )

        return listings, cursor

    def fetch_job_detail(self, listing: RawListing, registry: SourceRegistryEntry) -> RawJobDetail:
        now = datetime.now(timezone.utc)
        if listing.raw_payload and "job" in listing.raw_payload:
            job = listing.raw_payload["job"]
            content = job.get("content") or ""
            return RawJobDetail(
                source_slug=self.slug,
                fetched_at=now,
                url=listing.url,
                external_id=listing.external_id,
                html=content,
                text=content,
                structured={"job": job, "board_token": listing.raw_payload.get("board_token")},
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
        company = detail.structured.get("board_token") or (listing.company_hint if listing else "")
        location = (job.get("location") or {}).get("name") or (listing.location_hint if listing else None)

        description = detail.text or ""
        return NormalizedJob(
            source_slug=self.slug,
            canonical_url=detail.url,
            source_url=detail.url,
            external_id=detail.external_id,
            title=title or "Unknown Title",
            company_name=company or "Unknown Company",
            location=location,
            remote_flag=_is_remote(location),
            employment_type=None,
            seniority=None,
            description_text=description,
            date_posted=_parse_datetime(job.get("updated_at")) or (listing.posted_at_hint if listing else None),
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


def _is_remote(location: str | None) -> bool:
    if not location:
        return False
    return "remote" in location.lower()
