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

cd "$ROOT_DIR/apps/api"

if [[ ! -d ".venv" ]]; then
  python -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt

PYTHONPATH="$ROOT_DIR/packages" uvicorn app.main:app --reload --port "${API_PORT:-8010}"
