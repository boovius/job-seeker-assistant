from __future__ import annotations

import os
from typing import Iterable

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from db.models import Source, UserSource


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _get_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def _upsert_source(db: Session, *, slug: str, adapter: str, kind: str, base_url: str, default_config: dict) -> Source:
    source = db.execute(select(Source).where(Source.slug == slug)).scalar_one_or_none()
    if source:
        source.adapter = adapter
        source.kind = kind
        source.base_url = base_url
        source.default_config = default_config
        db.add(source)
        db.flush()
        return source

    source = Source(
        slug=slug,
        adapter=adapter,
        kind=kind,
        base_url=base_url,
        default_config=default_config,
    )
    db.add(source)
    db.flush()
    return source


def _ensure_user_source(db: Session, user_id: str, source: Source) -> None:
    existing = (
        db.execute(
            select(UserSource)
            .where(UserSource.user_id == user_id)
            .where(UserSource.source_id == source.id)
        )
        .scalar_one_or_none()
    )
    if existing:
        return
    db.add(UserSource(user_id=user_id, source_id=source.id, enabled=True, weight=1))


def main() -> None:
    database_url = _get_env("DATABASE_URL")
    user_id = _get_env("SUPABASE_USER_ID")

    greenhouse_tokens = _split_csv(os.getenv("GREENHOUSE_BOARD_TOKENS"))
    lever_companies = _split_csv(os.getenv("LEVER_COMPANIES"))

    engine = create_engine(database_url, pool_pre_ping=True)

    with Session(engine) as db:
        greenhouse = _upsert_source(
            db,
            slug="greenhouse",
            adapter="greenhouse_job_board_v1",
            kind="ats_api",
            base_url="https://boards.greenhouse.io",
            default_config={"board_tokens": greenhouse_tokens},
        )
        lever = _upsert_source(
            db,
            slug="lever",
            adapter="lever_postings_v1",
            kind="ats_api",
            base_url="https://jobs.lever.co",
            default_config={"companies": lever_companies},
        )

        _ensure_user_source(db, user_id, greenhouse)
        _ensure_user_source(db, user_id, lever)

        db.commit()
        print("Seeded sources for user", user_id)


if __name__ == "__main__":
    main()
