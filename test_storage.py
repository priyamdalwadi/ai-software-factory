import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from factory import State
from storage import TaskStore


class PersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "test.db"
        self.store = TaskStore(self.path)
        self.store.create("t-1")

    def test_new_python_process_reads_committed_history(self) -> None:
        self.store.advance("t-1", State.IMPLEMENTING)
        self.store.advance("t-1", State.REVIEWING)
        result = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).with_name("lesson2.py")),
                "--db",
                str(self.path),
                "show",
                "t-1",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(
            json.loads(result.stdout),
            {
                "task_id": "t-1",
                "state": "reviewing",
                "history": ["received", "implementing", "reviewing"],
            },
        )

    def test_failed_event_insert_rolls_back_state_update(self) -> None:
        # Force failure AFTER UPDATE but before the transaction can commit.
        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.execute("""
                CREATE TRIGGER reject_event BEFORE INSERT ON events
                BEGIN SELECT RAISE(ABORT, 'simulated disk-write failure'); END
            """)
        with self.assertRaisesRegex(sqlite3.IntegrityError, "simulated"):
            self.store.advance("t-1", State.IMPLEMENTING)
        task = TaskStore(self.path).load("t-1")
        self.assertEqual(task.state, State.RECEIVED)
        self.assertEqual(task.history, (State.RECEIVED,))

    def test_invalid_transition_changes_neither_state_nor_history(self) -> None:
        before = self.store.load("t-1")
        with self.assertRaises(ValueError):
            self.store.advance("t-1", State.REVIEW_ACCEPTED)
        self.assertEqual(self.store.load("t-1"), before)

    def test_duplicate_creation_does_not_reset_existing_task(self) -> None:
        before = self.store.advance("t-1", State.IMPLEMENTING)
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.create("t-1")
        self.assertEqual(self.store.load("t-1"), before)

    def test_missing_task_is_explicit(self) -> None:
        with self.assertRaisesRegex(KeyError, "Unknown task"):
            self.store.load("missing")


if __name__ == "__main__":
    unittest.main()
