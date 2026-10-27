from collections import deque
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from app.engine.context import ExecutionContext
from app.nodes.handlers import HANDLERS
from app.schemas.workflow import WorkflowDefinition


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
    status: str  # "succeeded" | "failed"
    node_results: list[NodeExecutionResult]


def execute_workflow(
    definition: WorkflowDefinition, trigger_input: dict[str, Any]
) -> ExecutionResult:
    """Execute an already-validated DAG in dependency order.

    Stops at the first failing node: later nodes are not executed, since an
    earlier external side effect may already have happened and should not be
    masked by an unrelated downstream error.
    """
    order = _topological_order(definition)
    context = ExecutionContext(trigger_input)
    node_results: list[NodeExecutionResult] = []
    overall_status = "succeeded"

    nodes_by_id = {node.id: node for node in definition.nodes}

    for node_id in order:
        node = nodes_by_id[node_id]
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
            overall_status = "failed"
            break

        try:
            output = handler(node.config, context)
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
            overall_status = "failed"
            break

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

    return ExecutionResult(status=overall_status, node_results=node_results)


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
