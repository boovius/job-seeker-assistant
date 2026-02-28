#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

if [[ -f "$ROOT_DIR/.env" ]]; then
  set -a
  source "$ROOT_DIR/.env"
  set +a
fi

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <EMAIL> <PASSWORD>"
  exit 1
fi

PROJECT_REF="${SUPABASE_PROJECT_REF:-}"
ANON_KEY="${SUPABASE_ANON_KEY:-}"
EMAIL="$1"
PASSWORD="$2"

if [[ -z "$PROJECT_REF" || -z "$ANON_KEY" ]]; then
  echo "Missing SUPABASE_PROJECT_REF or SUPABASE_ANON_KEY in .env"
  exit 1
fi

curl -s \
  -X POST "https://${PROJECT_REF}.supabase.co/auth/v1/token?grant_type=password" \
  -H "apikey: ${ANON_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASSWORD}\"}"
