from fastapi.testclient import TestClient

APPROVAL_DEFINITION = {
    "schema_version": "1.0",
    "name": "Triage with approval",
    "nodes": [
        {
            "id": "trigger_1",
            "type": "trigger.manual",
            "position": {"x": 0, "y": 0},
            "config": {},
        },
        {
            "id": "approval_1",
            "type": "human.approval",
            "position": {"x": 200, "y": 0},
            "config": {"payload": {"draft": "$.trigger.message"}},
        },
        {
            "id": "email_1",
            "type": "action.mock_email",
            "position": {"x": 400, "y": 0},
            "config": {"to": "x", "subject": "x", "body": "$.approval_1.draft"},
        },
    ],
    "edges": [
        {"id": "edge_1", "source": "trigger_1", "target": "approval_1"},
        {"id": "edge_2", "source": "approval_1", "target": "email_1"},
    ],
}


def _create_published_workflow(client: TestClient) -> tuple[str, str]:
    ws_response = client.post("/api/v1/workspaces", json={"name": "Acme"})
    workspace_id = ws_response.json()["id"]
    create_response = client.post(
        "/api/v1/workflows",
        json={
            "workspace_id": workspace_id,
            "name": "Triage",
            "definition": APPROVAL_DEFINITION,
        },
    )
    workflow_id = create_response.json()["id"]
    publish_response = client.post(
        f"/api/v1/workflows/{workflow_id}/publish", params={"workspace_id": workspace_id}
    )
    assert publish_response.status_code == 200
    return workspace_id, workflow_id


def test_run_pauses_for_approval(client: TestClient) -> None:
    workspace_id, workflow_id = _create_published_workflow(client)

    run_response = client.post(
        f"/api/v1/workflows/{workflow_id}/runs",
        params={"workspace_id": workspace_id},
        json={"input": {"message": "Order delayed"}},
    )
    assert run_response.status_code == 202
    assert run_response.json()["status"] == "waiting_for_approval"

    pending = client.get("/api/v1/approvals", params={"workspace_id": workspace_id})
    assert pending.status_code == 200
    assert len(pending.json()) == 1
    approval = pending.json()[0]
    assert approval["node_id"] == "approval_1"
    assert approval["proposed_payload"] == {"draft": "Order delayed"}
    assert approval["status"] == "pending"


def test_approving_with_edited_payload_resumes_and_propagates(client: TestClient) -> None:
    workspace_id, workflow_id = _create_published_workflow(client)

    run_response = client.post(
        f"/api/v1/workflows/{workflow_id}/runs",
        params={"workspace_id": workspace_id},
        json={"input": {"message": "Order delayed"}},
    )
    run_id = run_response.json()["id"]
    approval_id = client.get("/api/v1/approvals", params={"workspace_id": workspace_id}).json()[
        0
    ]["id"]

    decision_response = client.post(
        f"/api/v1/approvals/{approval_id}/decision",
        params={"workspace_id": workspace_id},
        json={"decision": "approved", "payload": {"draft": "edited by reviewer"}},
    )
    assert decision_response.status_code == 200
    assert decision_response.json()["status"] == "approved"

    run_after = client.get(f"/api/v1/runs/{run_id}", params={"workspace_id": workspace_id})
    assert run_after.json()["status"] == "succeeded"

    node_runs = client.get(
        f"/api/v1/runs/{run_id}/nodes", params={"workspace_id": workspace_id}
    ).json()
    node_ids = [n["node_id"] for n in node_runs]
    assert node_ids == ["trigger_1", "email_1"]  # approval node isn't a NodeRun, only a decision
    email_result = next(n for n in node_runs if n["node_id"] == "email_1")
    assert email_result["output"]["body"] == "edited by reviewer"


