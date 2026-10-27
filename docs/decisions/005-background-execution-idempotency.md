# ADR-005: Async execution via Celery, with idempotent run creation

## Status

Accepted

## Context

A workflow run must not block the HTTP request that starts it — some runs
pause for human approval and may not finish for hours. The API also needs to
protect against duplicate runs if a client retries a request (e.g. a flaky
network causing a double-submit of "start this run").

## Decision

`POST /workflows/{id}/runs` creates a `WorkflowRun` row with status `queued`,
returns `202 Accepted` immediately, and enqueues `execute_run_task.delay(...)`
(`app/workers/tasks.py`) rather than running the engine inline. The actual
Celery worker process imports the same `app/engine/executor.py` used by tests
(ADR-001) — there is no separate "worker-only" execution path to drift from
the one under test.

Idempotency is handled at the request layer, not the queue layer: the client
may pass an `idempotency_key`; `create_run` (`app/services/runs.py`) checks for
an existing run with the same `(workflow_id, idempotency_key)` pair before
inserting, enforced by a unique constraint
(`uq_run_idempotency_key`) so a race between two near-simultaneous requests
still can't create two rows. A retried request returns the *original* run,
not a new one.

Per-node retries and timeouts (`app/engine/executor.py::_run_with_retries_and_timeout`)
are configured per-node in the workflow definition (`max_retries`,
`retry_backoff_seconds`, `timeout_seconds`) rather than globally — a slow AI
call and a fast mock-email send have different reasonable timeout values, and
a single engine-wide setting would be wrong for one of them by construction.

## Alternatives considered

- **Run workflows synchronously in the request handler**: rejected
  immediately — incompatible with human-approval pauses (ADR-006) and with
  the spec's explicit requirement that "execution should be asynchronous."
- **Idempotency via a Celery task ID / message deduplication**: rejected.
  Celery's own deduplication operates at the queue/broker level and doesn't
  protect against the actual failure mode here (a client retrying the HTTP
  `POST` before any task was ever enqueued). The unique-constraint-at-creation
  approach catches it earlier and more simply.
- **One global `EXECUTION_TIMEOUT` setting**: rejected per above — node-level
  config matched the real variance in node runtimes better than a single
  engine-wide number would have.

## Consequences

- `execute_run` explicitly `return`s early if `run.status != "queued"`
  (`app/services/runs.py`) — this one guard is what makes it safe to call the
  same Celery task twice (e.g. once from `create_run`'s initial enqueue, and
  again after an approval decision re-queues the same run; see ADR-006). No
  separate "is this a resume?" flag was needed because the status field
  already encodes it.
- Timeouts are enforced via a `ThreadPoolExecutor` wrapping each node handler
  call, which has real overhead (thread spawn per attempt) — acceptable given
  node counts per workflow are small (single digits), would need revisiting
  for workflows with hundreds of nodes.
