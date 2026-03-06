from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class SourceRegistryEntry:
    slug: str
    adapter: str
    kind: str
    base_url: Optional[str] = None
    enabled: bool = True
    weight: float = 1.0
    fetch_mode: str = "http"
    rate_limit_rps: float = 0.2
    concurrency: int = 2
    config: dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None


@dataclass
class FetchCursor:
    state: dict[str, Any] = field(default_factory=dict)


@dataclass
class RawListing:
    source_slug: str
    discovered_at: datetime
    url: str
    external_id: Optional[str] = None
    title_hint: Optional[str] = None
    company_hint: Optional[str] = None
    location_hint: Optional[str] = None
    posted_at_hint: Optional[datetime] = None
    raw_snippet: Optional[str] = None
    raw_payload: Optional[dict[str, Any]] = None


@dataclass
class RawJobDetail:
    source_slug: str
    fetched_at: datetime
    url: str
    external_id: Optional[str] = None
    html: Optional[str] = None
    text: Optional[str] = None
    structured: dict[str, Any] = field(default_factory=dict)


@dataclass
class NormalizedJob:
    source_slug: str
    canonical_url: str
    source_url: str
    external_id: Optional[str]
    title: str
    company_name: str
    location: Optional[str]
    remote_flag: bool
    employment_type: Optional[str]
    seniority: Optional[str]
    description_text: str
    date_posted: Optional[datetime]
    tags: list[str] = field(default_factory=list)
    tech_stack: list[str] = field(default_factory=list)
    discovered_at: Optional[datetime] = None
    fetched_at: Optional[datetime] = None
    raw_fingerprint: Optional[str] = None


class SourceAdapter(ABC):
    slug: str

    @abstractmethod
    def fetch_listings(
        self,
        registry: SourceRegistryEntry,
        cursor: FetchCursor,
    ) -> tuple[list[RawListing], FetchCursor]:
        raise NotImplementedError

    @abstractmethod
    def fetch_job_detail(
        self,
        listing: RawListing,
        registry: SourceRegistryEntry,
    ) -> RawJobDetail:
        raise NotImplementedError

    @abstractmethod
    def normalize(
        self,
        detail: RawJobDetail,
        listing: Optional[RawListing] = None,
    ) -> NormalizedJob:
        raise NotImplementedError
