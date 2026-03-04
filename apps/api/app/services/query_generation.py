from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session

from app.services.user_profiles import get_preference_profile, get_resume, get_value_profile
from db.models import Source, UserSource


class SearchProfile(BaseModel):
    role_keywords: list[str] = Field(default_factory=list)
    sector_keywords: list[str] = Field(default_factory=list)
    location: str | None = None
    remote: bool | None = None


class LLMSearchProfiles(BaseModel):
    search_profiles: list[SearchProfile] = Field(default_factory=list)


KEYWORD_ADAPTERS = {"remotive_api_v1", "adzuna_api_v1", "jooble_api_v1"}


def _fallback_profiles(pref: Any | None) -> LLMSearchProfiles:
    if not pref:
        return LLMSearchProfiles()
    role = pref.target_role or ""
    sector = pref.sector or ""
    if not role and not sector:
        return LLMSearchProfiles()
    return LLMSearchProfiles(
        search_profiles=[
            SearchProfile(
                role_keywords=[role] if role else [],
                sector_keywords=[sector] if sector else [],
                location=pref.location,
                remote=True if pref.work_mode == "remote" else None,
            )
        ]
    )


def build_llm_prompt(pref: Any | None, values: Any | None, resume: str | None) -> str:
    return (
        "Create search_profiles JSON for job discovery.\n"
        "Return JSON in this shape:\n"
        "{ \"search_profiles\": [\n"
        "  {\"role_keywords\": [\"...\"], \"sector_keywords\": [\"...\"], \"location\": \"...\", \"remote\": true}\n"
        "]}\n\n"
        f"Preferences: {pref}\n"
        f"Values: {values}\n"
        f"Resume: {resume}\n"
        "Keep role and sector keywords short. Use up to 5 profiles."
    )


def generate_profiles(db: Session, user_id: str) -> LLMSearchProfiles:
    pref = get_preference_profile(db, user_id)
    values = get_value_profile(db, user_id)
    resume = get_resume(db, user_id)
    resume_text = resume.resume_text if resume else None

    if not pref and not values:
        return LLMSearchProfiles()

    try:
        from app.services.llm.openai_client import OpenAIQueryGenerator

        generator = OpenAIQueryGenerator()
        prompt = build_llm_prompt(pref, values, resume_text)
        return generator.generate(prompt)
    except (ImportError, ValueError, ValidationError):
        return _fallback_profiles(pref)


def apply_profiles_to_sources(db: Session, user_id: str, profiles: LLMSearchProfiles) -> int:
    if not profiles.search_profiles:
        return 0

    rows = (
        db.query(Source, UserSource)
        .join(UserSource, UserSource.source_id == Source.id)
        .filter(UserSource.user_id == user_id)
        .filter(UserSource.enabled.is_(True))
        .all()
    )

    updated = 0
    for source, user_source in rows:
        if source.adapter not in KEYWORD_ADAPTERS:
            continue
        filters = dict(user_source.filters or {})
        filters["search_profiles"] = [profile.model_dump() for profile in profiles.search_profiles]
        user_source.filters = filters
        db.add(user_source)
        updated += 1

    return updated
