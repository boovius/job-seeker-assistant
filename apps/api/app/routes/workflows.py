from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.auth import RequireUser
from app.db.deps import get_db
from app.services.pipeline_events import log_event
from app.services.query_generation import apply_profiles_to_sources, generate_profiles
from app.workers.runner import run_once
from db.models import Source, UserSource, WorkflowQueue


def _run_worker_cycles(max_cycles: int) -> None:
    for _ in range(max_cycles):
        run_once()

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("/run-once")
def run_workflow_once():
    run_once()
    return {"status": "ok"}


@router.post("/enqueue-fetch-listings")
def enqueue_fetch_listings(payload: dict, db: Session = Depends(get_db), user=RequireUser):
    user_id = user.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user id")

    source_slug = payload.get("source_slug")
    if not source_slug:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing source_slug")

    source = db.query(Source).filter(Source.slug == source_slug).first()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown source")

    user_source = (
        db.query(UserSource)
        .filter(UserSource.source_id == source.id)
        .filter(UserSource.user_id == user_id)
        .first()
    )
    if not user_source:
        user_source = UserSource(user_id=user_id, source_id=source.id, enabled=True, weight=1)
        db.add(user_source)
        db.flush()

    task = WorkflowQueue(task_type="fetch_listings", payload={"source_id": str(source.id), "user_id": user_id})
    db.add(task)
    db.commit()
    return {"status": "queued", "task_id": str(task.id)}


@router.post("/run-pipeline")
def run_pipeline(
    payload: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user=RequireUser,
):
    user_id = user.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user id")

    max_cycles = payload.get("max_cycles", 3)
    run_worker = payload.get("run_worker", True)

    rows = (
        db.query(Source, UserSource)
        .join(UserSource, UserSource.source_id == Source.id)
        .filter(UserSource.user_id == user_id)
        .filter(UserSource.enabled.is_(True))
        .all()
    )

    if not rows:
        return {"status": "no_sources", "tasks": 0, "message": "No enabled sources for user"}

    profiles = generate_profiles(db, user_id)
    log_event(
        db,
        event_type="llm_profiles",
        message="Generated search profiles",
        payload={"profiles": [profile.model_dump() for profile in profiles.search_profiles]},
        user_id=user_id,
    )
    updated_sources = apply_profiles_to_sources(db, user_id, profiles)
    log_event(
        db,
        event_type="profiles_applied",
        message=f"Applied profiles to {updated_sources} sources",
        payload={"updated_sources": updated_sources},
        user_id=user_id,
    )

    for source, _ in rows:
        task = WorkflowQueue(task_type="fetch_listings", payload={"source_id": str(source.id), "user_id": user_id})
        db.add(task)

    db.commit()
    log_event(
        db,
        event_type="pipeline_enqueued",
        message=f"Enqueued {len(rows)} sources",
        payload={"source_ids": [str(source.id) for source, _ in rows]},
        user_id=user_id,
    )

    if run_worker:
        background_tasks.add_task(_run_worker_cycles, int(max_cycles))

    return {
        "status": "queued",
        "tasks": len(rows),
        "run_worker": bool(run_worker),
        "max_cycles": int(max_cycles),
        "source_ids": [str(source.id) for source, _ in rows],
        "message": f"Enqueued {len(rows)} sources (updated {updated_sources} search profiles)",
    }


@router.delete("/queue")
def clear_workflow_queue(db: Session = Depends(get_db), user=RequireUser):
    user_id = user.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user id")
    stmt = delete(WorkflowQueue).where(WorkflowQueue.payload["user_id"].astext == user_id)
    result = db.execute(stmt)
    db.commit()
    return {"status": "ok", "deleted": result.rowcount or 0}
