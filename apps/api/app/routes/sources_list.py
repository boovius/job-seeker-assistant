from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import RequireUser
from app.db.deps import get_db
from db.models import Source

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("")
def list_sources(db: Session = Depends(get_db), user=RequireUser):
    items = db.query(Source).order_by(Source.slug.asc()).all()
    return {
        "items": [
            {
                "id": str(item.id),
                "slug": item.slug,
                "adapter": item.adapter,
                "kind": item.kind,
                "base_url": item.base_url,
                "default_config": item.default_config,
            }
            for item in items
        ],
        "count": len(items),
    }
