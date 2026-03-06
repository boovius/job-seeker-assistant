from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import RequireUser
from app.db.deps import get_db
from db.models import PipelineEvent

router = APIRouter(prefix="/pipeline-events", tags=["pipeline-events"])


@router.get("")
def list_pipeline_events(limit: int = 50, db: Session = Depends(get_db), user=RequireUser):
    user_id = user.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user id")
    items = (
        db.query(PipelineEvent)
        .filter(PipelineEvent.user_id == user_id)
        .order_by(PipelineEvent.created_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "items": [
            {
                "id": str(item.id),
                "event_type": item.event_type,
                "message": item.message,
                "payload": item.payload,
                "created_at": item.created_at,
                "task_id": str(item.task_id) if item.task_id else None,
            }
            for item in items
        ],
        "count": len(items),
    }
