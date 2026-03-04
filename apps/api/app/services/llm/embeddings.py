from __future__ import annotations

from typing import Any

import httpx
from pydantic import BaseModel, Field

from app.config import settings


class EmbeddingResponse(BaseModel):
    embedding: list[float] = Field(default_factory=list)


class OpenAIEmbeddingsClient:
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise ValueError("Missing OPENAI_API_KEY")
        self.client = httpx.Client(timeout=60)

    def embed(self, inputs: list[str]) -> list[EmbeddingResponse]:
        payload: dict[str, Any] = {
            "model": settings.openai_embeddings_model,
            "input": inputs,
        }
        resp = self.client.post(
            "https://api.openai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        return [EmbeddingResponse(embedding=item["embedding"]) for item in data.get("data", [])]
