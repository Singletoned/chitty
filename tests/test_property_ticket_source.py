import unittest

from hypothesis import given
from hypothesis import strategies as st

from chitty.errors import ChittyError
from chitty.ids import TaskId
from chitty.ticket_source import WORKING_TREE, ticket_source


@st.composite
def graphs(draw):
    fork = draw(st.booleans())

    def contains(a, b):
        a, b = int(a), int(b)
        if a == b:
            return True
        if not fork:
            return a > b
        # 0 is the shared root; 1 and 2 fork; 3+ are unrelated commits.
        return a in (1, 2) and b == 0

    return fork, contains


@st.composite
def task_ids(draw):
    prefix = draw(st.sampled_from(["TASK", "HUMAN", "BUG"]))
    number = draw(st.integers(min_value=1, max_value=99))
    return TaskId(prefix, number)


class TestTicketSource(unittest.TestCase):
    @given(graphs(), task_ids(), st.booleans(), st.booleans())
    def test_provisional_always_uses_working_tree(self, graph, task_id, on_main, changed):
        _, contains = graph
        self.assertEqual(
            ticket_source(
                task_id,
                True,
                "main" if on_main else None,
                "main",
                None,
                {str(task_id).lower(): "2"},
                {},
                contains,
                lambda ref: changed,
            ),
            WORKING_TREE,
        )

    @given(graphs(), task_ids(), st.booleans(), st.booleans())
    def test_no_candidates_falls_back_or_errors_for_missing_main(
        self, graph, task_id, on_main, has_tip
    ):
        _, contains = graph
        main_tip = "0" if has_tip else None

        def call():
            return ticket_source(
                task_id,
                False,
                "main" if on_main else None,
                "main",
                main_tip,
                {},
                {},
                contains,
                lambda ref: False,
            )

        if not has_tip and not on_main:
            with self.assertRaisesRegex(ChittyError, "`main`"):
                call()
        else:
            self.assertEqual(call(), WORKING_TREE if on_main else "main")

    @given(graphs(), task_ids(), st.booleans())
    def test_main_drops_contained_candidates(self, graph, task_id, on_main):
        _, contains = graph
        branch = str(task_id).lower()
        # main tip is equal to the candidate tip, hence it is dropped.
        result = ticket_source(
            task_id,
            False,
            "main" if on_main else None,
            "main",
            "1",
            {branch: "1"},
            {},
            contains,
            lambda ref: False,
        )
        self.assertEqual(result, WORKING_TREE if on_main else "main")

    @given(graphs(), task_ids(), st.booleans())
    def test_candidate_at_chosen_tip_and_local_checkout(self, graph, task_id, fork):
        is_fork, contains = graph
        branch = str(task_id).lower()
        # main is unrelated to the candidate chain on a fork, and older on
        # a linear history.
        ancestor, descendant, main_tip = ("0", "1", "3") if is_fork else ("1", "2", "0")
        result = ticket_source(
            task_id,
            False,
            branch,
            "main",
            main_tip,
            {branch: descendant},
            {"origin/" + branch: ancestor},
            contains,
            lambda ref: False,
        )
        # In chain, local is the descendant; in fork neither candidate is
        # dropped and the root/arm relationship still chooses the descendant.
        self.assertEqual(result, WORKING_TREE)

    @given(graphs(), task_ids(), st.booleans())
    def test_equal_tip_prefers_local_then_remote_name(self, graph, task_id, current):
        _, contains = graph
        branch = str(task_id).lower()
        tips = {branch: "2"} if current else {}
        result = ticket_source(
            task_id,
            False,
            branch if current else None,
            "main",
            "0",
            tips,
            {"zeta/" + branch: "2", "alpha/" + branch: "2"},
            contains,
            lambda ref: False,
        )
        self.assertEqual(result, WORKING_TREE if current else "alpha/" + branch)

    @given(graphs(), task_ids())
    def test_changed_on_both_reports_chosen_remote(self, graph, task_id):
        _, contains = graph
        branch = str(task_id).lower()
        with self.assertRaises(ChittyError) as raised:
            ticket_source(
                task_id,
                False,
                None,
                "main",
                "0",
                {},
                {"origin/" + branch: "2"},
                contains,
                lambda ref: ref == "origin/" + branch,
            )
        message = str(raised.exception)
        for name in (str(task_id), "origin/" + branch, "main"):
            self.assertIn(f"`{name}`", message)

    @given(task_ids())
    def test_divergence_names_remaining_candidates_not_dropped_ones(self, task_id):
        def contains(a, b):
            return a == b or (a in ("1", "2") and b == "0")

        branch = str(task_id).lower()
        with self.assertRaises(ChittyError) as raised:
            ticket_source(
                task_id,
                False,
                None,
                "main",
                "1",
                {branch: "1"},
                {"origin/" + branch: "2", "backup/" + branch: "3"},
                contains,
                lambda ref: False,
            )
        message = str(raised.exception)
        self.assertIn(f"`origin/{branch}`", message)
        self.assertIn(f"`backup/{branch}`", message)
        self.assertNotIn(f"`{branch}`", message)

    @given(graphs(), task_ids())
    def test_decoys_and_unrelated_refs_do_not_change_result(self, graph, task_id):
        _, contains = graph
        branch = str(task_id).lower()
        base = ticket_source(
            task_id,
            False,
            None,
            "main",
            "0",
            {branch: "2"},
            {},
            contains,
            lambda ref: False,
        )
        expanded = ticket_source(
            task_id,
            False,
            None,
            "main",
            "0",
            {
                branch: "2",
                branch.upper(): "3",
                branch + "0": "3",
                "feature/" + branch: "3",
                "other": "3",
            },
            {"origin/" + branch + "0": "3", "origin/x/" + branch: "3"},
            contains,
            lambda ref: False,
        )
        self.assertEqual(expanded, base)
