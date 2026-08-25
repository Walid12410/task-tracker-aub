# Pydantic models for request/response validation across the entire application
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class HealthResponse(BaseModel):
    status: str
    timestamp: str


class TaskStatus(str, Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    tags: list[str] = []

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("title must not be empty or whitespace-only")
        if len(stripped) > 200:
            raise ValueError("title must not exceed 200 characters")
        return stripped

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        if len(v) > 10:
            raise ValueError("a task may have at most 10 tags")
        result = []
        for tag in v:
            t = tag.strip()
            if not t:
                raise ValueError("tags must not be empty or whitespace-only")
            if len(t) > 50:
                raise ValueError("each tag must not exceed 50 characters")
            result.append(t)
        return result


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = None
    tags: Optional[list[str]] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        stripped = v.strip()
        if not stripped:
            raise ValueError("title must not be empty or whitespace-only")
        if len(stripped) > 200:
            raise ValueError("title must not exceed 200 characters")
        return stripped

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        if v is None:
            return v
        if len(v) > 10:
            raise ValueError("a task may have at most 10 tags")
        result = []
        for tag in v:
            t = tag.strip()
            if not t:
                raise ValueError("tags must not be empty or whitespace-only")
            if len(t) > 50:
                raise ValueError("each tag must not exceed 50 characters")
            result.append(t)
        return result


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str]
    tags: list[str]
    created_at: datetime
    updated_at: datetime
