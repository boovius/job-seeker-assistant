from __future__ import annotations

import os
import sys
from pathlib import Path

import click

ROOT = Path(__file__).resolve().parents[1]
API_PATH = ROOT / "apps" / "api"
PACKAGES_PATH = ROOT / "packages"

for path in (ROOT, API_PATH, PACKAGES_PATH):
    if str(path) not in sys.path:
        sys.path.append(str(path))

from scripts.cli_list import list_jobs, list_queue, list_sources  # noqa: E402
from scripts.enqueue_all_sources import main as enqueue_all_main  # noqa: E402
from scripts.run_worker import main as run_worker_main  # noqa: E402
from scripts.seed_sources import main as seed_sources_main  # noqa: E402


@click.group()
def cli() -> None:
    """Job Culler developer CLI."""


@cli.command("seed-sources")
def seed_sources_cmd() -> None:
    """Seed sources and user_sources from env."""
    seed_sources_main()


@cli.command("enqueue-all")
def enqueue_all_cmd() -> None:
    """Enqueue fetch_listings tasks for all enabled sources."""
    enqueue_all_main()


@cli.command("run-worker")
@click.option("--poll-seconds", type=int, default=None)
@click.option("--max-cycles", type=int, default=None)
def run_worker_cmd(poll_seconds: int | None, max_cycles: int | None) -> None:
    """Run the worker loop locally."""
    if poll_seconds is not None:
        os.environ["WORKER_POLL_SECONDS"] = str(poll_seconds)
    if max_cycles is not None:
        os.environ["WORKER_MAX_CYCLES"] = str(max_cycles)
    run_worker_main()


@cli.command("run-pipeline")
@click.option("--poll-seconds", type=int, default=None)
@click.option("--max-cycles", type=int, default=None)
def run_pipeline_cmd(poll_seconds: int | None, max_cycles: int | None) -> None:
    """Enqueue all sources, then run the worker loop."""
    enqueue_all_main()
    if poll_seconds is not None:
        os.environ["WORKER_POLL_SECONDS"] = str(poll_seconds)
    if max_cycles is not None:
        os.environ["WORKER_MAX_CYCLES"] = str(max_cycles)
    run_worker_main()


@cli.command("list-sources")
def list_sources_cmd() -> None:
    """List sources from the database."""
    list_sources()


@cli.command("list-jobs")
def list_jobs_cmd() -> None:
    """List jobs from the database."""
    list_jobs()


@cli.command("list-queue")
@click.option("--failed", is_flag=True, default=False)
def list_queue_cmd(failed: bool) -> None:
    """List workflow queue items from the database."""
    list_queue(failed_only=failed)


if __name__ == "__main__":
    cli()
