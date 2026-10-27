from fastapi.testclient import TestClient

from app.main import app
from app.providers.factory import get_provider

BLANK_DEFINITION = {"schema_version": "1.0", "name": "Blank", "nodes": [], "edges": []}

VALID_RAW = {
    "name": "Triage",
    "nodes": [
        {"id": "trigger_1", "type": "trigger.manual", "position": {"x": 0, "y": 0}, "config": {}},
        {
            "id": "email_1",
            "type": "action.mock_email",
            "position": {"x": 200, "y": 0},
            "config": {"to": "x", "subject": "x", "body": "x"},
        },
    ],
    "edges": [{"id": "edge_1", "source": "trigger_1", "target": "email_1"}],
}


class FixedProvider:
    async def generate(self, prompt, *, output_schema=None):
        return VALID_RAW


def test_generate_endpoint_returns_proposal_without_persisting(client: TestClient) -> None:
    app.dependency_overrides[get_provider] = lambda: FixedProvider()
    try:
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
            f"/api/v1/workflows/{workflow_id}/generate",
            params={"workspace_id": workspace_id},
            json={"prompt": "Triage customer enquiries"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["is_valid"] is True
        assert [n["id"] for n in body["definition"]["nodes"]] == ["trigger_1", "email_1"]

        # generation must not mutate the stored draft
        get_response = client.get(
            f"/api/v1/workflows/{workflow_id}", params={"workspace_id": workspace_id}
        )
        assert get_response.json()["draft_definition"]["nodes"] == []
    finally:
        app.dependency_overrides.pop(get_provider, None)


def test_generate_endpoint_requires_existing_workflow(client: TestClient) -> None:
    ws_response = client.post("/api/v1/workspaces", json={"name": "Acme"})
    workspace_id = ws_response.json()["id"]

    response = client.post(
        "/api/v1/workflows/00000000-0000-0000-0000-000000000000/generate",
        params={"workspace_id": workspace_id},
        json={"prompt": "Triage customer enquiries"},
    )
    assert response.status_code == 404
