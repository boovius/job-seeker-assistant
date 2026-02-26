from __future__ import annotations

from sqlalchemy.orm import Session

from app.services.adapters import SourceRegistryEntry
from db.models import Source, UserSource


def list_enabled_sources(db: Session, user_id: str):
    return (
        db.query(Source, UserSource)
        .join(UserSource, UserSource.source_id == Source.id)
        .filter(UserSource.user_id == user_id)
        .filter(UserSource.enabled.is_(True))
        .all()
    )


def to_registry_entry(source: Source, user_source: UserSource | None = None) -> SourceRegistryEntry:
    weight = float(user_source.weight) if user_source else 1.0
    enabled = user_source.enabled if user_source else True
    config = source.default_config or {}
    if user_source and user_source.filters:
        config = {**config, **user_source.filters}

    return SourceRegistryEntry(
        slug=source.slug,
        adapter=source.adapter,
        kind=source.kind,
        base_url=source.base_url,
        enabled=enabled,
        weight=weight,
        config=config,
    )
