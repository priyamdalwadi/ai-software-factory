"""Validated API requests and responses."""

from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StrictBool, StringConstraints


class TaskInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
    notes: Annotated[str, StringConstraints(strip_whitespace=True, max_length=1000)] = ""
    priority: Literal["low", "normal", "high"] = "normal"


class Task(TaskInput):
    id: UUID
    completed: bool
    created_at: str


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    completed: StrictBool
