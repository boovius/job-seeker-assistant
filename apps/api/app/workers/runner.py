from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
import httpx

from app.db.session import SessionLocal
from app.services.pipeline_events import log_event
from app.services.adapters import FetchCursor, RawListing, get_adapter
from app.services.adapters.query_utils import build_queries
from app.services.sources import to_registry_entry
from db.models import IdealJobSubmission, Job, Source, SourceCursor, UserSource, WorkflowQueue


def claim_next_task(db: Session, lease_minutes: int = 5) -> WorkflowQueue | None:
    now = datetime.now(timezone.utc)
    stmt = (
        select(WorkflowQueue)
        .where(
            (WorkflowQueue.status == "queued")
            | (
                (WorkflowQueue.status == "leased")
                & (WorkflowQueue.lease_expires_at.isnot(None))
                & (WorkflowQueue.lease_expires_at < now)
            )
        )
        .order_by(WorkflowQueue.created_at.asc())
        .limit(1)
        .with_for_update(skip_locked=True)
    )
    task = db.execute(stmt).scalars().first()
    if not task:
        return None

    task.status = "leased"
    task.lease_expires_at = now + timedelta(minutes=lease_minutes)
    task.attempts = (task.attempts or 0) + 1
    task.started_at = now
    db.add(task)
    db.commit()
    db.refresh(task)
    log_event(
        db,
        event_type="task_claimed",
        message=f"Claimed task {task.task_type}",
        payload={"task_type": task.task_type},
        user_id=(task.payload or {}).get("user_id"),
        task_id=str(task.id),
    )
    return task


def _get_source_context(db: Session, source_id: str, user_id: str):
    source = db.query(Source).filter(Source.id == source_id).first()
    user_source = (
        db.query(UserSource)
        .filter(UserSource.source_id == source_id)
        .filter(UserSource.user_id == user_id)
        .first()
    )
    return source, user_source


def _get_source_by_slug(db: Session, user_id: str, slug: str):
    return (
        db.query(Source, UserSource)
        .join(UserSource, UserSource.source_id == Source.id)
        .filter(UserSource.user_id == user_id)
        .filter(Source.slug == slug)
        .first()
    )


def _get_cursor(db: Session, source_id: str, user_id: str) -> SourceCursor:
    cursor = (
        db.query(SourceCursor)
        .filter(SourceCursor.source_id == source_id)
        .filter(SourceCursor.user_id == user_id)
        .first()
    )
    if cursor:
        return cursor
    cursor = SourceCursor(source_id=source_id, user_id=user_id, cursor={})
    db.add(cursor)
    db.flush()
    return cursor


def _redact_config(config: dict) -> dict:
    redacted = {}
    for key, value in (config or {}).items():
        if key in {"api_key", "app_key", "app_id", "gmail_access_token", "gmail_refresh_token", "client_secret"}:
            redacted[key] = "<redacted>" if value else None
            continue
        redacted[key] = value
    return redacted


def _build_query_sets(config: dict) -> list[dict]:
    profiles = build_queries(config or {})
    if profiles:
        return profiles
    keywords = config.get("keywords", []) if config else []
    location = config.get("location") if config else None
    if not keywords and not location:
        return []
    return [{"keywords": " ".join([kw for kw in keywords if kw]), "location": location, "remote": None}]


def _build_request_specs(adapter: str, config: dict, query_sets: list[dict]) -> list[dict]:
    if adapter == "adzuna_api_v1":
        country = (config or {}).get("country", "us")
        results_per_page = (config or {}).get("results_per_page", 50)
        url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
        specs = []
        for qs in query_sets or [{}]:
            params = {"results_per_page": results_per_page, "content-type": "application/json"}
            if qs.get("keywords"):
                params["what"] = qs["keywords"]
            if qs.get("location"):
                params["where"] = qs["location"]
            specs.append({"method": "GET", "url": url, "params": params})
        return specs
    if adapter == "jooble_api_v1":
        page = (config or {}).get("page", 1)
        url = "https://jooble.org/api/<redacted>"
        specs = []
        for qs in query_sets or [{}]:
            payload = {"keywords": qs.get("keywords", ""), "page": page}
            if qs.get("location"):
                payload["location"] = qs["location"]
            specs.append({"method": "POST", "url": url, "json": payload})
        return specs
    if adapter == "gmail_climatebase_v1":
        return [
            {
                "method": "GET",
                "url": "https://gmail.googleapis.com/gmail/v1/users/me/messages",
                "params": {
                    "q": (config or {}).get("gmail_query", "from:(climatebase.org) newer_than:30d"),
                    "maxResults": (config or {}).get("max_messages", 20),
                },
            }
        ]
    return []