def test_approving_without_edits_uses_proposed_payload(client: TestClient) -> None:
    workspace_id, workflow_id = _create_published_workflow(client)

    run_response = client.post(
        f"/api/v1/workflows/{workflow_id}/runs",
        params={"workspace_id": workspace_id},
        json={"input": {"message": "Original message"}},
    )
    run_id = run_response.json()["id"]
    approval_id = client.get("/api/v1/approvals", params={"workspace_id": workspace_id}).json()[
        0
    ]["id"]

    client.post(
        f"/api/v1/approvals/{approval_id}/decision",
        params={"workspace_id": workspace_id},
        json={"decision": "approved"},
    )

    node_runs = client.get(
        f"/api/v1/runs/{run_id}/nodes", params={"workspace_id": workspace_id}
    ).json()
    email_result = next(n for n in node_runs if n["node_id"] == "email_1")
    assert email_result["output"]["body"] == "Original message"


def test_rejecting_cancels_the_run_without_executing_downstream(client: TestClient) -> None:
    workspace_id, workflow_id = _create_published_workflow(client)

    run_response = client.post(
        f"/api/v1/workflows/{workflow_id}/runs",
        params={"workspace_id": workspace_id},
        json={"input": {"message": "Order delayed"}},
    )
    run_id = run_response.json()["id"]
    approval_id = client.get("/api/v1/approvals", params={"workspace_id": workspace_id}).json()[
        0
    ]["id"]

    decision_response = client.post(
        f"/api/v1/approvals/{approval_id}/decision",
        params={"workspace_id": workspace_id},
        json={"decision": "rejected"},
    )
    assert decision_response.status_code == 200
    assert decision_response.json()["status"] == "rejected"

    run_after = client.get(f"/api/v1/runs/{run_id}", params={"workspace_id": workspace_id})
    assert run_after.json()["status"] == "cancelled"

    node_runs = client.get(
        f"/api/v1/runs/{run_id}/nodes", params={"workspace_id": workspace_id}
    ).json()
    assert [n["node_id"] for n in node_runs] == ["trigger_1"]  # email_1 never ran

    pending = client.get("/api/v1/approvals", params={"workspace_id": workspace_id})
    assert pending.json() == []


def test_deciding_an_already_decided_approval_returns_409(client: TestClient) -> None:
    workspace_id, workflow_id = _create_published_workflow(client)

    client.post(
        f"/api/v1/workflows/{workflow_id}/runs",
        params={"workspace_id": workspace_id},
        json={"input": {"message": "x"}},
    )
    approval_id = client.get("/api/v1/approvals", params={"workspace_id": workspace_id}).json()[
        0
    ]["id"]

    client.post(
        f"/api/v1/approvals/{approval_id}/decision",
        params={"workspace_id": workspace_id},
        json={"decision": "approved"},
    )
    second_decision = client.post(
        f"/api/v1/approvals/{approval_id}/decision",
        params={"workspace_id": workspace_id},
        json={"decision": "rejected"},
    )
    assert second_decision.status_code == 409


def test_approvals_are_workspace_isolated(client: TestClient) -> None:
    workspace_id, workflow_id = _create_published_workflow(client)
    other_ws_response = client.post("/api/v1/workspaces", json={"name": "Other"})
    other_workspace_id = other_ws_response.json()["id"]

    client.post(
        f"/api/v1/workflows/{workflow_id}/runs",
        params={"workspace_id": workspace_id},
        json={"input": {"message": "x"}},
    )
    approval_id = client.get("/api/v1/approvals", params={"workspace_id": workspace_id}).json()[
        0
    ]["id"]

    # the other workspace shouldn't see it in its pending list
    other_pending = client.get("/api/v1/approvals", params={"workspace_id": other_workspace_id})
    assert other_pending.json() == []

    # nor be able to decide it directly
    cross_tenant_decision = client.post(
        f"/api/v1/approvals/{approval_id}/decision",
        params={"workspace_id": other_workspace_id},
        json={"decision": "approved"},
    )
    assert cross_tenant_decision.status_code == 404
