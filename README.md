<<<<<<< HEAD
# FlowPilot

AI-powered workflow automation for small businesses. Users build workflows that combine triggers, deterministic logic, AI processing, and human approval before consequential actions.

Product spec and planning history: [docs/flowpilot-chat-history.md](docs/flowpilot-chat-history.md)

## Stack

- **apps/web** — Vite, React, TypeScript, Mantine, React Flow, React Router, TanStack Query
- **services/api** — FastAPI, SQLAlchemy 2, Alembic, Celery
- **PostgreSQL** + **Redis**

## Local development

```bash
cp .env.example .env
docker compose up --build
```

- Web: http://localhost:5173
- API: http://localhost:8000/api/v1/health

## Repository layout

```
apps/web/              Vite + React app
services/api/           FastAPI app + Celery worker
packages/workflow-contracts/  Shared workflow schema docs
infra/terraform/        Cloud deployment (future milestone)
docs/                   Specs and architecture decisions
```

## Status

Milestone M1 (foundation) complete. Milestone M2 (workflow contracts, validation, CRUD) in progress — see `docs/flowpilot-chat-history.md` for the full roadmap.
=======
# flowpilot
>>>>>>> 87635429c1758020897117a12c001cbaff59e7e3
