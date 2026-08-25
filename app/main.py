# Entry point: creates the FastAPI application instance and registers global routes
import os
from datetime import datetime, timezone
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app import storage
from app.business_rules import validate_status_transition
from app.models import HealthResponse, TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

load_dotenv()

app = FastAPI(
    title="Task Tracker API",
    version="0.1.0",
    description="REST API for managing tasks",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)


def _seed_dummy_data() -> None:
    dummy = [
        TaskCreate(title="Design database schema",     description="Define tables, relationships, and indexes.",          status=TaskStatus.TODO,        priority=TaskPriority.HIGH,   assignee=None,    tags=["backend", "database"]),
        TaskCreate(title="Write API documentation",    description="Document all endpoints using OpenAPI comments.",      status=TaskStatus.TODO,        priority=TaskPriority.MEDIUM, assignee="Carol",  tags=["docs"]),
        TaskCreate(title="Add input validation",       description="Use Pydantic validators on all request bodies.",      status=TaskStatus.TODO,        priority=TaskPriority.LOW,    assignee=None,    tags=["backend", "validation"]),
        TaskCreate(title="Build REST API endpoints",   description="Implement CRUD routes for tasks with FastAPI.",       status=TaskStatus.IN_PROGRESS, priority=TaskPriority.HIGH,   assignee="Alice",  tags=["backend", "api"]),
        TaskCreate(title="Integrate frontend fetch",   description="Connect board UI to GET /tasks and render cards.",    status=TaskStatus.IN_PROGRESS, priority=TaskPriority.MEDIUM, assignee="Bob",    tags=["frontend"]),
        TaskCreate(title="Set up project structure",   description="Scaffold folders, venv, requirements, and Makefile.", status=TaskStatus.DONE,        priority=TaskPriority.LOW,    assignee="Bob",    tags=["devops"]),
        TaskCreate(title="Configure CORS middleware",  description="Allow frontend origin in FastAPI middleware.",         status=TaskStatus.DONE,        priority=TaskPriority.MEDIUM, assignee="Alice",  tags=["backend", "security"]),
    ]
    for task in dummy:
        storage.add_task(task)

_seed_dummy_data()


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    q: Optional[str] = None,
    tag: Optional[str] = None,
    assignee: Optional[str] = None,
) -> list[TaskResponse]:
    return storage.get_all_tasks(status=status, priority=priority, q=q, tag=tag, assignee=assignee)


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    return storage.add_task(payload)


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def patch_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    if payload.status is not None:
        existing = storage.get_task_by_id(task_id)
        if existing is None:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
        validate_status_transition(existing.status, payload.status)
    task = storage.update_task(task_id, payload)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: str) -> None:
    if not storage.delete_task(task_id):
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")


@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
