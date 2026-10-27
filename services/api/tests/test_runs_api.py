from fastapi.testclient import TestClient

VALID_DEFINITION = {
    "schema_version": "1.0",
    "name": "Triage",
    "nodes": [
        {
            "id": "trigger_1",
            "type": "trigger.manual",
            "position": {"x": 0, "y": 0},
            "config": {},
        },
        {
            "id": "email_1",
            "type": "action.mock_email",
            "position": {"x": 200, "y": 0},
            "config": {
                "to": "$.trigger.customer_email",
                "subject": "Re: enquiry",
                "body": "Thanks!",
            },
        },
    ],
    "edges": [{"id": "edge_1", "source": "trigger_1", "target": "email_1"}],
}

BLANK_DEFINITION = {"schema_version": "1.0", "name": "Blank", "nodes": [], "edges": []}


def _create_published_workflow(client: TestClient) -> tuple[str, str]:
    ws_response = client.post("/api/v1/workspaces", json={"name": "Acme"})
    workspace_id = ws_response.json()["id"]

    create_response = client.post(
        "/api/v1/workflows",
        json={
            "workspace_id": workspace_id,
            "name": "Triage",
            "definition": VALID_DEFINITION,
        },
    )
    workflow_id = create_response.json()["id"]

    publish_response = client.post(
        f"/api/v1/workflows/{workflow_id}/publish", params={"workspace_id": workspace_id}
    )
    assert publish_response.status_code == 200

    return workspace_id, workflow_id


def test_run_executes_and_succeeds(client: TestClient) -> None:
    workspace_id, workflow_id = _create_published_workflow(client)

    response = client.post(
        f"/api/v1/workflows/{workflow_id}/runs",
        params={"workspace_id": workspace_id},
        json={"input": {"customer_email": "a@example.test"}},
    )
    assert response.status_code == 202
    run_id = response.json()["id"]
    assert response.json()["status"] == "succeeded"

    get_response = client.get(f"/api/v1/runs/{run_id}", params={"workspace_id": workspace_id})
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "succeeded"

    nodes_response = client.get(
        f"/api/v1/runs/{run_id}/nodes", params={"workspace_id": workspace_id}
    )
    assert nodes_response.status_code == 200
    node_results = nodes_response.json()
    assert [n["node_id"] for n in node_results] == ["trigger_1", "email_1"]
    assert node_results[1]["output"]["to"] == "a@example.test"


def test_run_requires_published_workflow(client: TestClient) -> None:
    ws_response = client.post("/api/v1/workspaces", json={"name": "Acme"})
    workspace_id = ws_response.json()["id"]
    create_response = client.post(
        "/api/v1/workflows",
        json={
            "workspace_id": workspace_id,
            "name": "Triage",
            "definition": BLANK_DEFINITION,
        },
    )
    workflow_id = create_response.json()["id"]

    response = client.post(
        f"/api/v1/workflows/{workflow_id}/runs",
        params={"workspace_id": workspace_id},
        json={"input": {}},
    )
    assert response.status_code == 422


def test_run_wrong_workspace_returns_404(client: TestClient) -> None:
    workspace_id, workflow_id = _create_published_workflow(client)
    other_ws_response = client.post("/api/v1/workspaces", json={"name": "Other"})
    other_workspace_id = other_ws_response.json()["id"]

    response = client.post(
        f"/api/v1/workflows/{workflow_id}/runs",
        params={"workspace_id": other_workspace_id},
        json={"input": {}},
    )
    assert response.status_code == 404


def test_idempotency_key_returns_same_run(client: TestClient) -> None:
    workspace_id, workflow_id = _create_published_workflow(client)

    first = client.post(
        f"/api/v1/workflows/{workflow_id}/runs",
        params={"workspace_id": workspace_id},
        json={"input": {"customer_email": "a@example.test"}, "idempotency_key": "req-1"},
    )
    second = client.post(
        f"/api/v1/workflows/{workflow_id}/runs",
        params={"workspace_id": workspace_id},
        json={"input": {"customer_email": "different@example.test"}, "idempotency_key": "req-1"},
    )

    assert first.json()["id"] == second.json()["id"]
    assert second.json()["input"]["customer_email"] == "a@example.test"


def test_publishing_new_version_does_not_affect_running_run_version(client: TestClient) -> None:
    workspace_id, workflow_id = _create_published_workflow(client)

    run_response = client.post(
        f"/api/v1/workflows/{workflow_id}/runs",
        params={"workspace_id": workspace_id},
        json={"input": {"customer_email": "a@example.test"}},
    )
    assert run_response.json()["workflow_version"] == 1

    client.put(
        f"/api/v1/workflows/{workflow_id}",
        params={"workspace_id": workspace_id},
        json={"definition": VALID_DEFINITION},
    )
    client.post(f"/api/v1/workflows/{workflow_id}/publish", params={"workspace_id": workspace_id})

    get_response = client.get(
        f"/api/v1/runs/{run_response.json()['id']}", params={"workspace_id": workspace_id}
    )
    assert get_response.json()["workflow_version"] == 1
