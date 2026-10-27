import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from app.engine.context import ExecutionContext
from app.nodes.handlers import HANDLERS
from app.schemas.workflow_definition import WorkflowDefinition

APPROVAL_NODE_TYPE = "human.approval"


@dataclass
class NodeExecutionResult:
    node_id: str
    status: str  # "succeeded" | "failed"
    output: dict[str, Any] | None
    error: str | None
    started_at: datetime
    finished_at: datetime


@dataclass
class ExecutionResult:
    status: str  # "succeeded" | "failed" | "waiting_for_approval"
    node_results: list[NodeExecutionResult] = field(default_factory=list)
    pending_approval_node_id: str | None = None
    pending_approval_payload: dict[str, Any] | None = None


def execute_workflow(
    definition: WorkflowDefinition,
    trigger_input: dict[str, Any],
    *,
    known_node_outputs: dict[str, dict[str, Any]] | None = None,
) -> ExecutionResult:
    """Execute an already-validated DAG in dependency order.

    `known_node_outputs` seeds the context with results from a prior pass
    (either earlier nodes already persisted, or a human.approval node's
    decided payload) so resuming after an approval doesn't re-run nodes that
    may already have had external side effects.

    Stops at the first failing node, and pauses (without erroring) the first
    time it reaches an undecided human.approval node.
    """
    known_node_outputs = known_node_outputs or {}
    order = _topological_order(definition)
    context = ExecutionContext(trigger_input)
    for node_id, output in known_node_outputs.items():
        context.set_output(node_id, output)

    node_results: list[NodeExecutionResult] = []
    nodes_by_id = {node.id: node for node in definition.nodes}

    for node_id in order:
        if node_id in known_node_outputs:
            continue

        node = nodes_by_id[node_id]

        if node.type == APPROVAL_NODE_TYPE:
            payload = context.resolve(node.config.get("payload", {}))
            return ExecutionResult(
                status="waiting_for_approval",
                node_results=node_results,
                pending_approval_node_id=node_id,
                pending_approval_payload=payload,
            )

        handler = HANDLERS.get(node.type)
        started_at = datetime.now(UTC)

        if handler is None:
            node_results.append(
                NodeExecutionResult(
                    node_id=node_id,
                    status="failed",
                    output=None,
                    error=f"No handler registered for node type: {node.type}",
                    started_at=started_at,
                    finished_at=datetime.now(UTC),
                )
            )
            return ExecutionResult(status="failed", node_results=node_results)

        try:
            output = _run_with_retries_and_timeout(handler, node.config, context)
        except Exception as exc:  # noqa: BLE001 - node failures are captured, not raised
            node_results.append(
                NodeExecutionResult(
                    node_id=node_id,
                    status="failed",
                    output=None,
                    error=str(exc),
                    started_at=started_at,
                    finished_at=datetime.now(UTC),
                )
            )
            return ExecutionResult(status="failed", node_results=node_results)

        context.set_output(node_id, output)
        node_results.append(
            NodeExecutionResult(
                node_id=node_id,
                status="succeeded",
                output=output,
                error=None,
                started_at=started_at,
                finished_at=datetime.now(UTC),
            )
        )

    return ExecutionResult(status="succeeded", node_results=node_results)


def _run_with_retries_and_timeout(
    handler: Any, config: dict[str, Any], context: ExecutionContext
) -> dict[str, Any]:
    max_attempts = max(1, int(config.get("max_retries", 0)) + 1)
    backoff_seconds = float(config.get("retry_backoff_seconds", 0))
    timeout_seconds = config.get("timeout_seconds")

    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            if timeout_seconds is None:
                return handler(config, context)
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(handler, config, context)
                try:
                    return future.result(timeout=float(timeout_seconds))
                except FutureTimeoutError as exc:
                    raise TimeoutError(
                        f"Node timed out after {timeout_seconds}s"
                    ) from exc
        except Exception as exc:  # noqa: BLE001 - retried, then re-raised below
            last_error = exc
            if attempt < max_attempts:
                time.sleep(backoff_seconds)

    assert last_error is not None
    raise last_error


def _topological_order(definition: WorkflowDefinition) -> list[str]:
    node_ids = [node.id for node in definition.nodes]
    adjacency: dict[str, list[str]] = {node_id: [] for node_id in node_ids}
    in_degree: dict[str, int] = dict.fromkeys(node_ids, 0)

    for edge in definition.edges:
        adjacency[edge.source].append(edge.target)
        in_degree[edge.target] += 1

    queue = deque(sorted(node_id for node_id, degree in in_degree.items() if degree == 0))
    order: list[str] = []

    while queue:
        node_id = queue.popleft()
        order.append(node_id)
        for neighbour in sorted(adjacency[node_id]):
            in_degree[neighbour] -= 1
            if in_degree[neighbour] == 0:
                queue.append(neighbour)

    return order
