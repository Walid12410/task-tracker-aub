# Repository layer: all reads and writes to the JSON data file go through this class
import threading
from pathlib import Path
from typing import Optional

from app.models import Task, TaskCreate

DATA_FILE = Path(__file__).parent.parent / "data" / "tasks.json"

# Prevents two concurrent write operations from corrupting the file
_lock = threading.Lock()


class TaskRepository:
    def list_all(self) -> list[Task]:
        raise NotImplementedError

    def get_by_id(self, task_id: int) -> Optional[Task]:
        raise NotImplementedError

    def create(self, task: TaskCreate) -> Task:
        raise NotImplementedError

    def update(self, task: Task) -> Task:
        raise NotImplementedError

    def delete(self, task_id: int) -> bool:
        raise NotImplementedError
