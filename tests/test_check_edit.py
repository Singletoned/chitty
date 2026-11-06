import unittest
from datetime import UTC, date, datetime

from hypothesis import given
from hypothesis import strategies as st

from chitty.errors import ChittyError
from chitty.model import new_task
from chitty.run import claim_edit, fail_review_edit
from chitty.store import REVIEW_FAILURE_LIMIT, Edit, check_edit

STATUSES = st.sampled_from(("backlog", "todo", "doing", "blocked", "review", "done"))
TEXT = st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=12)


def make_task(status, criteria, owner, notes):
    task = new_task(
        "Generated task",
        date(2026, 1, 1),
        "Description.",
        criteria,
        {"status": status, **({"owner": owner} if owner else {})},
    )
    for note in notes:
        task = task.with_note(note)
    return task


@st.composite
def tasks(draw, statuses=STATUSES):
    status = draw(statuses)
    criteria = draw(st.lists(TEXT, max_size=6))
    owner = draw(st.one_of(st.none(), TEXT))
    notes = draw(st.lists(TEXT, max_size=3))
    return make_task(status, criteria, owner, notes)


class TestCheckEdit(unittest.TestCase):
    @given(tasks(statuses=st.just("todo")))
    def test_claim_edit_is_accepted_for_every_todo_task(self, task):
        self.assertEqual(check_edit(task, claim_edit(), "fresh-reviewer").status, "doing")

    @given(tasks(statuses=st.just("review")))
    def test_fail_review_edit_is_accepted_for_every_review_task(self, task):
        edit = fail_review_edit("Review failed: generated failure.")
        self.assertIn(check_edit(task, edit, "fresh-reviewer").status, {"doing", "blocked"})

    @given(st.lists(TEXT, max_size=6), st.booleans(), st.booleans())
    def test_done_review_requires_reviewed_note_and_all_pass_verdicts(
        self, criteria, reviewed, passing
    ):
        task = make_task("review", criteria, None, [])
        verdicts = [
            f"{index}: {'pass' if passing else 'fail'} - checked"
            for index in range(1, len(criteria) + 1)
        ]
        note = "Reviewed: generated review.\n" + "\n".join(verdicts) if reviewed else "Not a review"
        edit = Edit(status="done", note=note)
        accepted = reviewed and (passing or not criteria)
        try:
            check_edit(task, edit, "fresh-reviewer")
        except ChittyError:
            self.assertFalse(accepted)
        else:
            self.assertTrue(accepted)

    @given(st.integers(min_value=0, max_value=5))
    def test_failed_reviews_escalate_at_the_limit(self, failures):
        task = make_task("review", [], None, [])
        when = datetime(2026, 1, 1, tzinfo=UTC)
        for _ in range(failures):
            task = task.with_history(when, "other-reviewer", "review", "doing")
        result = check_edit(
            task,
            fail_review_edit("Review failed: generated failure."),
            "fresh-reviewer",
        )
        if failures + 1 < REVIEW_FAILURE_LIMIT:
            self.assertEqual(result.status, "doing")
        else:
            self.assertEqual(result.status, "blocked")
            self.assertEqual(result.owner, "human")
