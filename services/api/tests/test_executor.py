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


def test_pauses_at_human_approval_node() -> None:
    definition = WorkflowDefinition(
        name="Approval gate",
        nodes=[
            _node("trigger_1", "trigger.manual"),
            _node(
                "approval_1",
                "human.approval",
                {"payload": {"draft": "$.trigger.message"}},
            ),
            _node(
                "email_1",
                "action.mock_email",
                {"to": "x", "subject": "x", "body": "$.approval_1.draft"},
            ),
        ],
        edges=[
            WorkflowEdge(id="edge_1", source="trigger_1", target="approval_1"),
            WorkflowEdge(id="edge_2", source="approval_1", target="email_1"),
        ],
    )

    result = execute_workflow(definition, {"message": "Thanks for your patience"})

    assert result.status == "waiting_for_approval"
    assert result.pending_approval_node_id == "approval_1"
    assert result.pending_approval_payload == {"draft": "Thanks for your patience"}
    # the approval node itself is paused on, so only the trigger has run so far
    assert [r.node_id for r in result.node_results] == ["trigger_1"]


def test_resumes_after_approval_with_decided_payload() -> None:
    definition = WorkflowDefinition(
        name="Approval gate",
        nodes=[
            _node("trigger_1", "trigger.manual"),
            _node("approval_1", "human.approval", {"payload": {"draft": "original"}}),
            _node(
                "email_1",
                "action.mock_email",
                {"to": "x", "subject": "x", "body": "$.approval_1.draft"},
            ),
        ],
        edges=[
            WorkflowEdge(id="edge_1", source="trigger_1", target="approval_1"),
            WorkflowEdge(id="edge_2", source="approval_1", target="email_1"),
        ],
    )

    # simulate: trigger already ran, approval was decided with an edited payload
    known_outputs = {
        "trigger_1": {"message": "hi"},
        "approval_1": {"draft": "edited by reviewer"},
    }

    result = execute_workflow(definition, {"message": "hi"}, known_node_outputs=known_outputs)

    assert result.status == "succeeded"
    # only the newly-executed node (email_1) is reported; earlier nodes aren't re-run
    assert [r.node_id for r in result.node_results] == ["email_1"]
    assert result.node_results[0].output["body"] == "edited by reviewer"


def test_node_retries_until_success() -> None:
    attempts = {"count": 0}

    def flaky_handler(config, context):
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise RuntimeError("transient failure")
        return {"ok": True}

    from app.nodes import handlers as handlers_module

    handlers_module.HANDLERS["test.flaky"] = flaky_handler
    try:
        definition = WorkflowDefinition(
            name="Retry",
            nodes=[_node("flaky_1", "test.flaky", {"max_retries": 2})],
            edges=[],
        )

        result = execute_workflow(definition, {})

        assert result.status == "succeeded"
        assert attempts["count"] == 3
        assert result.node_results[0].output == {"ok": True}
    finally:
        del handlers_module.HANDLERS["test.flaky"]


def test_node_timeout_fails_the_node() -> None:
    def slow_handler(config, context):
        import time as time_module

        time_module.sleep(1)
        return {"ok": True}

    from app.nodes import handlers as handlers_module

    handlers_module.HANDLERS["test.slow"] = slow_handler
    try:
        definition = WorkflowDefinition(
            name="Timeout",
            nodes=[_node("slow_1", "test.slow", {"timeout_seconds": 0.05})],
            edges=[],
        )

        result = execute_workflow(definition, {})

        assert result.status == "failed"
        assert "timed out" in result.node_results[0].error
    finally:
        del handlers_module.HANDLERS["test.slow"]
