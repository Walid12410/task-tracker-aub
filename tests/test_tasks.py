# Tests for all /tasks routes - Module 2
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# POST /tasks
# ---------------------------------------------------------------------------

def test_create_task_valid_returns_201_with_full_body(client: TestClient):
    r = client.post("/tasks", json={"title": "Buy milk", "priority": "High"})
    assert r.status_code == 201
    body = r.json()
    assert body["title"] == "Buy milk"
    assert body["priority"] == "High"
    assert body["status"] == "ToDo"
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


def test_create_task_missing_title_returns_422(client: TestClient):
    r = client.post("/tasks", json={"priority": "Low"})
    assert r.status_code == 422


def test_create_task_blank_title_returns_422(client: TestClient):
    r = client.post("/tasks", json={"title": "   "})
    assert r.status_code == 422


def test_create_task_invalid_priority_returns_422(client: TestClient):
    r = client.post("/tasks", json={"title": "Task", "priority": "Critical"})
    assert r.status_code == 422


def test_create_task_unknown_field_returns_422(client: TestClient):
    r = client.post("/tasks", json={"title": "Task", "color": "red"})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# GET /tasks
# ---------------------------------------------------------------------------

def test_list_tasks_empty_returns_200_and_empty_list(client: TestClient):
    r = client.get("/tasks")
    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(client: TestClient):
    client.post("/tasks", json={"title": "Task A"})
    r = client.get("/tasks", params={"status": "Done"})
    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client: TestClient):
    client.post("/tasks", json={"title": "Low task", "priority": "Low"})
    client.post("/tasks", json={"title": "High task", "priority": "High"})
    r = client.get("/tasks", params={"priority": "High"})
    assert r.status_code == 200
    results = r.json()
    assert len(results) == 1
    assert results[0]["title"] == "High task"


# ---------------------------------------------------------------------------
# GET /tasks/{id}
# ---------------------------------------------------------------------------

def test_get_task_by_id_returns_task(client: TestClient, created_task: dict):
    task_id = created_task["id"]
    r = client.get(f"/tasks/{task_id}")
    assert r.status_code == 200
    assert r.json()["id"] == task_id


def test_get_task_by_id_not_found_returns_404_with_detail(client: TestClient):
    r = client.get("/tasks/nonexistent-id")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"].lower()


# ---------------------------------------------------------------------------
# PATCH /tasks/{id}
# ---------------------------------------------------------------------------

def test_patch_partial_update_keeps_other_fields(client: TestClient, created_task: dict):
    task_id = created_task["id"]
    r = client.patch(f"/tasks/{task_id}", json={"description": "updated desc"})
    assert r.status_code == 200
    body = r.json()
    assert body["description"] == "updated desc"
    assert body["title"] == created_task["title"]


def test_patch_not_found_returns_404(client: TestClient):
    r = client.patch("/tasks/nonexistent-id", json={"description": "x"})
    assert r.status_code == 404
    assert "not found" in r.json()["detail"].lower()


def test_patch_valid_transition_todo_to_inprogress_returns_200(client: TestClient, created_task: dict):
    task_id = created_task["id"]
    r = client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})
    assert r.status_code == 200
    assert r.json()["status"] == "InProgress"


def test_patch_invalid_transition_todo_to_done_returns_422(client: TestClient, created_task: dict):
    task_id = created_task["id"]
    r = client.patch(f"/tasks/{task_id}", json={"status": "Done"})
    assert r.status_code == 422


def test_patch_same_status_returns_422(client: TestClient, created_task: dict):
    task_id = created_task["id"]
    r = client.patch(f"/tasks/{task_id}", json={"status": "ToDo"})
    assert r.status_code == 422


def test_patch_valid_transition_inprogress_to_done_returns_200(client: TestClient, created_task: dict):
    task_id = created_task["id"]
    client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})
    r = client.patch(f"/tasks/{task_id}", json={"status": "Done"})
    assert r.status_code == 200
    assert r.json()["status"] == "Done"


def test_patch_valid_transition_done_to_inprogress_returns_200(client: TestClient, created_task: dict):
    task_id = created_task["id"]
    client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})
    client.patch(f"/tasks/{task_id}", json={"status": "Done"})
    r = client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})
    assert r.status_code == 200
    assert r.json()["status"] == "InProgress"


def test_patch_whitespace_only_title_returns_422(client: TestClient, created_task: dict):
    task_id = created_task["id"]
    r = client.patch(f"/tasks/{task_id}", json={"title": "   "})
    assert r.status_code == 422


def test_patch_invalid_priority_value_returns_422(client: TestClient, created_task: dict):
    task_id = created_task["id"]
    r = client.patch(f"/tasks/{task_id}", json={"priority": "Critical"})
    assert r.status_code == 422


def test_patch_empty_body_returns_200_with_fields_unchanged(client: TestClient, created_task: dict):
    task_id = created_task["id"]
    r = client.patch(f"/tasks/{task_id}", json={})
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == created_task["title"]
    assert body["status"] == created_task["status"]
    assert body["priority"] == created_task["priority"]
    assert body["assignee"] == created_task["assignee"]


def test_patch_unknown_field_returns_422(client: TestClient, created_task: dict):
    task_id = created_task["id"]
    r = client.patch(f"/tasks/{task_id}", json={"color": "red"})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# DELETE /tasks/{id}
# ---------------------------------------------------------------------------

def test_delete_existing_returns_204_no_body(client: TestClient, created_task: dict):
    task_id = created_task["id"]
    r = client.delete(f"/tasks/{task_id}")
    assert r.status_code == 204
    assert r.content == b""


def test_delete_missing_returns_404(client: TestClient):
    r = client.delete("/tasks/nonexistent-id")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Tags — Feature 1
