from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from db.models import PipelineEvent


def log_event(
    db: Session,
    event_type: str,
    message: str | None = None,
    payload: dict[str, Any] | None = None,
    user_id: str | None = None,
    task_id: str | None = None,
) -> None:
    db.add(
        PipelineEvent(
            user_id=user_id,
            task_id=task_id,
            event_type=event_type,
            message=message,
            payload=payload,
        )
    )
