from __future__ import annotations

import json
from typing import Any

import httpx

from app.config import settings
from app.services.query_generation import LLMSearchProfiles


class OpenAIQueryGenerator:
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise ValueError("Missing OPENAI_API_KEY")
        self.client = httpx.Client(timeout=60)

    def generate(self, prompt: str) -> LLMSearchProfiles:
        payload: dict[str, Any] = {
            "model": settings.openai_model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that outputs strict JSON."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        resp = self.client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        try:
            return LLMSearchProfiles.model_validate_json(content)
        except Exception:
            parsed = json.loads(content)
            return LLMSearchProfiles.model_validate(parsed)
