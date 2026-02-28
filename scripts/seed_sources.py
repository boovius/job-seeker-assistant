from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from db.models import Source, UserSource


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


def _ensure_user_source(db: Session, user_id: str, source: Source, enabled: bool) -> None:
    existing = (
        db.execute(
            select(UserSource)
            .where(UserSource.user_id == user_id)
            .where(UserSource.source_id == source.id)
        )
        .scalar_one_or_none()
    )
    if existing:
        existing.enabled = enabled
        db.add(existing)
        return
    db.add(UserSource(user_id=user_id, source_id=source.id, enabled=enabled, weight=1))


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing config file: {path}")
    return yaml.safe_load(path.read_text())


def main() -> None:
    database_url = _get_env("DATABASE_URL")
    user_id = _get_env("SUPABASE_USER_ID")

    config_path = Path(os.getenv("SOURCES_CONFIG", "config/sources.yaml"))
    config = _load_yaml(config_path)
    sources = config.get("sources", {})

    engine = create_engine(database_url, pool_pre_ping=True)

    with Session(engine) as db:
        for slug, entry in sources.items():
            adapter = entry.get("adapter")
            kind = entry.get("kind")
            base_url = entry.get("base_url")
            enabled = bool(entry.get("enabled", True))
            cfg = entry.get("config", {})
            if not adapter or not kind:
                raise RuntimeError(f"Missing adapter/kind for source {slug}")

            source = _upsert_source(
                db,
                slug=slug,
                adapter=adapter,
                kind=kind,
                base_url=base_url,
                default_config=cfg,
            )
            _ensure_user_source(db, user_id, source, enabled)

        db.commit()
        print("Seeded sources for user", user_id)


if __name__ == "__main__":
    main()
