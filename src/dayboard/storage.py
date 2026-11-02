"""SQLite storage; every operation uses its own short-lived connection."""

import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from dayboard.models import Task, TaskInput


class TaskStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=5)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with closing(self.connect()) as connection, connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY NOT NULL,
                    title TEXT NOT NULL,
                    notes TEXT NOT NULL,
                    priority TEXT NOT NULL CHECK(priority IN ('low', 'normal', 'high')),
                    completed INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0, 1)),
                    created_at TEXT NOT NULL
                )
            """)

    def list(self) -> list[Task]:
        with closing(self.connect()) as connection:
            rows = connection.execute("SELECT * FROM tasks ORDER BY created_at DESC, id").fetchall()
        return [Task.model_validate(dict(row)) for row in rows]

    def create(self, request: TaskInput) -> Task:
        task = Task(
            **request.model_dump(),
            id=uuid4(),
            completed=False,
            created_at=datetime.now(UTC).isoformat(),
        )
        with closing(self.connect()) as connection, connection:
            connection.execute(
                "INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?)",
                (str(task.id), task.title, task.notes, task.priority, 0, task.created_at),
            )
        return task

    def set_completed(self, task_id: UUID, completed: bool) -> Task | None:
        with closing(self.connect()) as connection, connection:
            changed = connection.execute(
                "UPDATE tasks SET completed = ? WHERE id = ?", (int(completed), str(task_id))
            )
            if changed.rowcount == 0:
                return None
            row = connection.execute("SELECT * FROM tasks WHERE id = ?", (str(task_id),)).fetchone()
            return Task.model_validate(dict(row))

    def delete(self, task_id: UUID) -> bool:
        with closing(self.connect()) as connection, connection:
            result = connection.execute("DELETE FROM tasks WHERE id = ?", (str(task_id),))
            return result.rowcount == 1
