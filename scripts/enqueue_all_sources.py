from __future__ import annotations

import os

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from db.models import Source, UserSource, WorkflowQueue


def _get_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def main() -> None:
    database_url = _get_env("DATABASE_URL")
    user_id = _get_env("SUPABASE_USER_ID")

    engine = create_engine(database_url, pool_pre_ping=True)
    with Session(engine) as db:
        rows = (
            db.execute(
                select(Source, UserSource)
                .join(UserSource, UserSource.source_id == Source.id)
                .where(UserSource.user_id == user_id)
                .where(UserSource.enabled.is_(True))
            )
            .all()
        )

        if not rows:
            print("No enabled sources for user", user_id)
            return

        for source, _ in rows:
            task = WorkflowQueue(task_type="fetch_listings", payload={"source_id": str(source.id), "user_id": user_id})
            db.add(task)

        db.commit()
        print("Enqueued", len(rows), "sources for user", user_id)


if __name__ == "__main__":
    main()
