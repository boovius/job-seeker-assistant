from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import RequireUser
from app.db.deps import get_db
from db.models import WorkflowQueue

router = APIRouter(prefix="/queue", tags=["queue"])


@router.get("")
def list_queue(db: Session = Depends(get_db), user=RequireUser):
    items = (
        db.query(WorkflowQueue)
        .order_by(WorkflowQueue.created_at.desc())
        .limit(100)
        .all()
    )
    return {
        "items": [
            {
                "id": str(item.id),
                "task_type": item.task_type,
                "status": item.status,
                "attempts": item.attempts,
                "last_error": item.last_error,
                "created_at": item.created_at,
                "started_at": item.started_at,
                "finished_at": item.finished_at,
            }
            for item in items
        ],
        "count": len(items),
    }


@router.get("/failed")
def list_failed(db: Session = Depends(get_db), user=RequireUser):
    items = (
        db.query(WorkflowQueue)
        .filter(WorkflowQueue.status == "failed")
        .order_by(WorkflowQueue.created_at.desc())
        .limit(100)
        .all()
    )
    return {
        "items": [
            {
                "id": str(item.id),
                "task_type": item.task_type,
                "status": item.status,
                "attempts": item.attempts,
                "last_error": item.last_error,
                "created_at": item.created_at,
                "started_at": item.started_at,
                "finished_at": item.finished_at,
            }
            for item in items
        ],
        "count": len(items),
    }
