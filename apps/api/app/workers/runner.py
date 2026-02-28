from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.adapters import FetchCursor, RawListing, get_adapter
from app.services.sources import to_registry_entry
from db.models import Job, Source, SourceCursor, UserSource, WorkflowQueue


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


def _enqueue_fetch_detail(db: Session, listing: RawListing, source_id: str, user_id: str) -> None:
    payload = {
        "source_id": source_id,
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


def _handle_fetch_listings(db: Session, task: WorkflowQueue) -> None:
    payload = task.payload or {}
    source_id = payload.get("source_id")
    user_id = payload.get("user_id")
    if not source_id or not user_id:
        raise ValueError("Missing source_id or user_id")

    source, user_source = _get_source_context(db, source_id, user_id)
    if not source:
        raise ValueError("Unknown source")

    registry = to_registry_entry(source, user_source)
    adapter = get_adapter(source.adapter)
    cursor = _get_cursor(db, source_id, user_id)

    listings, updated = adapter.fetch_listings(registry, FetchCursor(cursor.cursor or {}))
    for listing in listings:
        _enqueue_fetch_detail(db, listing, source_id, user_id)

    cursor.cursor = updated.state
    db.add(cursor)


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


def run_once() -> None:
    db = SessionLocal()
    try:
        task = claim_next_task(db)
        if not task:
            return

        try:
            if task.task_type == "fetch_listings":
                _handle_fetch_listings(db, task)
            elif task.task_type == "fetch_detail":
                _handle_fetch_detail(db, task)
            else:
                raise ValueError(f"Unknown task_type: {task.task_type}")

            task.status = "succeeded"
            task.finished_at = datetime.now(timezone.utc)
            db.commit()
        except Exception as exc:  # pragma: no cover - runner logs later
            task.status = "failed"
            task.last_error = str(exc)
            task.finished_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run_once()
