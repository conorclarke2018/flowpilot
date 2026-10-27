# ADR-006: Human approval gates with safe, non-destructive resumption

## Status

Accepted

## Context

Some workflow nodes (e.g. sending an email) are consequential enough that a
human should review and optionally edit the proposed action before it fires.
This requires the execution engine to genuinely *pause* — not poll, not block
a thread — potentially for an arbitrary amount of time, then resume from
exactly where it left off without re-doing (and re-triggering the side
effects of) any node that already ran.

## Decision

`human.approval` is a special-cased node type in the executor
(`app/engine/executor.py`), not a normal handler: reaching one for the first
time resolves its `payload` config from upstream context and returns
immediately with `status="waiting_for_approval"` plus the resolved payload —
the worker task finishes normally (no blocked thread, no polling loop)
and `WorkflowRun.status` becomes `waiting_for_approval`
(`app/services/runs.py`). An `Approval` row is created with the proposed
payload.

Resumption works by **replay with memoization**, not by picking up execution
state mid-function: `execute_workflow` accepts `known_node_outputs`, a map of
node ID → already-computed output. On every call — first run or resume alike
— the executor walks the full topological order but *skips* any node already
present in `known_node_outputs`, re-seeding the context from those cached
outputs instead of re-executing. `_known_node_outputs`
(`app/services/runs.py`) builds this map from persisted `NodeRun` rows plus
any `approved` `Approval.decided_payload`. This means there is exactly one
code path for "run a workflow" — resume isn't a different function, it's the
same function called with a non-empty seed.

Approving records an optional **edited** payload
(`POST /approvals/{id}/decision`) which becomes that approval node's output —
so a human can rewrite a drafted email before it sends, and the edit
genuinely propagates to downstream nodes via the normal `$.node_id.field`
reference mechanism, not a special-cased override. Rejecting sets the run to
`cancelled` and never re-queues it — the downstream action node simply never
runs.

## Alternatives considered

- **Block the Celery worker thread on a `wait()` until a decision arrives**:
  rejected outright — this would hold a worker slot per pending approval
  indefinitely, and the spec is explicit that "the worker releases the task
  rather than blocking a process indefinitely."
- **A separate "resume" execution function with its own logic for
  reconstructing context**: rejected after noticing it would duplicate
  `execute_workflow`'s topological walk and create two places that could
  disagree about execution order. The `known_node_outputs` seed parameter was
  a smaller, safer change.
- **Re-run the whole workflow on resume and let already-"done" nodes
  no-op themselves**: rejected — this would require every node handler to be
  independently idempotent and aware of its own prior execution, pushing
  complexity into every future node type instead of handling it once in the
  executor.

## Consequences

- Verified end-to-end (not just unit-tested): a real browser test approved an
  edited payload through the Approval Inbox UI and confirmed via the API that
  the earlier `trigger` and later `action.mock_email` node-run records showed
  no duplicate side effect, and the email body matched the edited text, not
  the original draft.
- `Approval` records are scoped to `(workflow_run_id, node_id)` — a changed
  proposed payload on a second pass through the same node (not currently
  possible given the DAG-no-loops constraint in ADR-003) would need a new
  approval, by design, rather than silently reusing a stale decision.
