from app.engine.executor import execute_workflow
from app.schemas.workflow import WorkflowDefinition, WorkflowEdge, WorkflowNode

POSITION = {"x": 0, "y": 0}


def _node(node_id: str, node_type: str, config: dict | None = None) -> WorkflowNode:
    return WorkflowNode(id=node_id, type=node_type, position=POSITION, config=config or {})


def test_executes_linear_workflow_in_order() -> None:
    definition = WorkflowDefinition(
        name="Linear",
        nodes=[
            _node("trigger_1", "trigger.manual"),
            _node(
                "transform_1",
                "data.transform",
                {"mapping": {"email": "$.trigger_1.customer_email"}},
            ),
        ],
        edges=[WorkflowEdge(id="edge_1", source="trigger_1", target="transform_1")],
    )

    result = execute_workflow(definition, {"customer_email": "a@example.test"})

    assert result.status == "succeeded"
    assert [r.node_id for r in result.node_results] == ["trigger_1", "transform_1"]
    assert result.node_results[1].output == {"email": "a@example.test"}


def test_data_transform_can_reference_trigger_directly() -> None:
    definition = WorkflowDefinition(
        name="Trigger ref",
        nodes=[
            _node("trigger_1", "trigger.manual"),
            _node("transform_1", "data.transform", {"mapping": {"subject": "$.trigger.subject"}}),
        ],
        edges=[WorkflowEdge(id="edge_1", source="trigger_1", target="transform_1")],
    )

    result = execute_workflow(definition, {"subject": "Order delayed"})

    assert result.node_results[1].output == {"subject": "Order delayed"}


def test_mock_email_action_resolves_upstream_output() -> None:
    definition = WorkflowDefinition(
        name="Email",
        nodes=[
            _node("trigger_1", "trigger.manual"),
            _node(
                "transform_1",
                "data.transform",
                {"mapping": {"reply_to": "$.trigger.customer_email"}},
            ),
            _node(
                "email_1",
                "action.mock_email",
                {
                    "to": "$.transform_1.reply_to",
                    "subject": "Re: your enquiry",
                    "body": "Thanks for reaching out.",
                },
            ),
        ],
        edges=[
            WorkflowEdge(id="edge_1", source="trigger_1", target="transform_1"),
            WorkflowEdge(id="edge_2", source="transform_1", target="email_1"),
        ],
    )

    result = execute_workflow(definition, {"customer_email": "customer@example.test"})

    assert result.status == "succeeded"
    email_result = result.node_results[-1]
    assert email_result.output == {
        "sent": True,
        "to": "customer@example.test",
        "subject": "Re: your enquiry",
        "body": "Thanks for reaching out.",
    }


def test_stops_at_first_failing_node() -> None:
    definition = WorkflowDefinition(
        name="Unsupported mid-graph",
        nodes=[
            _node("trigger_1", "trigger.manual"),
            _node("unsupported_1", "exec.shell"),
            _node("email_1", "action.mock_email", {"to": "x", "subject": "x", "body": "x"}),
        ],
        edges=[
            WorkflowEdge(id="edge_1", source="trigger_1", target="unsupported_1"),
            WorkflowEdge(id="edge_2", source="unsupported_1", target="email_1"),
        ],
    )

    result = execute_workflow(definition, {})

    assert result.status == "failed"
    assert [r.node_id for r in result.node_results] == ["trigger_1", "unsupported_1"]
    assert result.node_results[-1].error is not None
