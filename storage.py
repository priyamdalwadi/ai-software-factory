"""SQLite adapter: save task state and transition history together."""

import sqlite3
from contextlib import closing
from pathlib import Path

from factory import State, Task, transition


class TaskStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        with closing(self._connect()) as connection, connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY NOT NULL,
                    state TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS events (
                    event_id INTEGER PRIMARY KEY,
                    task_id TEXT NOT NULL REFERENCES tasks(task_id),
                    state TEXT NOT NULL,
                    recorded_at TEXT NOT NULL DEFAULT
                        (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
                );
                CREATE INDEX IF NOT EXISTS events_by_task
                    ON events(task_id, event_id);
            """)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @staticmethod
    def _load(connection: sqlite3.Connection, task_id: str) -> Task:
        row = connection.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
        if row is None:
            raise KeyError(f"Unknown task: {task_id}")
        history = connection.execute(
            "SELECT state FROM events WHERE task_id = ? ORDER BY event_id",
            (task_id,),
        ).fetchall()
        return Task(task_id, State(row[0]), tuple(State(item[0]) for item in history))

    def create(self, task_id: str) -> Task:
        task = Task(task_id)
        with closing(self._connect()) as connection, connection:
            connection.execute(
                "INSERT INTO tasks(task_id, state) VALUES (?, ?)",
                (task_id, task.state.value),
            )
            connection.execute(
                "INSERT INTO events(task_id, state) VALUES (?, ?)",
                (task_id, task.state.value),
            )
        return task

    def load(self, task_id: str) -> Task:
        with closing(self._connect()) as connection, connection:
            connection.execute("BEGIN")
            return self._load(connection, task_id)

    def advance(self, task_id: str, target: State) -> Task:
        with closing(self._connect()) as connection, connection:
            # Reserve the writer before reading, so this update uses current state.
            connection.execute("BEGIN IMMEDIATE")
            task = transition(self._load(connection, task_id), target)
            connection.execute(
                "UPDATE tasks SET state = ? WHERE task_id = ?",
                (task.state.value, task_id),
            )
            connection.execute(
                "INSERT INTO events(task_id, state) VALUES (?, ?)",
                (task_id, task.state.value),
            )
        return task
