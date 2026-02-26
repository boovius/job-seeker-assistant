from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import RequireUser
from app.db.deps import get_db
from db.models import ManualSubmission

router = APIRouter(prefix="/manual-submissions", tags=["manual-submissions"])


@router.get("")
def list_manual_submissions(db: Session = Depends(get_db), user=RequireUser):
    items = db.query(ManualSubmission).order_by(ManualSubmission.submitted_at.desc()).limit(50).all()
    return {
        "items": [
            {
                "id": str(item.id),
                "url": item.url,
                "notes": item.notes,
                "status": item.status,
                "submitted_at": item.submitted_at,
            }
            for item in items
        ],
        "count": len(items),
    }
