import unittest

from hypothesis import given
from hypothesis import strategies as st

from chitty.errors import ChittyError
from chitty.ids import TaskId
from chitty.ticket_source import WORKING_TREE, ticket_source


@st.composite
def graphs(draw):
    size = draw(st.integers(min_value=5, max_value=12))
    fork_at = draw(st.integers(min_value=1, max_value=size - 3))
    fork = draw(st.booleans())

    def contains(a, b):
        ai, bi = map(int, (a, b))
        if not fork:
            return ai >= bi
        # 0..fork_at is shared; then two arms, then unrelated tail.
        if bi <= fork_at:
            return ai < size - 2 and ai >= bi or ai == bi
        return ai == bi or (ai in (fork_at + 1, fork_at + 2) and bi <= fork_at)

    # Explicit DAG represented by indices; fork tips are incomparable.
    def reachable(a, b):
        ai, bi = int(a), int(b)
        if ai == bi:
            return True
        if not fork:
            return ai >= bi
        left, right = size - 2, size - 1
        if ai in (left, right):
            return bi <= fork_at or bi == ai
        return ai <= fork_at and bi <= ai

    return size, fork, reachable


class TestTicketSource(unittest.TestCase):
    @given(graphs())
    def test_provisional_overrides_everything(self, graph):
        _, _, contains = graph
        self.assertEqual(
            ticket_source(
                TaskId("TASK", 5),
                True,
                None,
                "main",
                None,
                {"task-5": "1"},
                {},
                contains,
                lambda ref: True,
            ),
            WORKING_TREE,
        )

    @given(graphs(), st.booleans())
    def test_fallback_after_candidates_dropped_or_absent(self, graph, on_main):
        _, _, contains = graph
        result = ticket_source(
            TaskId("TASK", 5),
            False,
            "main" if on_main else None,
            "main",
            "0",
            {"task-5": "0"},
            {},
            contains,
            lambda ref: False,
        )
        self.assertEqual(result, WORKING_TREE if on_main else "main")

    @given(st.integers(min_value=2, max_value=40))
    def test_descendant_candidate_wins_and_local_worktree_is_respected(self, tip):
        ancestor = str(tip - 1)
        result = ticket_source(
            TaskId("TASK", 5),
            False,
            "task-5",
            "main",
            "0",
            {"task-5": ancestor},
            {"origin/task-5": str(tip)},
            lambda a, b: int(a) >= int(b),
            lambda ref: False,
        )
        self.assertEqual(result, "origin/task-5")

    @given(st.integers(min_value=4, max_value=40))
    def test_diverged_candidates_are_named(self, root):
        left, right = str(root + 1), str(root + 2)

        def ancestry(a, b):
            return a == b or (a == left and b == str(root)) or (a == right and b == str(root))

        with self.assertRaises(ChittyError) as raised:
            ticket_source(
                TaskId("TASK", 5),
                False,
                None,
                "main",
                str(root),
                {"task-5": left},
                {"origin/task-5": right},
                ancestry,
                lambda ref: False,
            )
        self.assertIn("`task-5`", str(raised.exception))
        self.assertIn("`origin/task-5`", str(raised.exception))

    @given(st.integers(min_value=2, max_value=40))
    def test_changed_on_both_names_ticket_ref_and_main(self, tip):
        with self.assertRaises(ChittyError) as raised:
            ticket_source(
                TaskId("TASK", 5),
                False,
                None,
                "main",
                "0",
                {"task-5": str(tip)},
                {},
                lambda a, b: int(a) >= int(b),
                lambda ref: ref == "task-5",
            )
        message = str(raised.exception)
        for name in ("TASK-5", "task-5", "main"):
            self.assertIn(f"`{name}`", message)

    def test_decoys_do_not_change_answer(self):
        def ancestry(a, b):
            return int(a) >= int(b)

        baseline = ticket_source(
            TaskId("TASK", 5),
            False,
            None,
            "main",
            "0",
            {"task-5": "2"},
            {"origin/task-5": "3"},
            ancestry,
            lambda ref: False,
        )
        with_decoys = ticket_source(
            TaskId("TASK", 5),
            False,
            None,
            "main",
            "0",
            {"task-5": "2", "TASK-5": "8", "task-50": "9", "feature/task-5": "9"},
            {"origin/task-5": "3", "origin/task-50": "8", "origin/x/task-5": "9"},
            ancestry,
            lambda ref: False,
        )
        self.assertEqual(with_decoys, baseline)
