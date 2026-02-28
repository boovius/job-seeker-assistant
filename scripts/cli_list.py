from __future__ import annotations

import os
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from db.models import Job, Source, WorkflowQueue


def _db() -> Session:
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        raise RuntimeError("Missing DATABASE_URL")
    engine = create_engine(database_url, pool_pre_ping=True)
    return Session(engine)


def list_sources() -> None:
    with _db() as db:
        items = db.execute(select(Source).order_by(Source.slug.asc())).scalars().all()
        for item in items:
            print(item.slug, item.adapter, item.kind, item.default_config)


def list_jobs() -> None:
    with _db() as db:
        items = (
            db.execute(select(Job).order_by(Job.date_posted.desc().nullslast(), Job.id.desc()).limit(100))
            .scalars()
            .all()
        )
        for item in items:
            print(item.id, item.company_name, item.title, item.status)


def list_queue(failed_only: bool = False) -> None:
    with _db() as db:
        stmt = select(WorkflowQueue).order_by(WorkflowQueue.created_at.desc()).limit(100)
        if failed_only:
            stmt = stmt.filter(WorkflowQueue.status == "failed")
        items = db.execute(stmt).scalars().all()
        for item in items:
            print(item.id, item.task_type, item.status, item.attempts, item.last_error)
