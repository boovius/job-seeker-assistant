#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

if [[ -f "$ROOT_DIR/.env" ]]; then
  set -a
  source "$ROOT_DIR/.env"
  set +a
fi

cd "$ROOT_DIR"

PYTHONPATH=packages alembic -c packages/db/alembic.ini revision --autogenerate -m "${1:-auto}"
PYTHONPATH=packages alembic -c packages/db/alembic.ini upgrade head
