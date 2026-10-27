#!/usr/bin/env bash
# Makes sure Postgres/Redis are up and migrated before uvicorn/Celery try to
# connect — auto-starts them via Docker Compose if they're down, instead of
# letting a dead DB surface as a 50KB SQLAlchemy connection-refused
# traceback on the first incoming request.
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

port_open() {
  local host="$1" port="$2"
  (exec 3<>"/dev/tcp/${host}/${port}") 2>/dev/null
  local result=$?
  exec 3<&- 3>&- 2>/dev/null || true
  return $result
}

both_ports_open() {
  port_open "$DB_HOST" "$DB_PORT" && port_open "$REDIS_HOST" "$REDIS_PORT"
}

if ! both_ports_open; then
  echo "→ Postgres/Redis not reachable, starting them (docker compose up -d postgres redis)..."

  if ! docker compose up -d postgres redis; then
    echo ""
    echo "✗ Could not start Postgres/Redis — is Docker running?"
    echo ""
    exit 1
  fi

  echo -n "→ Waiting for Postgres to accept connections"
  ready=false
  for _ in $(seq 1 30); do
    if both_ports_open; then
      echo " ready."
      ready=true
      break
    fi
    echo -n "."
    sleep 1
  done

  if [ "$ready" != true ]; then
    echo ""
    echo "✗ Postgres/Redis still not reachable at ${DB_HOST}:${DB_PORT} / ${REDIS_HOST}:${REDIS_PORT} after 30s"
    echo "  Check: docker compose logs postgres redis"
    exit 1
  fi
fi

if ! (cd services/api && uv run alembic upgrade head >/tmp/flowpilot-migrate.log 2>&1); then
  echo ""
  echo "✗ Migrations failed:"
  cat /tmp/flowpilot-migrate.log
  exit 1
fi
