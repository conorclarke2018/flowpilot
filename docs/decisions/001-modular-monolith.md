# ADR-001: Modular monolith, not microservices

## Status

Accepted

## Context

FlowPilot has several logically distinct responsibilities: a REST API, a workflow
execution engine, an AI provider layer, and a background worker for async runs.
It would be possible to split these into separate deployable services from day
one — an "API service," an "execution service," an "AI service" — communicating
over HTTP or a message bus.

## Decision

Build a single FastAPI application (`services/api`) containing all domain logic
(`app/engine`, `app/nodes`, `app/providers`, `app/services`), with **one**
separate deployable unit: a Celery worker process that imports and runs the same
codebase in a different mode (`uv run celery -A app.workers.celery_app worker`).
Both processes share the same Python package, the same SQLAlchemy models, and
the same `app/engine/executor.py` — the worker is not a different application,
it's the same application started differently.

## Alternatives considered

- **Microservices per domain** (API service, execution service, AI service):
  rejected. At this scale it buys nothing — there's one team, one deploy
  cadence, and no component has a scaling profile different enough from the
  others to justify the operational cost (service discovery, inter-service
  auth, distributed tracing, N deployment pipelines instead of one). It would
  have slowed every feature in this build by requiring a network boundary
  between the API and the engine that didn't need one.
- **Everything synchronous in the API process, no worker at all**: rejected
  because workflow runs can pause indefinitely waiting on a human approval
  (see ADR-006) — that cannot live inside a request/response cycle.

## Consequences

- Fast iteration: adding the `human.approval` node type (ADR-006) touched the
  executor, the run service, and a new API router, all in one deploy, one test
  run, one PR.
- The worker and API *can* drift if someone edits `app/engine/executor.py`
  without restarting both processes in dev — in practice this surfaced during
  development as "I changed the executor but the running worker didn't pick it
  up" confusion, solved by `--reload` on the API and a manual worker restart.
  Acceptable tradeoff for a single-developer/small-team project.
- If a specific component (e.g. AI classification) ever needs independent
  scaling or a different language runtime, it can be extracted later — the
  `app/providers/` abstraction (ADR-004) already isolates that boundary,
  so extraction wouldn't require a rewrite, just a new transport.
