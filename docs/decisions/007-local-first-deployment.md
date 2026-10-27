# ADR-007: Local-first deployment with portable infrastructure

## Status

Accepted

## Context

The project needed to be fully runnable and testable without any cloud
account, while keeping the door open to a real cloud deployment later without
a rewrite.

## Decision

Two supported local paths, both documented in the README:

- **Docker Compose** (`docker-compose.yml`) — the full stack (postgres, redis,
  api, worker, web) in containers, closest to how it would run in production.
- **Native dev** (`pnpm dev`) — Vite and `uvicorn --reload` run directly on
  the host for fast iteration, against Postgres/Redis still running in
  Docker. A pre-flight script (`scripts/check-local-services.sh`) checks TCP
  connectivity to both before launching anything, so a cold database produces
  one clear message ("Postgres is not reachable at localhost:5433 — start it
  with: docker compose up -d postgres redis") instead of a multi-hundred-line
  SQLAlchemy traceback surfacing on the first incoming request.

No AWS/cloud dependency exists anywhere in the application code — `DATABASE_URL`
and `REDIS_URL` are plain connection strings read from environment via
`pydantic-settings` (`app/core/config.py`), with no AWS SDK, no
cloud-provider-specific client, and no hard-coded endpoint. `infra/terraform/`
is reserved but intentionally empty until there's a real account/region/domain
to target — scaffolding Terraform against nothing would produce modules nobody
could `terraform plan`, let alone `apply`, and would need rewriting once real
constraints (VPC layout, existing DNS, budget) are known anyway.

## Alternatives considered

- **Require AWS (e.g. RDS, ElastiCache) even for local dev**: rejected —
  this would mean no one could clone the repo and run it without a cloud
  account and a credit card, which actively works against the project's
  purpose as a demonstrable, inspectable portfolio piece.
- **Scaffold a full Terraform module tree now, unapplied**: rejected for this
  phase. Speculative infrastructure-as-code that was never run against a real
  account tends to bit-rot and, worse, teaches the wrong lesson in an
  interview setting if asked "did you actually deploy this?" The honest
  answer — local-first by design, cloud deployment is a scoped follow-on
  requiring real account decisions — is the one documented here.
- **`docker-compose up` as the *only* dev path**, no native option: rejected
  after feeling the iteration-speed cost directly — container rebuilds on
  every backend change are meaningfully slower than `uvicorn --reload`, enough
  to justify maintaining both paths.

## Consequences

- Two local dev paths means two things that can drift (e.g. the port-mapping
  bug fixed earlier, where Docker's Postgres and the host's existing
  Postgres.app installation both claimed `5432`, resolved by remapping to
  `5433`/`6380` and documenting it) — an explicit, accepted cost of
  supporting both.
- The eventual cloud deployment (RDS, ElastiCache, ECS/EKS, Secrets Manager)
  is a distinct, separately-scoped piece of work gated on real account access
  — not blocked by anything in the application architecture itself, since
  `DATABASE_URL`/`REDIS_URL` swap transparently from local containers to
  managed services.
