import sqlite3
from collections.abc import Iterator
from contextlib import closing
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from dayboard.main import create_app


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    with TestClient(create_app(tmp_path / "tasks.db")) as connection:
        yield connection


def test_webpage_assets_and_health(client: TestClient) -> None:
    page = client.get("/")
    assert page.status_code == 200
    assert "Make room for progress." in page.text
    assert "default-src 'self'" in page.headers["content-security-policy"]
    assert page.headers["x-content-type-options"] == "nosniff"
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/style.css").status_code == 200
    assert client.get("/healthz").json() == {"status": "ok", "service": "dayboard"}


def test_task_lifecycle_and_restart(tmp_path: Path) -> None:
    path = tmp_path / "tasks.db"
    with TestClient(create_app(path)) as client:
        assert client.get("/api/tasks").json() == []
        created = client.post(
            "/api/tasks", json={"title": "  Ship the website  ", "priority": "high"}
        )
        assert created.status_code == 201
        task = created.json()
        assert task["title"] == "Ship the website"
        assert task["completed"] is False
        assert task["notes"] == ""
        updated = client.patch(f"/api/tasks/{task['id']}", json={"completed": True})
        assert updated.status_code == 200
        assert updated.json()["completed"] is True
    with TestClient(create_app(path)) as restarted:
        tasks = restarted.get("/api/tasks")
        assert tasks.headers["cache-control"] == "no-store"
        assert tasks.json()[0]["completed"] is True
        assert tasks.json()[0]["id"] == task["id"]
        assert restarted.delete(f"/api/tasks/{task['id']}").status_code == 204
        assert restarted.get("/api/tasks").json() == []


@pytest.mark.parametrize(
    "body",
    [
        {"title": " "},
        {"title": "x" * 121},
        {"title": "ok", "notes": "x" * 1001},
        {"title": "ok", "priority": "urgent"},
        {"title": "ok", "completed": True},
        {},
    ],
)
def test_invalid_creation_cannot_write(client: TestClient, body: dict) -> None:
    assert client.post("/api/tasks", json=body).status_code == 422
    assert client.get("/api/tasks").json() == []


def test_invalid_updates_and_unknown_ids(client: TestClient) -> None:
    task = client.post("/api/tasks", json={"title": "Existing"}).json()
    assert client.patch(f"/api/tasks/{task['id']}", json={"completed": "yes"}).status_code == 422
    assert client.get("/api/tasks").json()[0]["completed"] is False
    assert client.patch(f"/api/tasks/{uuid4()}", json={"completed": True}).status_code == 404
    assert client.delete(f"/api/tasks/{uuid4()}").status_code == 404
    assert client.delete("/api/tasks/not-a-uuid").status_code == 422


def test_user_text_is_stored_as_data(client: TestClient) -> None:
    title = "<img src=x onerror=alert(1)> '); DROP TABLE tasks; --"
    assert client.post("/api/tasks", json={"title": title}).status_code == 201
    assert client.get("/api/tasks").json()[0]["title"] == title
    assert client.post("/api/tasks", json={"title": "Still works"}).status_code == 201
    assert len(client.get("/api/tasks").json()) == 2


def test_database_write_failure_does_not_report_success(tmp_path: Path) -> None:
    path = tmp_path / "tasks.db"
    with TestClient(create_app(path), raise_server_exceptions=False) as client:
        with closing(sqlite3.connect(path)) as connection, connection:
            connection.execute("""
                CREATE TRIGGER fail_insert BEFORE INSERT ON tasks
                BEGIN SELECT RAISE(ABORT, 'simulated storage failure'); END
            """)
        assert client.post("/api/tasks", json={"title": "Not saved"}).status_code == 500
        assert client.get("/api/tasks").json() == []
