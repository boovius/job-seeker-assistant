from __future__ import annotations

from typing import Any, Iterable


def build_queries(config: dict[str, Any]) -> list[dict[str, Any]]:
    profiles = config.get("search_profiles")
    if not profiles:
        return []

    queries: list[dict[str, Any]] = []
    for profile in profiles:
        role_keywords = profile.get("role_keywords", [])
        sector_keywords = profile.get("sector_keywords", [])
        extra_keywords = profile.get("extra_keywords", [])
        location = profile.get("location")
        remote = profile.get("remote")

        keywords = [*role_keywords, *sector_keywords, *extra_keywords]
        query = {
            "keywords": " ".join([kw for kw in keywords if kw]),
            "location": location,
            "remote": remote,
        }
        queries.append(query)

    return queries