def _build_listings_preview(listings: list[RawListing], limit: int = 5) -> list[dict]:
    preview = []
    for listing in listings[:limit]:
        preview.append(
            {
                "title": listing.title_hint,
                "company": listing.company_hint,
                "location": listing.location_hint,
                "url": listing.url,
                "target_source_slug": (listing.raw_payload or {}).get("target_source_slug"),
            }
        )
    return preview


def _enqueue_fetch_detail(db: Session, listing: RawListing, source_id: str, user_id: str, detail_source_id: str | None = None) -> None:
    payload = {
        "source_id": detail_source_id or source_id,
        "discovered_from_source_id": source_id,
        "user_id": user_id,
        "listing": {
            "url": listing.url,
            "external_id": listing.external_id,
            "title_hint": listing.title_hint,
            "company_hint": listing.company_hint,
            "location_hint": listing.location_hint,
            "posted_at_hint": listing.posted_at_hint.isoformat() if listing.posted_at_hint else None,
            "raw_payload": listing.raw_payload,
        },
    }
    task = WorkflowQueue(task_type="fetch_detail", payload=payload, status="queued")
    db.add(task)


def _resolve_detail_source_id(db: Session, user_id: str, source_id: str, listing: RawListing) -> str:
    raw_payload = listing.raw_payload or {}
    target_source_slug = raw_payload.get("target_source_slug")
    if not target_source_slug:
        return source_id

    row = _get_source_by_slug(db, user_id, target_source_slug)
    if not row:
        raise ValueError(f"Missing enabled source for target_source_slug={target_source_slug}")
    source, _ = row
    return str(source.id)


def _upsert_job(db: Session, job: dict) -> None:
    stmt = insert(Job).values(**job)
    stmt = stmt.on_conflict_do_update(
        index_elements=[Job.canonical_url],
        set_={
            "title": stmt.excluded.title,
            "company_name": stmt.excluded.company_name,
            "location": stmt.excluded.location,
            "remote_flag": stmt.excluded.remote_flag,
            "description": stmt.excluded.description,
            "source_type": stmt.excluded.source_type,
            "date_posted": stmt.excluded.date_posted,
            "status": stmt.excluded.status,
        },
    )
    db.execute(stmt)


def _handle_fetch_listings(db: Session, task: WorkflowQueue) -> int:
    payload = task.payload or {}
    source_id = payload.get("source_id")
    user_id = payload.get("user_id")
    if not source_id or not user_id:
        raise ValueError("Missing source_id or user_id")

    source, user_source = _get_source_context(db, source_id, user_id)
    if not source:
        raise ValueError("Unknown source")

    registry = to_registry_entry(source, user_source)
    query_sets = _build_query_sets(registry.config or {})
    request_specs = _build_request_specs(source.adapter, registry.config or {}, query_sets)
    log_event(
        db,
        event_type="fetch_listings_start",
        message="Fetching listings",
        payload={
            "source_id": str(source.id),
            "adapter": source.adapter,
            "base_url": source.base_url,
            "config": _redact_config(registry.config or {}),
            "query_sets": query_sets,
            "requests": request_specs,
        },
        user_id=user_id,
        task_id=str(task.id),
    )
    adapter = get_adapter(source.adapter)
    cursor = _get_cursor(db, source_id, user_id)

    listings, updated = adapter.fetch_listings(registry, FetchCursor(cursor.cursor or {}))
    for listing in listings:
        detail_source_id = _resolve_detail_source_id(db, user_id, source_id, listing)
        _enqueue_fetch_detail(db, listing, source_id, user_id, detail_source_id=detail_source_id)

    cursor.cursor = updated.state
    db.add(cursor)
    log_event(
        db,
        event_type="fetch_listings_done",
        message=f"Fetched {len(listings)} listings",
        payload={
            "source_id": str(source.id),
            "count": len(listings),
            "listings_preview": _build_listings_preview(listings),
        },
        user_id=user_id,
        task_id=str(task.id),
    )
    return len(listings)


