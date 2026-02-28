from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import RequireUser
from app.db.deps import get_db
from db.models import Job

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("")
def list_jobs(db: Session = Depends(get_db), user=RequireUser):
    items = db.query(Job).order_by(Job.date_posted.desc().nullslast(), Job.id.desc()).limit(100).all()
    return {
        "items": [
            {
                "id": str(item.id),
                "canonical_url": item.canonical_url,
                "title": item.title,
                "company_name": item.company_name,
                "location": item.location,
                "status": item.status,
                "date_posted": item.date_posted,
            }
            for item in items
        ],
        "count": len(items),
    }
