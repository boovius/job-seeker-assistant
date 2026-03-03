#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
MODE="${1:-local}"
ENV_FILE="$ROOT_DIR/.env"

if [[ "$MODE" == "remote" ]]; then
  ENV_FILE="$ROOT_DIR/.env.remote"
fi

if [[ -f "$ENV_FILE" ]]; then
  set -a
  source "$ENV_FILE"
  set +a
else
  echo "Missing env file: $ENV_FILE"
  exit 1
fi

cd "$ROOT_DIR"

MIGRATION_NAME="${2:-auto}"
PYTHONPATH=packages alembic -c packages/db/alembic.ini upgrade head
PYTHONPATH=packages alembic -c packages/db/alembic.ini revision --autogenerate -m "$MIGRATION_NAME"
