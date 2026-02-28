from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from app.services.adapters.base import FetchCursor, NormalizedJob, RawJobDetail, RawListing, SourceAdapter, SourceRegistryEntry
from app.services.adapters.query_utils import build_queries


class AdzunaAdapter(SourceAdapter):
    slug = "adzuna"

    def __init__(self, client: httpx.Client | None = None) -> None:
        self.client = client or httpx.Client(timeout=30)

    def fetch_listings(
        self,
        registry: SourceRegistryEntry,
        cursor: FetchCursor,
    ) -> tuple[list[RawListing], FetchCursor]:
        app_id = registry.config.get("app_id")
        app_key = registry.config.get("app_key")
        country = registry.config.get("country", "us")
        keywords = registry.config.get("keywords", [])
        results_per_page = registry.config.get("results_per_page", 50)
        profiles = build_queries(registry.config)

        if not app_id or not app_key:
            raise ValueError("Missing Adzuna app_id/app_key")

        listings: list[RawListing] = []
        now = datetime.now(timezone.utc)

        query_sets = profiles or [{"keywords": " ".join(keywords)}]

        for qs in query_sets:
            params = {
                "app_id": app_id,
                "app_key": app_key,
                "results_per_page": results_per_page,
                "content-type": "application/json",
            }
            kw = qs.get("keywords")
            if kw:
                params["what"] = kw
            where = qs.get("location")
            if where:
                params["where"] = where

            url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
            resp = self.client.get(url, params=params)
            resp.raise_for_status()
            payload = resp.json()

            for job in payload.get("results", []):
                listings.append(
                    RawListing(
                        source_slug=self.slug,
                        discovered_at=now,
                        url=job.get("redirect_url") or job.get("url") or "",
                        external_id=str(job.get("id")) if job.get("id") is not None else None,
                        title_hint=job.get("title"),
                        company_hint=(job.get("company") or {}).get("display_name"),
                        location_hint=(job.get("location") or {}).get("display_name"),
                        posted_at_hint=_parse_datetime(job.get("created")),
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
        company = (job.get("company") or {}).get("display_name") or (listing.company_hint if listing else "")
        location = (job.get("location") or {}).get("display_name") or (listing.location_hint if listing else None)
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
            date_posted=_parse_datetime(job.get("created")) or (listing.posted_at_hint if listing else None),
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
