"""Lesson 1: legal task transitions, without agents or persistence yet."""

import json
from dataclasses import dataclass
from enum import StrEnum


class State(StrEnum):
    RECEIVED = "received"
    IMPLEMENTING = "implementing"
    REVIEWING = "reviewing"
    REVIEW_ACCEPTED = "review_accepted"


ALLOWED = {
    State.RECEIVED: frozenset({State.IMPLEMENTING}),
    State.IMPLEMENTING: frozenset({State.REVIEWING}),
    State.REVIEWING: frozenset({State.IMPLEMENTING, State.REVIEW_ACCEPTED}),
    State.REVIEW_ACCEPTED: frozenset(),
}


@dataclass(frozen=True)
class Task:
    task_id: str
    state: State = State.RECEIVED
    history: tuple[State, ...] = (State.RECEIVED,)


def transition(task: Task, target: State) -> Task:
    """Return a new task, or reject an illegal transition without mutation."""
    if target not in ALLOWED[task.state]:
        raise ValueError(f"Illegal transition: {task.state.value} -> {target.value}")
    return Task(task.task_id, target, task.history + (target,))


def main() -> None:
    task = Task("lesson-1")
    for target in (State.IMPLEMENTING, State.REVIEWING, State.REVIEW_ACCEPTED):
        task = transition(task, target)
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
