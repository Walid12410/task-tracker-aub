# Shared fixtures available to all test modules
import pytest
from fastapi.testclient import TestClient

from app import storage
from app.main import app


@pytest.fixture(autouse=True)
def _reset_storage():
    storage._reset()
    yield
    storage._reset()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def created_task(client: TestClient) -> dict:
    r = client.post("/tasks", json={"title": "fixture task"})
    assert r.status_code == 201
    return r.json()
