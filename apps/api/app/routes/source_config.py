from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import RequireUser
from app.db.deps import get_db
from app.services.source_config import apply_sources, get_yaml_or_file, upsert_config

router = APIRouter(prefix="/source-config", tags=["source-config"])


@router.get("")
def get_source_config(db: Session = Depends(get_db), user=RequireUser):
    user_id = user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Missing user id")

    yaml_text, source = get_yaml_or_file(db, user_id)
    return {"yaml": yaml_text, "source": source}


@router.put("")
def update_source_config(payload: dict, db: Session = Depends(get_db), user=RequireUser):
    user_id = user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Missing user id")

    yaml_text = payload.get("yaml")
    if not yaml_text or not isinstance(yaml_text, str):
        raise HTTPException(status_code=400, detail="Missing yaml")

    config = upsert_config(db, user_id, yaml_text)
    apply_sources(db, user_id, config.config_json)
    db.commit()

    return {"status": "ok"}
