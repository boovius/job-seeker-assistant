from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import RequireUser
from app.db.deps import get_db
from db.models import ManualSubmission, WorkflowQueue

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("")
def list_jobs(db: Session = Depends(get_db), user=RequireUser):
    # TODO: query jobs table
    return {"items": [], "count": 0}


@router.post("/manual")
def submit_manual_url(payload: dict, db: Session = Depends(get_db), user=RequireUser):
    url = payload.get("url")
    notes = payload.get("notes")
    if not url or not isinstance(url, str):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing url")

    submission = ManualSubmission(url=url, notes=notes)
    db.add(submission)
    db.flush()

    task = WorkflowQueue(
        job_id=None,
        task_type="manual_ingest",
        payload={"url": url, "notes": notes, "submission_id": str(submission.id)},
        status="queued",
    )
    db.add(task)
    db.commit()

    return {"status": "queued", "submission_id": str(submission.id), "task_id": str(task.id)}
