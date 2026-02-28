from __future__ import annotations

from app.services.adapters.adzuna import AdzunaAdapter
from app.services.adapters.base import SourceAdapter
from app.services.adapters.greenhouse import GreenhouseAdapter
from app.services.adapters.jooble import JoobleAdapter
from app.services.adapters.lever import LeverAdapter
from app.services.adapters.remotive import RemotiveAdapter


ADAPTER_REGISTRY: dict[str, type[SourceAdapter]] = {
    "greenhouse_job_board_v1": GreenhouseAdapter,
    "lever_postings_v1": LeverAdapter,
    "remotive_api_v1": RemotiveAdapter,
    "adzuna_api_v1": AdzunaAdapter,
    "jooble_api_v1": JoobleAdapter,
}


def get_adapter(adapter_name: str) -> SourceAdapter:
    adapter_cls = ADAPTER_REGISTRY.get(adapter_name)
    if not adapter_cls:
        raise KeyError(f"Unknown adapter: {adapter_name}")
    return adapter_cls()