# ---------------------------------------------------------------------------

def test_create_task_with_tags_returns_201_and_tags_in_response(client: TestClient):
    r = client.post("/tasks", json={"title": "Tagged task", "tags": ["frontend", "bug"]})
    assert r.status_code == 201
    body = r.json()
    assert body["tags"] == ["frontend", "bug"]


def test_create_task_with_empty_string_tag_returns_422(client: TestClient):
    r = client.post("/tasks", json={"title": "Bad tag", "tags": [""]})
    assert r.status_code == 422


def test_create_task_with_whitespace_only_tag_returns_422(client: TestClient):
    r = client.post("/tasks", json={"title": "Bad tag", "tags": ["   "]})
    assert r.status_code == 422


def test_create_task_with_too_many_tags_returns_422(client: TestClient):
    r = client.post("/tasks", json={"title": "Too many", "tags": [str(i) for i in range(11)]})
    assert r.status_code == 422


def test_create_task_with_no_tags_defaults_to_empty_list(client: TestClient):
    r = client.post("/tasks", json={"title": "No tags"})
    assert r.status_code == 201
    assert r.json()["tags"] == []


def test_patch_task_tags_preserves_other_fields(client: TestClient, created_task: dict):
    task_id = created_task["id"]
    r = client.patch(f"/tasks/{task_id}", json={"tags": ["backend"]})
    assert r.status_code == 200
    body = r.json()
    assert body["tags"] == ["backend"]
    assert body["title"] == created_task["title"]
    assert body["status"] == created_task["status"]


def test_patch_task_tags_can_be_cleared(client: TestClient, created_task: dict):
    task_id = created_task["id"]
    client.patch(f"/tasks/{task_id}", json={"tags": ["backend"]})
    r = client.patch(f"/tasks/{task_id}", json={"tags": []})
    assert r.status_code == 200
    assert r.json()["tags"] == []


def test_patch_unrelated_update_preserves_tags(client: TestClient):
    r = client.post("/tasks", json={"title": "With tags", "tags": ["api", "v2"]})
    task_id = r.json()["id"]
    r2 = client.patch(f"/tasks/{task_id}", json={"description": "updated desc"})
    assert r2.status_code == 200
    assert r2.json()["tags"] == ["api", "v2"]


def test_list_tasks_filter_by_tag_returns_only_matching(client: TestClient):
    client.post("/tasks", json={"title": "Frontend task", "tags": ["frontend"]})
    client.post("/tasks", json={"title": "Backend task", "tags": ["backend"]})
    r = client.get("/tasks", params={"tag": "frontend"})
    assert r.status_code == 200
    results = r.json()
    assert len(results) == 1
    assert results[0]["title"] == "Frontend task"


def test_list_tasks_filter_by_tag_no_match_returns_empty_list(client: TestClient):
    client.post("/tasks", json={"title": "Some task", "tags": ["docs"]})
    r = client.get("/tasks", params={"tag": "nonexistent"})
    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_filter_by_tag_is_case_insensitive(client: TestClient):
    client.post("/tasks", json={"title": "Case task", "tags": ["Frontend"]})
    r = client.get("/tasks", params={"tag": "frontend"})
    assert r.status_code == 200
    assert len(r.json()) == 1


# ---------------------------------------------------------------------------
# Search + Combined Filters — Feature 2
# ---------------------------------------------------------------------------

def test_list_tasks_search_by_title_returns_matching(client: TestClient):
    client.post("/tasks", json={"title": "Fix login bug", "description": ""})
    client.post("/tasks", json={"title": "Update readme", "description": ""})
    r = client.get("/tasks", params={"q": "login"})
    assert r.status_code == 200
    results = r.json()
    assert len(results) == 1
    assert results[0]["title"] == "Fix login bug"


def test_list_tasks_search_by_description_returns_matching(client: TestClient):
    client.post("/tasks", json={"title": "Task A", "description": "involves database migration"})
    client.post("/tasks", json={"title": "Task B", "description": "frontend styling"})
    r = client.get("/tasks", params={"q": "database"})
    assert r.status_code == 200
    results = r.json()
    assert len(results) == 1
    assert results[0]["title"] == "Task A"


def test_list_tasks_search_is_case_insensitive(client: TestClient):
    client.post("/tasks", json={"title": "Deploy to Production", "description": ""})
    r = client.get("/tasks", params={"q": "production"})
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_list_tasks_search_no_match_returns_200_empty_list(client: TestClient):
    client.post("/tasks", json={"title": "Some task", "description": ""})
    r = client.get("/tasks", params={"q": "zzznomatch"})
    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_combined_search_and_status_filter(client: TestClient):
    client.post("/tasks", json={"title": "Auth bug", "description": "", "status": "InProgress"})
    client.post("/tasks", json={"title": "Auth docs", "description": "", "status": "Done"})
    r = client.get("/tasks", params={"q": "auth", "status": "InProgress"})
    assert r.status_code == 200
    results = r.json()
    assert len(results) == 1
    assert results[0]["title"] == "Auth bug"


def test_list_tasks_combined_tag_and_priority_filter(client: TestClient):
    client.post("/tasks", json={"title": "High backend", "priority": "High", "tags": ["backend"]})
    client.post("/tasks", json={"title": "Low backend",  "priority": "Low",  "tags": ["backend"]})
    client.post("/tasks", json={"title": "High frontend","priority": "High", "tags": ["frontend"]})
    r = client.get("/tasks", params={"tag": "backend", "priority": "High"})
    assert r.status_code == 200
    results = r.json()
    assert len(results) == 1
    assert results[0]["title"] == "High backend"
