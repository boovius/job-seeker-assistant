from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import Source, UserSource, UserSourceConfig


def _load_file_config() -> dict[str, Any]:
    root_dir = Path(__file__).resolve().parents[4]
    path = root_dir / "config" / "sources.yaml"
    if not path.exists():
        raise RuntimeError("Missing config/sources.yaml")
    return yaml.safe_load(path.read_text())


def _merge_secret_config(slug: str, cfg: dict[str, Any]) -> dict[str, Any]:
    import os

    merged = dict(cfg)
    if slug == "adzuna":
        app_id = os.getenv("ADZUNA_APP_ID")
        app_key = os.getenv("ADZUNA_APP_KEY")
        if app_id:
            merged["app_id"] = app_id
        if app_key:
            merged["app_key"] = app_key
    if slug == "jooble":
        api_key = os.getenv("JOOBLE_API_KEY")
        if api_key:
            merged["api_key"] = api_key
    return merged


def get_or_default_config(db: Session, user_id: str) -> UserSourceConfig | None:
    return db.execute(select(UserSourceConfig).where(UserSourceConfig.user_id == user_id)).scalar_one_or_none()


def upsert_config(db: Session, user_id: str, yaml_text: str) -> UserSourceConfig:
    data = yaml.safe_load(yaml_text)
    if not isinstance(data, dict):
        raise ValueError("Invalid config format")

    config = db.execute(select(UserSourceConfig).where(UserSourceConfig.user_id == user_id)).scalar_one_or_none()
    if config:
        config.yaml_text = yaml_text
        config.config_json = data
        db.add(config)
    else:
        config = UserSourceConfig(user_id=user_id, yaml_text=yaml_text, config_json=data)
        db.add(config)
    db.flush()
    return config


def apply_sources(db: Session, user_id: str, config_json: dict[str, Any]) -> None:
    sources = config_json.get("sources", {})
    for slug, entry in sources.items():
        adapter = entry.get("adapter")
        kind = entry.get("kind")
        base_url = entry.get("base_url")
        enabled = bool(entry.get("enabled", True))
        cfg = entry.get("config", {})
        if not adapter or not kind:
            raise ValueError(f"Missing adapter/kind for source {slug}")

        cfg = _merge_secret_config(slug, cfg)

        source = db.execute(select(Source).where(Source.slug == slug)).scalar_one_or_none()
        if source:
            source.adapter = adapter
            source.kind = kind
            source.base_url = base_url
            source.default_config = cfg
            db.add(source)
        else:
            source = Source(
                slug=slug,
                adapter=adapter,
                kind=kind,
                base_url=base_url,
                default_config=cfg,
            )
            db.add(source)
        db.flush()

        user_source = (
            db.execute(
                select(UserSource)
                .where(UserSource.user_id == user_id)
                .where(UserSource.source_id == source.id)
            )
            .scalar_one_or_none()
        )
        if user_source:
            user_source.enabled = enabled
            db.add(user_source)
        else:
            db.add(UserSource(user_id=user_id, source_id=source.id, enabled=enabled, weight=1))


def get_yaml_or_file(db: Session, user_id: str) -> tuple[str, str]:
    existing = get_or_default_config(db, user_id)
    if existing:
        return existing.yaml_text, "db"
    data = _load_file_config()
    return yaml.safe_dump(data, sort_keys=False), "file"
