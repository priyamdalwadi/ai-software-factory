import unittest

from factory import State, Task, transition


class TransitionTests(unittest.TestCase):
    def test_happy_path_preserves_history_and_identity(self) -> None:
        task = Task("t-1")
        for target in (State.IMPLEMENTING, State.REVIEWING, State.REVIEW_ACCEPTED):
            task = transition(task, target)
        self.assertEqual(task.task_id, "t-1")
        self.assertEqual(task.history, tuple(State))
        self.assertEqual(task.state, State.REVIEW_ACCEPTED)

    def test_cannot_skip_review_and_failure_does_not_mutate(self) -> None:
        task = transition(Task("t-2"), State.IMPLEMENTING)
        with self.assertRaisesRegex(ValueError, "Illegal transition"):
            transition(task, State.REVIEW_ACCEPTED)
        self.assertEqual(task.state, State.IMPLEMENTING)
        self.assertEqual(len(task.history), 2)

    def test_rejected_review_can_return_to_implementation(self) -> None:
        task = transition(Task("t-3"), State.IMPLEMENTING)
        task = transition(task, State.REVIEWING)
        task = transition(task, State.IMPLEMENTING)
        self.assertEqual(task.history[-2:], (State.REVIEWING, State.IMPLEMENTING))

    def test_accepted_task_has_no_outbound_transition(self) -> None:
        task = Task("t-4")
        for target in (State.IMPLEMENTING, State.REVIEWING, State.REVIEW_ACCEPTED):
            task = transition(task, target)
        for target in State:
            with self.subTest(target=target), self.assertRaises(ValueError):
                transition(task, target)


if __name__ == "__main__":
    unittest.main()
