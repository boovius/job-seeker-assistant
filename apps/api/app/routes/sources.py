from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.auth import RequireUser
from app.db.deps import get_db
from db.models import Source

router = APIRouter(prefix="/sources", tags=["sources"])


@router.post("/upsert")
def upsert_source(payload: dict, db: Session = Depends(get_db), user=RequireUser):
    slug = payload.get("slug")
    adapter = payload.get("adapter")
    kind = payload.get("kind")
    base_url = payload.get("base_url")
    default_config = payload.get("default_config")

    if not slug or not adapter or not kind:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing slug/adapter/kind")

    stmt = insert(Source).values(
        slug=slug,
        adapter=adapter,
        kind=kind,
        base_url=base_url,
        default_config=default_config,
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=[Source.slug],
        set_={
            "adapter": stmt.excluded.adapter,
            "kind": stmt.excluded.kind,
            "base_url": stmt.excluded.base_url,
            "default_config": stmt.excluded.default_config,
        },
    )
    db.execute(stmt)
    db.commit()

    return {"status": "ok", "slug": slug}
