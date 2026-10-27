from dataclasses import dataclass

from app.engine.registry import NODE_TYPES, TRIGGER_NODE_TYPES
from app.schemas.workflow_definition import WorkflowDefinition


@dataclass(frozen=True)
class ValidationError:
    code: str
    message: str


class WorkflowValidationResult:
    def __init__(self, errors: list[ValidationError]) -> None:
        self.errors = errors

    @property
    def is_valid(self) -> bool:
        return not self.errors


def validate_workflow(definition: WorkflowDefinition) -> WorkflowValidationResult:
    errors: list[ValidationError] = []

    node_ids = [node.id for node in definition.nodes]
    _check_unique_ids(node_ids, "duplicate_node_id", "node", errors)

    edge_ids = [edge.id for edge in definition.edges]
    _check_unique_ids(edge_ids, "duplicate_edge_id", "edge", errors)

    node_id_set = set(node_ids)
    for node in definition.nodes:
        if node.type not in NODE_TYPES:
            errors.append(
                ValidationError("unsupported_node_type", f"Unsupported node type: {node.type}")
            )

    for edge in definition.edges:
        if edge.source not in node_id_set:
            errors.append(
                ValidationError(
                    "invalid_edge_reference", f"Edge {edge.id} references unknown source node"
                )
            )
        if edge.target not in node_id_set:
            errors.append(
                ValidationError(
                    "invalid_edge_reference", f"Edge {edge.id} references unknown target node"
                )
            )

    trigger_count = sum(1 for node in definition.nodes if node.type in TRIGGER_NODE_TYPES)
    if trigger_count != 1:
        errors.append(
            ValidationError(
                "invalid_trigger_count",
                f"Workflow must have exactly one trigger node, found {trigger_count}",
            )
        )

    if not errors:
        cycle_error = _detect_cycle(node_ids, definition)
        if cycle_error:
            errors.append(cycle_error)

    return WorkflowValidationResult(errors)


def _check_unique_ids(
    ids: list[str], code: str, label: str, errors: list[ValidationError]
) -> None:
    seen: set[str] = set()
    for item_id in ids:
        if item_id in seen:
            errors.append(ValidationError(code, f"Duplicate {label} id: {item_id}"))
        seen.add(item_id)


def _detect_cycle(
    node_ids: list[str], definition: WorkflowDefinition
) -> ValidationError | None:
    adjacency: dict[str, list[str]] = {node_id: [] for node_id in node_ids}
    for edge in definition.edges:
        adjacency.setdefault(edge.source, []).append(edge.target)

    WHITE, GRAY, BLACK = 0, 1, 2
    color = dict.fromkeys(node_ids, WHITE)

    def visit(node_id: str) -> bool:
        color[node_id] = GRAY
        for neighbour in adjacency.get(node_id, []):
            if color.get(neighbour) == GRAY:
                return True
            if color.get(neighbour, WHITE) == WHITE and visit(neighbour):
                return True
        color[node_id] = BLACK
        return False

    for node_id in node_ids:
        if color[node_id] == WHITE and visit(node_id):
            return ValidationError("cycle_detected", "Workflow graph contains a cycle")
    return None
