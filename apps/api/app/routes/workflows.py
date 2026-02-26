from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import RequireUser
from app.db.deps import get_db
from app.workers.runner import run_once
from db.models import Source, UserSource, WorkflowQueue

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
