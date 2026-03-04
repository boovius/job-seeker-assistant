from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import RequireUser
from app.db.deps import get_db
from app.services.user_profiles import (
    get_preference_profile,
    get_value_profile,
    upsert_preference_profile,
    upsert_value_profile,
)

router = APIRouter(prefix="/user", tags=["user"])


class PreferencePayload(BaseModel):
    location: str | None = None
    work_mode: str | None = None
    salary: str | dict | int | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str | None = None
    salary_period: str | None = None
    sector: str | None = None
    target_role: str | None = None
    company_size: str | None = None


class PreferenceResponse(BaseModel):
    location: str | None
    work_mode: str | None
    salary_min: int | None
    salary_max: int | None
    salary_currency: str | None
    salary_period: str | None
    sector: str | None
    target_role: str | None
    company_size: str | None


class ValuePayload(BaseModel):
    values: list[str] | str | None = None
    dream_job_description: str | None = None


class ValueResponse(BaseModel):
    values: list[str] | None
    dream_job_description: str | None


@router.get("/preferences", response_model=PreferenceResponse)
def get_preferences(db: Session = Depends(get_db), user=RequireUser):
    user_id = user.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user id")
    pref = get_preference_profile(db, user_id)
    if not pref:
        return PreferenceResponse(
            location=None,
            work_mode=None,
            salary_min=None,
            salary_max=None,
            salary_currency=None,
            sector=None,
            target_role=None,
            company_size=None,
        )
    return PreferenceResponse(
        location=pref.location,
        work_mode=pref.work_mode,
        salary_min=pref.salary_min,
        salary_max=pref.salary_max,
        salary_currency=pref.salary_currency,
        salary_period=pref.salary_period,
        sector=pref.sector,
        target_role=pref.target_role,
        company_size=pref.company_size,
    )


@router.put("/preferences")
def update_preferences(payload: PreferencePayload, db: Session = Depends(get_db), user=RequireUser):
    user_id = user.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user id")
    upsert_preference_profile(db, user_id, payload.model_dump())
    db.commit()
    return {"status": "ok"}


@router.get("/values", response_model=ValueResponse)
def get_values(db: Session = Depends(get_db), user=RequireUser):
    user_id = user.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user id")
    val = get_value_profile(db, user_id)
    if not val:
        return ValueResponse(values=None, dream_job_description=None)
    return ValueResponse(values=val.values, dream_job_description=val.dream_job_description)


@router.put("/values")
def update_values(payload: ValuePayload, db: Session = Depends(get_db), user=RequireUser):
    user_id = user.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user id")
    upsert_value_profile(db, user_id, payload.model_dump())
    db.commit()
    return {"status": "ok"}