def _handle_fetch_detail(db: Session, task: WorkflowQueue) -> None:
    payload = task.payload or {}
    source_id = payload.get("source_id")
    user_id = payload.get("user_id")
    listing_payload = payload.get("listing") or {}
    if not source_id or not user_id or not listing_payload:
        raise ValueError("Missing source_id, user_id, or listing payload")

    source, user_source = _get_source_context(db, source_id, user_id)
    if not source:
        raise ValueError("Unknown source")

    registry = to_registry_entry(source, user_source)
    adapter = get_adapter(source.adapter)

    listing = RawListing(
        source_slug=registry.slug,
        discovered_at=None,
        url=listing_payload.get("url", ""),
        external_id=listing_payload.get("external_id"),
        title_hint=listing_payload.get("title_hint"),
        company_hint=listing_payload.get("company_hint"),
        location_hint=listing_payload.get("location_hint"),
        posted_at_hint=None,
        raw_payload=listing_payload.get("raw_payload"),
    )
    detail = adapter.fetch_job_detail(listing, registry)
    normalized = adapter.normalize(detail, listing)

    _upsert_job(
        db,
        {
            "canonical_url": normalized.canonical_url,
            "title": normalized.title,
            "company_name": normalized.company_name,
            "location": normalized.location,
            "remote_flag": normalized.remote_flag,
            "description": normalized.description_text,
            "source_type": "auto",
            "date_posted": normalized.date_posted,
            "status": "new",
        },
    )
    log_event(
        db,
        event_type="fetch_detail_done",
        message="Upserted job",
        payload={
            "source_id": str(source.id),
            "canonical_url": normalized.canonical_url,
            "discovered_from_source_id": payload.get("discovered_from_source_id"),
            "gmail_provenance": (listing.raw_payload or {}).get("gmail_provenance"),
        },
        user_id=user_id,
        task_id=str(task.id),
    )


def _handle_ideal_ingest(db: Session, task: WorkflowQueue) -> None:
    payload = task.payload or {}
    submission_id = payload.get("submission_id")
    url = payload.get("url")
    if not submission_id or not url:
        raise ValueError("Missing submission_id or url")

    submission = db.query(IdealJobSubmission).filter(IdealJobSubmission.id == submission_id).first()
    if not submission:
        raise ValueError("Unknown ideal job submission")

    resp = httpx.get(url, timeout=20)
    resp.raise_for_status()
    submission.page_text = resp.text[:200000]
    submission.fetched_at = datetime.now(timezone.utc)
    submission.status = "processed"
    db.add(submission)


def run_once() -> None:
    db = SessionLocal()
    try:
        task = claim_next_task(db)
        if not task:
            return

        try:
            if task.task_type == "fetch_listings":
                listings_count = _handle_fetch_listings(db, task)
                task.last_error = f"Fetched {listings_count} listings; enqueued {listings_count} details"
            elif task.task_type == "fetch_detail":
                _handle_fetch_detail(db, task)
            elif task.task_type == "ideal_ingest":
                _handle_ideal_ingest(db, task)
            else:
                raise ValueError(f"Unknown task_type: {task.task_type}")

            task.status = "succeeded"
            task.finished_at = datetime.now(timezone.utc)
            db.commit()
            log_event(
                db,
                event_type="task_succeeded",
                message=f"Task {task.task_type} succeeded",
                payload={"task_type": task.task_type},
                user_id=(task.payload or {}).get("user_id"),
                task_id=str(task.id),
            )
        except Exception as exc:  # pragma: no cover - runner logs later
            task.status = "failed"
            task.last_error = str(exc)
            task.finished_at = datetime.now(timezone.utc)
            db.commit()
            log_event(
                db,
                event_type="task_failed",
                message=f"Task {task.task_type} failed",
                payload={"task_type": task.task_type, "error": str(exc)},
                user_id=(task.payload or {}).get("user_id"),
                task_id=str(task.id),
            )
    finally:
        db.close()


if __name__ == "__main__":
    run_once()
