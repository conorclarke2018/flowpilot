from fastapi.testclient import TestClient

BLANK_DEFINITION = {"schema_version": "1.0", "name": "Blank", "nodes": [], "edges": []}

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
            "id": "classify_1",
            "type": "ai.classify",
            "position": {"x": 200, "y": 0},
            "config": {},
        },
    ],
    "edges": [{"id": "edge_1", "source": "trigger_1", "target": "classify_1"}],
}


def _create_workspace(client: TestClient) -> str:
    response = client.post("/api/v1/workspaces", json={"name": "Acme"})
    assert response.status_code == 201
    return response.json()["id"]


def test_create_workflow_with_nonexistent_workspace_returns_404(client: TestClient) -> None:
    response = client.post(
        "/api/v1/workflows",
        json={
            "workspace_id": "00000000-0000-0000-0000-000000000000",
            "name": "Triage",
            "definition": BLANK_DEFINITION,
        },
    )
    assert response.status_code == 404


def test_create_and_get_workflow(client: TestClient) -> None:
    workspace_id = _create_workspace(client)

    create_response = client.post(
        "/api/v1/workflows",
        json={
            "workspace_id": workspace_id,
            "name": "Triage",
            "definition": BLANK_DEFINITION,
        },
    )
    assert create_response.status_code == 201
    workflow_id = create_response.json()["id"]
    assert create_response.json()["draft_revision"] == 1
    assert create_response.json()["published_version"] is None

    get_response = client.get(
        f"/api/v1/workflows/{workflow_id}", params={"workspace_id": workspace_id}
    )
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Triage"


def test_get_workflow_wrong_workspace_returns_404(client: TestClient) -> None:
    workspace_id = _create_workspace(client)
    other_workspace_id = _create_workspace(client)

    create_response = client.post(
        "/api/v1/workflows",
        json={"workspace_id": workspace_id, "name": "Triage", "definition": BLANK_DEFINITION},
    )
    workflow_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/workflows/{workflow_id}", params={"workspace_id": other_workspace_id}
    )
    assert response.status_code == 404


def test_update_draft_increments_revision(client: TestClient) -> None:
    workspace_id = _create_workspace(client)
    create_response = client.post(
        "/api/v1/workflows",
        json={"workspace_id": workspace_id, "name": "Triage", "definition": BLANK_DEFINITION},
    )
    workflow_id = create_response.json()["id"]

    update_response = client.put(
        f"/api/v1/workflows/{workflow_id}",
        params={"workspace_id": workspace_id},
        json={"definition": VALID_DEFINITION},
    )
    assert update_response.status_code == 200
    assert update_response.json()["draft_revision"] == 2
    assert update_response.json()["draft_definition"]["nodes"][0]["id"] == "trigger_1"


def test_validate_invalid_draft_reports_errors(client: TestClient) -> None:
    workspace_id = _create_workspace(client)
    create_response = client.post(
        "/api/v1/workflows",
        json={"workspace_id": workspace_id, "name": "Triage", "definition": BLANK_DEFINITION},
    )
    workflow_id = create_response.json()["id"]

    response = client.post(
        f"/api/v1/workflows/{workflow_id}/validate", params={"workspace_id": workspace_id}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["is_valid"] is False
    assert any(e["code"] == "invalid_trigger_count" for e in body["errors"])


def test_publish_invalid_draft_returns_422(client: TestClient) -> None:
    workspace_id = _create_workspace(client)
    create_response = client.post(
        "/api/v1/workflows",
        json={"workspace_id": workspace_id, "name": "Triage", "definition": BLANK_DEFINITION},
    )
    workflow_id = create_response.json()["id"]

    response = client.post(
        f"/api/v1/workflows/{workflow_id}/publish", params={"workspace_id": workspace_id}
    )
    assert response.status_code == 422


def test_publish_valid_draft_creates_immutable_version(client: TestClient) -> None:
    workspace_id = _create_workspace(client)
    create_response = client.post(
        "/api/v1/workflows",
        json={"workspace_id": workspace_id, "name": "Triage", "definition": VALID_DEFINITION},
    )
    workflow_id = create_response.json()["id"]

    publish_response = client.post(
        f"/api/v1/workflows/{workflow_id}/publish", params={"workspace_id": workspace_id}
    )
    assert publish_response.status_code == 200
    assert publish_response.json()["version"] == 1

    get_response = client.get(
        f"/api/v1/workflows/{workflow_id}", params={"workspace_id": workspace_id}
    )
    assert get_response.json()["published_version"] == 1

    # editing the draft afterwards must not change the already-published version
    update_response = client.put(
        f"/api/v1/workflows/{workflow_id}",
        params={"workspace_id": workspace_id},
        json={"definition": BLANK_DEFINITION},
    )
    assert update_response.status_code == 200
    assert update_response.json()["published_version"] == 1
