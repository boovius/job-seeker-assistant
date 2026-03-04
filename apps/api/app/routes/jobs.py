from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import RequireUser
from app.db.deps import get_db
from db.models import IdealJobSubmission, ManualSubmission, WorkflowQueue

router = APIRouter(prefix="/jobs", tags=["jobs"])


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


@router.post("/ideal")
def submit_ideal_job(payload: dict, db: Session = Depends(get_db), user=RequireUser):
    user_id = user.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user id")

    url = payload.get("url")
    why_text = payload.get("why_text")
    if not url or not isinstance(url, str):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing url")
    if not why_text or not isinstance(why_text, str):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing why_text")

    submission = IdealJobSubmission(user_id=user_id, url=url, why_text=why_text)
    db.add(submission)
    db.flush()

    task = WorkflowQueue(
        job_id=None,
        task_type="ideal_ingest",
        payload={"url": url, "why_text": why_text, "submission_id": str(submission.id), "user_id": user_id},
        status="queued",
    )
    db.add(task)
    db.commit()

    return {"status": "queued", "submission_id": str(submission.id), "task_id": str(task.id)}
