# Service layer: enforces business rules including valid status transitions
from typing import Optional

from app.models import Task, TaskCreate, TaskStatus, TaskUpdate
from app.repository import TaskRepository

# Only forward transitions are permitted; backward transitions are rejected
VALID_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.todo: {TaskStatus.in_progress, TaskStatus.done},
    TaskStatus.in_progress: {TaskStatus.done},
    TaskStatus.done: set(),
}


class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def list_tasks(self, status: Optional[TaskStatus] = None, priority=None) -> list[Task]:
        raise NotImplementedError

    def get_task(self, task_id: int) -> Task:
        raise NotImplementedError

    def create_task(self, data: TaskCreate) -> Task:
        raise NotImplementedError

    def update_task(self, task_id: int, data: TaskUpdate) -> Task:
        raise NotImplementedError

    def delete_task(self, task_id: int) -> bool:
        raise NotImplementedError
