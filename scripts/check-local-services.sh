#!/usr/bin/env bash
# Fails fast with one clear line instead of letting uvicorn/Celery hit a
# dead Postgres/Redis and dump a 50KB SQLAlchemy traceback into the log.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

DB_HOST="localhost"
DB_PORT="5433"
REDIS_HOST="localhost"
REDIS_PORT="6380"

if [ -f .env ]; then
  # Pull host/port out of DATABASE_URL / REDIS_URL if set there.
  db_url=$(grep -E '^DATABASE_URL=' .env | head -1 | cut -d= -f2- || true)
  redis_url=$(grep -E '^REDIS_URL=' .env | head -1 | cut -d= -f2- || true)
  if [ -n "$db_url" ]; then
    hostport=$(echo "$db_url" | sed -E 's#.*@([^/]+)/.*#\1#')
    DB_HOST="${hostport%%:*}"
    DB_PORT="${hostport##*:}"
  fi
  if [ -n "$redis_url" ]; then
    hostport=$(echo "$redis_url" | sed -E 's#redis://([^/]+)/.*#\1#')
    REDIS_HOST="${hostport%%:*}"
    REDIS_PORT="${hostport##*:}"
  fi
fi

check_port() {
  local host="$1" port="$2" name="$3"
  if ! (exec 3<>"/dev/tcp/${host}/${port}") 2>/dev/null; then
    echo ""
    echo "✗ ${name} is not reachable at ${host}:${port}"
    echo ""
    echo "  Start it with:  docker compose up -d postgres redis"
    echo "  Then apply migrations once if needed:"
    echo "    cd services/api && uv run alembic upgrade head"
    echo ""
    exit 1
  fi
  exec 3<&- 3>&- 2>/dev/null || true
}

check_port "$DB_HOST" "$DB_PORT" "Postgres"
check_port "$REDIS_HOST" "$REDIS_PORT" "Redis"
