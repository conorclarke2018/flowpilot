# FlowPilot

AI-powered workflow automation for small businesses. Users build workflows that combine triggers, deterministic logic, AI processing, and human approval before consequential actions.

Product spec and planning history: [docs/flowpilot-chat-history.md](docs/flowpilot-chat-history.md)

## Stack

- **apps/web** — Vite, React, TypeScript, Mantine, React Flow, React Router, TanStack Query
- **services/api** — FastAPI, SQLAlchemy 2, Alembic, Celery
- **PostgreSQL** + **Redis**

## Local development

### Option A — Docker Compose (closest to production)

```bash
cp .env.example .env
docker compose up --build
docker exec saasproject-api-1 uv run alembic upgrade head
```

### Option B — native, faster reloads

Requires Postgres + Redis running locally (e.g. `docker compose up -d postgres redis`) and the API deps synced (`cd services/api && uv sync`).

```bash
pnpm install
pnpm dev          # runs the Vite dev server and FastAPI (uvicorn --reload) together
pnpm run dev:worker   # in a second terminal, if you need Celery/background runs
```

- Web: http://localhost:5173
- API: http://localhost:8000/api/v1/health
- Interactive API docs: http://localhost:8000/docs

Other root scripts: `pnpm test:api`, `pnpm lint` (web + api), `pnpm typecheck:web`, `pnpm build:web`.

## Repository layout

```
apps/web/              Vite + React app
services/api/           FastAPI app + Celery worker
packages/workflow-contracts/  Shared workflow schema docs
infra/terraform/        Cloud deployment (future milestone)
docs/                   Specs and architecture decisions
```

## Status

Milestones M1–M5 complete (foundation, workflow contracts/CRUD, execution engine, visual editor, AI integration). See `docs/flowpilot-chat-history.md` for the full roadmap.
