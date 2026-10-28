from fastapi.testclient import TestClient

from ai_factory.api import create_app


def test_service_health_contract() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "ai-software-factory"}


def test_release_action_is_not_exposed() -> None:
    with TestClient(create_app()) as client:
        response = client.post("/deploy", json={"environment": "production"})
    assert response.status_code == 404
