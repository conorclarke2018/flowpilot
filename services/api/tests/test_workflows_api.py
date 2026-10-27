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


def test_update_draft_can_rename_workflow(client: TestClient) -> None:
    workspace_id = _create_workspace(client)
    create_response = client.post(
        "/api/v1/workflows",
        json={"workspace_id": workspace_id, "name": "Triage", "definition": BLANK_DEFINITION},
    )
    workflow_id = create_response.json()["id"]

    rename_response = client.put(
        f"/api/v1/workflows/{workflow_id}",
        params={"workspace_id": workspace_id},
        json={"definition": BLANK_DEFINITION, "name": "Customer Enquiry Triage"},
    )
    assert rename_response.status_code == 200
    assert rename_response.json()["name"] == "Customer Enquiry Triage"

    get_response = client.get(
        f"/api/v1/workflows/{workflow_id}", params={"workspace_id": workspace_id}
    )
    assert get_response.json()["name"] == "Customer Enquiry Triage"


def test_update_draft_without_name_keeps_existing_name(client: TestClient) -> None:
    workspace_id = _create_workspace(client)
    create_response = client.post(
        "/api/v1/workflows",
        json={"workspace_id": workspace_id, "name": "Triage", "definition": BLANK_DEFINITION},
    )
    workflow_id = create_response.json()["id"]

    update_response = client.put(
        f"/api/v1/workflows/{workflow_id}",
        params={"workspace_id": workspace_id},
        json={"definition": BLANK_DEFINITION},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Triage"


def test_delete_workflow(client: TestClient) -> None:
    workspace_id = _create_workspace(client)
    create_response = client.post(
        "/api/v1/workflows",
        json={"workspace_id": workspace_id, "name": "Triage", "definition": BLANK_DEFINITION},
    )
    workflow_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/workflows/{workflow_id}", params={"workspace_id": workspace_id}
    )
    assert delete_response.status_code == 204

    get_response = client.get(
        f"/api/v1/workflows/{workflow_id}", params={"workspace_id": workspace_id}
    )
    assert get_response.status_code == 404


def test_delete_nonexistent_workflow_returns_404(client: TestClient) -> None:
    workspace_id = _create_workspace(client)

    response = client.delete(
        "/api/v1/workflows/00000000-0000-0000-0000-000000000000",
        params={"workspace_id": workspace_id},
    )
    assert response.status_code == 404


def test_delete_workflow_wrong_workspace_returns_404(client: TestClient) -> None:
    workspace_id = _create_workspace(client)
    other_workspace_id = _create_workspace(client)
    create_response = client.post(
        "/api/v1/workflows",
        json={"workspace_id": workspace_id, "name": "Triage", "definition": BLANK_DEFINITION},
    )
    workflow_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/workflows/{workflow_id}", params={"workspace_id": other_workspace_id}
    )
    assert response.status_code == 404

    # the workflow must still exist for its real workspace
    get_response = client.get(
        f"/api/v1/workflows/{workflow_id}", params={"workspace_id": workspace_id}
    )
    assert get_response.status_code == 200


def test_delete_workflow_cascades_published_versions_runs_and_approvals(
    client: TestClient,
) -> None:
    # A workflow with a published version, a completed run (node_runs), and a
    # pending approval exercises the full FK chain: workflows -> workflow_versions,
    # workflows -> workflow_runs -> node_runs, workflow_runs -> approvals.
    # If ondelete=CASCADE weren't wired correctly on every link, this delete
    # would raise a foreign-key violation instead of succeeding.
    workspace_id = _create_workspace(client)
    approval_definition = {
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
                "config": {"payload": {}},
            },
        ],
        "edges": [{"id": "edge_1", "source": "trigger_1", "target": "approval_1"}],
    }
    create_response = client.post(
        "/api/v1/workflows",
        json={
            "workspace_id": workspace_id,
            "name": "Triage",
            "definition": approval_definition,
        },
    )
    workflow_id = create_response.json()["id"]
    client.post(f"/api/v1/workflows/{workflow_id}/publish", params={"workspace_id": workspace_id})
    client.post(
        f"/api/v1/workflows/{workflow_id}/runs",
        params={"workspace_id": workspace_id},
        json={"input": {}},
    )

    delete_response = client.delete(
        f"/api/v1/workflows/{workflow_id}", params={"workspace_id": workspace_id}
    )
    assert delete_response.status_code == 204

    assert (
        client.get(
            f"/api/v1/workflows/{workflow_id}", params={"workspace_id": workspace_id}
        ).status_code
        == 404
    )
    assert client.get("/api/v1/approvals", params={"workspace_id": workspace_id}).json() == []


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
