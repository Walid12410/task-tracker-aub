# In-memory storage for tasks
import uuid
from datetime import datetime, timezone
from typing import Optional

from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

_tasks: dict[str, TaskResponse] = {}


def add_task(payload: TaskCreate) -> TaskResponse:
    now = datetime.now(timezone.utc)
    task = TaskResponse(
        id=str(uuid.uuid4()),
        title=payload.title,
        description=payload.description or "",
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        tags=payload.tags,
        created_at=now,
        updated_at=now,
    )
    _tasks[task.id] = task
    return task


def get_all_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    q: Optional[str] = None,
    tag: Optional[str] = None,
    assignee: Optional[str] = None,
) -> list[TaskResponse]:
    result = list(_tasks.values())

    if status is not None:
        result = [t for t in result if t.status == status]

    if priority is not None:
        result = [t for t in result if t.priority == priority]

    if assignee is not None:
        result = [t for t in result if t.assignee == assignee]

    if tag is not None:
        tag_lower = tag.strip().lower()
        result = [t for t in result if any(tg.lower() == tag_lower for tg in t.tags)]

    if q is not None:
        q_lower = q.strip().lower()
        if q_lower:
            result = [
                t for t in result
                if q_lower in t.title.lower() or q_lower in t.description.lower()
            ]

    return result


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    task = _tasks.get(task_id)
    if task is None:
        return None
    patch = payload.model_dump(exclude_unset=True)
    updated = task.model_copy(update={**patch, "updated_at": datetime.now(timezone.utc)})
    _tasks[task_id] = updated
    return updated


def delete_task(task_id: str) -> bool:
    if task_id not in _tasks:
        return False
    del _tasks[task_id]
    return True


def _reset() -> None:
    _tasks.clear()
