from fastapi.testclient import TestClient


def test_get_workspace(client: TestClient) -> None:
    create_response = client.post("/api/v1/workspaces", json={"name": "Acme"})
    workspace_id = create_response.json()["id"]

    response = client.get(f"/api/v1/workspaces/{workspace_id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Acme"


def test_get_nonexistent_workspace_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/workspaces/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
