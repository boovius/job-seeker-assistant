from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from db.models import WorkflowQueue


def fetch_next_task(db: Session) -> WorkflowQueue | None:
    stmt = (
        select(WorkflowQueue)
        .where(WorkflowQueue.status == "queued")
        .order_by(WorkflowQueue.created_at.asc())
        .limit(1)
    )
    return db.execute(stmt).scalars().first()


def run_once() -> None:
    db = SessionLocal()
    try:
        task = fetch_next_task(db)
        if not task:
            return

        # TODO: implement task dispatch by task_type
        task.status = "running"
        db.add(task)
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run_once()
