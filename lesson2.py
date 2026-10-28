"""Each invocation starts a new process and opens the same database file."""

import argparse
import json
import sqlite3
from pathlib import Path

from factory import State
from storage import TaskStore


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=Path("lesson2.db"))
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("create", "show", "move"):
        command = commands.add_parser(name)
        command.add_argument("task_id")
        if name == "move":
            command.add_argument("state", choices=[state.value for state in State])
    args = parser.parse_args()
    try:
        store = TaskStore(args.db)
        if args.command == "create":
            task = store.create(args.task_id)
        elif args.command == "show":
            task = store.load(args.task_id)
        else:
            task = store.advance(args.task_id, State(args.state))
    except (KeyError, ValueError, sqlite3.Error) as error:
        parser.exit(1, f"{type(error).__name__}: {error}\n")
    print(
        json.dumps(
            {
                "task_id": task.task_id,
                "state": task.state.value,
                "history": [state.value for state in task.history],
            }
        )
    )


if __name__ == "__main__":
    main()
