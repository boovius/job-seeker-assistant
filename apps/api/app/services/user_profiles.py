from __future__ import annotations

import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import UserPreferenceProfile, UserValueProfile


def _parse_salary(value: Any) -> tuple[int | None, int | None, str | None, str | None]:
    if isinstance(value, dict):
        minimum = value.get("min")
        maximum = value.get("max")
        currency = value.get("currency")
        period = value.get("period")
        return (
            _to_int(minimum),
            _to_int(maximum),
            currency if isinstance(currency, str) else None,
            period if isinstance(period, str) else None,
        )

    if isinstance(value, (int, float)):
        return int(value), None, None, None

    if isinstance(value, str):
        numbers = re.findall(r"\\d+(?:\\.\\d+)?", value.replace(",", ""))
        if not numbers:
            return None, None, None, None
        normalized = [_normalize_amount(n, value) for n in numbers]
        minimum = normalized[0] if "+" in value or len(normalized) == 1 else normalized[0]
        maximum = normalized[1] if len(normalized) > 1 else None
        return minimum, maximum, None, _parse_salary_period(value)

    return None, None, None, None


def _normalize_amount(amount: str, raw: str) -> int:
    value = float(amount)
    if re.search(r"\\b[kK]\\b", raw) or "k" in raw.lower():
        value *= 1000
    return int(value)


def _parse_salary_period(value: str) -> str | None:
    lowered = value.lower()
    if "hour" in lowered or "/hr" in lowered or "hr" in lowered:
        return "hour"
    if "month" in lowered or "/mo" in lowered:
        return "month"
    if "week" in lowered or "/wk" in lowered:
        return "week"
    if "day" in lowered or "/day" in lowered:
        return "day"
    if "year" in lowered or "/yr" in lowered or "annual" in lowered or "per year" in lowered:
        return "year"
    return None


def _to_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def apply_user_profiles(db: Session, user_id: str, config_json: dict[str, Any]) -> None:
    core_preferences = config_json.get("core_preferences") or {}
    core_values = config_json.get("core_values") or {}

    salary_min, salary_max, salary_currency, salary_period = _parse_salary(core_preferences.get("salary"))

    pref = (
        db.execute(select(UserPreferenceProfile).where(UserPreferenceProfile.user_id == user_id))
        .scalar_one_or_none()
    )
    if pref:
        pref.location = core_preferences.get("location")
        pref.work_mode = core_preferences.get("work_mode")
        pref.salary_min = salary_min
        pref.salary_max = salary_max
        pref.salary_currency = salary_currency
        pref.salary_period = salary_period
        pref.sector = core_preferences.get("sector")
        pref.target_role = core_preferences.get("target_role")
        pref.company_size = core_preferences.get("company_size")
        db.add(pref)
    else:
        db.add(
            UserPreferenceProfile(
                user_id=user_id,
                location=core_preferences.get("location"),
                work_mode=core_preferences.get("work_mode"),
                salary_min=salary_min,
                salary_max=salary_max,
                salary_currency=salary_currency,
                salary_period=salary_period,
                sector=core_preferences.get("sector"),
                target_role=core_preferences.get("target_role"),
                company_size=core_preferences.get("company_size"),
            )
        )

    values = core_values.get("values")
    if values is not None and not isinstance(values, list):
        values = [values]

    val = (
        db.execute(select(UserValueProfile).where(UserValueProfile.user_id == user_id))
        .scalar_one_or_none()
    )
    if val:
        val.values = values
        val.dream_job_description = core_values.get("dream_job_description")
        db.add(val)
    else:
        db.add(
            UserValueProfile(
                user_id=user_id,
                values=values,
                dream_job_description=core_values.get("dream_job_description"),
            )
        )


def get_preference_profile(db: Session, user_id: str) -> UserPreferenceProfile | None:
    return (
        db.execute(select(UserPreferenceProfile).where(UserPreferenceProfile.user_id == user_id))
        .scalar_one_or_none()
    )


def upsert_preference_profile(db: Session, user_id: str, payload: dict[str, Any]) -> UserPreferenceProfile:
    salary_min, salary_max, salary_currency, salary_period = _parse_salary(payload.get("salary"))
    pref = get_preference_profile(db, user_id)
    if pref:
        pref.location = payload.get("location")
        pref.work_mode = payload.get("work_mode")
        pref.salary_min = payload.get("salary_min", salary_min)
        pref.salary_max = payload.get("salary_max", salary_max)
        pref.salary_currency = payload.get("salary_currency", salary_currency)
        pref.salary_period = payload.get("salary_period", salary_period)
        pref.sector = payload.get("sector")
        pref.target_role = payload.get("target_role")
        pref.company_size = payload.get("company_size")
        db.add(pref)
        return pref
    pref = UserPreferenceProfile(
        user_id=user_id,
        location=payload.get("location"),
        work_mode=payload.get("work_mode"),
        salary_min=payload.get("salary_min", salary_min),
        salary_max=payload.get("salary_max", salary_max),
        salary_currency=payload.get("salary_currency", salary_currency),
        salary_period=payload.get("salary_period", salary_period),
        sector=payload.get("sector"),
        target_role=payload.get("target_role"),
        company_size=payload.get("company_size"),
    )
    db.add(pref)
    return pref


def get_value_profile(db: Session, user_id: str) -> UserValueProfile | None:
    return (
        db.execute(select(UserValueProfile).where(UserValueProfile.user_id == user_id))
        .scalar_one_or_none()
    )


def upsert_value_profile(db: Session, user_id: str, payload: dict[str, Any]) -> UserValueProfile:
    values = payload.get("values")
    if values is not None and not isinstance(values, list):
        values = [values]
    val = get_value_profile(db, user_id)
    if val:
        val.values = values
        val.dream_job_description = payload.get("dream_job_description")
        db.add(val)
        return val
    val = UserValueProfile(
        user_id=user_id,
        values=values,
        dream_job_description=payload.get("dream_job_description"),
    )
    db.add(val)
    return val
