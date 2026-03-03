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

export VITE_SUPABASE_URL=${VITE_SUPABASE_URL:-${SUPABASE_URL:-}}
export VITE_SUPABASE_ANON_KEY=${VITE_SUPABASE_ANON_KEY:-${SUPABASE_ANON_KEY:-}}

cd "$ROOT_DIR/apps/web"

if [[ ! -d "node_modules" ]]; then
  npm install
fi

npm run dev
