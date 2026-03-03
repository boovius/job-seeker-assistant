#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

if [[ -f "$ROOT_DIR/.env" ]]; then
  set -a
  source "$ROOT_DIR/.env"
  set +a
fi

export VITE_SUPABASE_URL=${VITE_SUPABASE_URL:-${SUPABASE_URL:-}}
export VITE_SUPABASE_ANON_KEY=${VITE_SUPABASE_ANON_KEY:-${SUPABASE_ANON_KEY:-}}

cd "$ROOT_DIR/apps/web"

if [[ ! -d "node_modules" ]]; then
  npm install
fi

npm run dev
