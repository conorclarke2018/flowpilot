from app.engine.validation import validate_workflow
from app.schemas.workflow_definition import WorkflowDefinition, WorkflowEdge, WorkflowNode

POSITION = {"x": 0, "y": 0}


def _node(node_id: str, node_type: str) -> WorkflowNode:
    return WorkflowNode(id=node_id, type=node_type, position=POSITION, config={})


def test_valid_linear_workflow_passes() -> None:
    definition = WorkflowDefinition(
        name="Valid",
        nodes=[
            _node("trigger_1", "trigger.manual"),
            _node("classify_1", "ai.classify"),
        ],
        edges=[
            WorkflowEdge(id="edge_1", source="trigger_1", target="classify_1"),
        ],
    )

    result = validate_workflow(definition)

    assert result.is_valid


def test_missing_trigger_fails() -> None:
    definition = WorkflowDefinition(
        name="No trigger",
        nodes=[_node("classify_1", "ai.classify")],
        edges=[],
    )

    result = validate_workflow(definition)

    assert not result.is_valid
    assert any(error.code == "invalid_trigger_count" for error in result.errors)


def test_multiple_triggers_fails() -> None:
    definition = WorkflowDefinition(
        name="Two triggers",
        nodes=[
            _node("trigger_1", "trigger.manual"),
            _node("trigger_2", "trigger.webhook"),
        ],
        edges=[],
    )

    result = validate_workflow(definition)

    assert not result.is_valid
    assert any(error.code == "invalid_trigger_count" for error in result.errors)


def test_duplicate_node_ids_fails() -> None:
    definition = WorkflowDefinition(
        name="Duplicate ids",
        nodes=[
            _node("trigger_1", "trigger.manual"),
            _node("trigger_1", "ai.classify"),
        ],
        edges=[],
    )

    result = validate_workflow(definition)

    assert not result.is_valid
    assert any(error.code == "duplicate_node_id" for error in result.errors)


def test_edge_referencing_unknown_node_fails() -> None:
    definition = WorkflowDefinition(
        name="Dangling edge",
        nodes=[_node("trigger_1", "trigger.manual")],
        edges=[WorkflowEdge(id="edge_1", source="trigger_1", target="missing")],
    )

    result = validate_workflow(definition)

    assert not result.is_valid
    assert any(error.code == "invalid_edge_reference" for error in result.errors)


def test_unsupported_node_type_fails() -> None:
    definition = WorkflowDefinition(
        name="Bad node type",
        nodes=[_node("trigger_1", "trigger.manual"), _node("evil_1", "exec.shell")],
        edges=[],
    )

    result = validate_workflow(definition)

    assert not result.is_valid
    assert any(error.code == "unsupported_node_type" for error in result.errors)


def test_cycle_detected() -> None:
    definition = WorkflowDefinition(
        name="Cycle",
        nodes=[
            _node("trigger_1", "trigger.manual"),
            _node("condition_1", "logic.condition"),
            _node("classify_1", "ai.classify"),
        ],
        edges=[
            WorkflowEdge(id="edge_1", source="trigger_1", target="condition_1"),
            WorkflowEdge(id="edge_2", source="condition_1", target="classify_1"),
            WorkflowEdge(id="edge_3", source="classify_1", target="condition_1"),
        ],
    )

    result = validate_workflow(definition)

    assert not result.is_valid
    assert any(error.code == "cycle_detected" for error in result.errors)
