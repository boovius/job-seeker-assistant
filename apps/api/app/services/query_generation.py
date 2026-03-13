from __future__ import annotations

from typing import Any

import json

from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session

from app.services.resume_chunks import get_resume_chunks
from app.services.user_profiles import get_preference_profile, get_resume, get_value_profile
from app.services.pipeline_events import log_event
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


def build_llm_prompt(pref: Any | None, values: Any | None, resume: str | None, resume_chunks: list[str]) -> str:
    pref_payload = (
        {
            "location": pref.location,
            "work_mode": pref.work_mode,
            "salary_min": pref.salary_min,
            "salary_max": pref.salary_max,
            "salary_currency": pref.salary_currency,
            "salary_period": pref.salary_period,
            "sector": pref.sector,
            "target_role": pref.target_role,
            "company_size": pref.company_size,
        }
        if pref
        else None
    )
    values_payload = (
        {"values": values.values, "dream_job_description": values.dream_job_description} if values else None
    )
    schema = json.dumps(LLMSearchProfiles.model_json_schema(), indent=2)
    return (
        "Create search_profiles JSON for job discovery.\n"
        "Return ONLY JSON that matches this Pydantic JSON schema:\n"
        f"{schema}\n\n"
        "Return JSON in this shape:\n"
        "{ \"search_profiles\": [\n"
        "  {\"role_keywords\": [\"...\"], \"sector_keywords\": [\"...\"], \"location\": \"...\", \"remote\": true}\n"
        "]}\n\n"
        f"Preferences: {pref_payload}\n"
        f"Values: {values_payload}\n"
        f"Resume: {resume}\n"
        f"ResumeChunks: {resume_chunks}\n"
        "Keep role and sector keywords short. Use up to 5 profiles."
    )


def generate_profiles(db: Session, user_id: str) -> LLMSearchProfiles:
    pref = get_preference_profile(db, user_id)
    values = get_value_profile(db, user_id)
    resume = get_resume(db, user_id)
    resume_text = resume.resume_text if resume else None
    chunks = [chunk.chunk_text for chunk in get_resume_chunks(db, user_id, limit=5)]

    if not pref and not values:
        log_event(
            db,
            event_type="llm_profiles_debug_skip",
            message="Skipped LLM generation (no preferences or values)",
            payload={"has_preferences": False, "has_values": False, "has_resume": bool(resume_text)},
            user_id=user_id,
        )
        return LLMSearchProfiles()

    try:
        from app.services.llm.openai_client import OpenAIQueryGenerator

        generator = OpenAIQueryGenerator()
        prompt = build_llm_prompt(pref, values, resume_text, chunks)
        log_event(
            db,
            event_type="llm_prompt_debug",
            message="Built LLM prompt for search profiles",
            payload={
                "prompt_preview": prompt[:2000],
                "prompt_length": len(prompt),
                "has_preferences": bool(pref),
                "has_values": bool(values),
                "has_resume": bool(resume_text),
                "resume_chunks": len(chunks),
            },
            user_id=user_id,
        )
        profiles = generator.generate(prompt)
        if generator.last_response_content:
            log_event(
                db,
                event_type="llm_response_debug",
                message="LLM raw response (truncated)",
                payload={
                    "response_preview": generator.last_response_content[:2000],
                    "response_length": len(generator.last_response_content),
                },
                user_id=user_id,
            )
        log_event(
            db,
            event_type="llm_profiles_debug",
            message="LLM generated search profiles",
            payload={"profiles": [profile.model_dump() for profile in profiles.search_profiles]},
            user_id=user_id,
        )
        return profiles
    except (ImportError, ValueError, ValidationError) as exc:
        log_event(
            db,
            event_type="llm_profiles_debug_error",
            message="LLM generation failed; falling back",
            payload={"error_type": exc.__class__.__name__, "error": str(exc)},
            user_id=user_id,
        )
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
