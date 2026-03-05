from __future__ import annotations

from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.services.llm.embeddings import OpenAIEmbeddingsClient
from db.models import UserResumeChunk


def chunk_resume(text: str, max_chars: int = 1200, min_chars: int = 200) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current: list[str] = []
    size = 0
    for paragraph in paragraphs:
        if size + len(paragraph) + 2 > max_chars and current:
            combined = "\n\n".join(current).strip()
            if combined:
                chunks.append(combined)
            current = [paragraph]
            size = len(paragraph)
        else:
            current.append(paragraph)
            size += len(paragraph) + 2

    if current:
        combined = "\n\n".join(current).strip()
        if combined:
            chunks.append(combined)

    normalized: list[str] = []
    for chunk in chunks:
        if len(chunk) >= min_chars:
            normalized.append(chunk)
        else:
            if normalized:
                normalized[-1] = f"{normalized[-1]}\n\n{chunk}".strip()
            else:
                normalized.append(chunk)
    return normalized


def upsert_resume_chunks(db: Session, user_id: str, resume_text: str) -> int:
    chunks = chunk_resume(resume_text)
    db.execute(delete(UserResumeChunk).where(UserResumeChunk.user_id == user_id))

    embeddings: list[list[float]] = []
    try:
        client = OpenAIEmbeddingsClient()
        embeddings = [item.embedding for item in client.embed(chunks)]
    except Exception:
        embeddings = [[] for _ in chunks]

    for idx, chunk in enumerate(chunks):
        embedding = embeddings[idx] if idx < len(embeddings) else []
        db.add(
            UserResumeChunk(
                user_id=user_id,
                chunk_index=idx,
                chunk_text=chunk,
                embedding=embedding,
                chunk_metadata={"length": len(chunk)},
            )
        )
    return len(chunks)


def get_resume_chunks(db: Session, user_id: str, limit: int = 5) -> list[UserResumeChunk]:
    return (
        db.execute(
            select(UserResumeChunk)
            .where(UserResumeChunk.user_id == user_id)
            .order_by(UserResumeChunk.chunk_index.asc())
            .limit(limit)
        )
        .scalars()
        .all()
    )
