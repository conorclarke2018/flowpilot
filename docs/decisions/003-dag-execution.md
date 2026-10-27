# ADR-003: DAG execution with deterministic topological scheduling

## Status

Accepted

## Context

A workflow is a graph of nodes and edges. The engine needs a scheduling rule
that is predictable (same graph → same execution order, every time), supports
branching, and can be paused and resumed mid-graph (ADR-006) without
re-running nodes that already executed — some of which have external side
effects (`action.mock_email`) that must not fire twice.

## Decision

Restrict the graph to a **directed acyclic graph**: validation
(`app/engine/validation.py`) rejects cycles via DFS white/gray/black coloring,
and requires exactly one trigger node. The executor
(`app/engine/executor.py::_topological_order`) computes a single deterministic
order with Kahn's algorithm, breaking ties by sorting node IDs — so the same
graph always produces the same order, which makes test assertions like
`assert [r.node_id for r in result.node_results] == ["trigger_1", "email_1"]`
meaningful rather than flaky.

Execution is a linear walk of that order. Each node's output is stored in an
`ExecutionContext` keyed by node ID; downstream nodes reference upstream
outputs via `$.node_id.field` string interpolation
(`app/engine/context.py::resolve`). A node that fails stops the walk
immediately — later nodes are never attempted, because an earlier node may
already have had a real-world side effect that a later failure shouldn't mask
or imply should be retried from scratch.

## Alternatives considered

- **Allow cycles / loops in the graph**: rejected for the MVP. Loops need
  explicit termination conditions, cycle-aware scheduling, and change what
  "the execution order" even means. The spec explicitly scoped this out
  ("support branching, but not loops or arbitrary cycles — DAGs are easier to
  validate, schedule and debug"), and nothing in the current node set
  (`trigger.*`, `data.transform`, `ai.classify`, `logic.condition`,
  `human.approval`, `action.*`) needs one.
- **Re-run the whole workflow from the start on resume**: rejected — this is
  the direct cause of ADR-006's `known_node_outputs` resume design. Re-running
  from scratch after an approval would re-send any email already sent by an
  earlier action node.
- **Execute nodes concurrently where the DAG allows it** (parallel branches):
  deferred. The current node set has no I/O-bound node worth parallelizing
  (even `ai.classify`'s network call is bridged via `asyncio.run`, not
  truly concurrent — see ADR-004), and linear execution is far easier to
  reason about and test. Worth revisiting if the node set grows to include
  genuinely slow, independent branches.

## Consequences

- `logic.condition` is defined in the node registry but its branching
  semantics (named output handles, e.g. `true`/`false`) aren't implemented
  yet — the schema supports arbitrary `source_handle` strings, but the
  executor doesn't currently use them to prune unselected branches. This is a
  known gap, not an oversight: it's scoped for when a real use case needs it.
- Deterministic ordering made the entire test suite's exact-sequence
  assertions possible without timing-based flakiness.
