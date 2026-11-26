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
    @given(
        TEXT.filter(lambda value: value != "human"),
        TEXT,
        st.sampled_from(("planning", "backlog", "todo")),
        st.booleans(),
    )
    def test_planning_claim(self, claimant, other, status, releasing):
        from chitty.model import claim_refusal

        if other in (claimant, "human"):
            other = claimant + "other"
        task = make_task(status, [], None, [])
        unclaimed = task.with_history(datetime(2026, 1, 1, tzinfo=UTC), claimant, "todo", "doing")
        claimed = unclaimed.with_history(
            datetime(2026, 1, 1, tzinfo=UTC), claimant, "backlog", "planning"
        )
        for actor in (claimant, other, "human"):
            self.assertIsNone(claim_refusal("TASK-1", unclaimed, actor, releasing))
            result = claim_refusal("TASK-1", claimed, actor, releasing)
            if status == "planning" and actor == other and not releasing:
                self.assertIsNotNone(result)
                assert result is not None
                self.assertIn(f"being planned by {claimant}", result)
            else:
                self.assertIsNone(result)

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

    @given(
        st.lists(
            st.sampled_from(
                (
                    ("review", "doing"),
                    ("done", "doing"),
                    ("doing", "review"),
                    ("review", "done"),
                    ("doing", "blocked"),
                    ("blocked", "doing"),
                )
            ),
            max_size=8,
        ),
        st.sampled_from(("review", "done")),
    )
    def test_landing_and_review_failures_escalate(self, transitions, status):
        task = make_task(status, [], None, [])
        when = datetime(2026, 1, 1, tzinfo=UTC)
        failures = 1
        for old, new in transitions:
            task = task.with_history(when, "other-reviewer", old, new)
            if new == "blocked":
                failures = 1
            elif (old, new) in (("review", "doing"), ("done", "doing")):
                failures += 1
        result = check_edit(
            task, fail_review_edit("Review failed: generated failure."), "fresh-reviewer"
        )
        self.assertEqual(result.status, "blocked" if failures >= REVIEW_FAILURE_LIMIT else "doing")
        if failures >= REVIEW_FAILURE_LIMIT:
            self.assertEqual(result.owner, "human")

    @given(
        st.lists(
            st.sampled_from(
                (
                    ("doing", "planning"),
                    ("review", "planning"),
                    ("doing", "to-plan"),
                    ("review", "to-plan"),
                    ("doing", "blocked"),
                    ("blocked", "doing"),
                )
            ),
            max_size=9,
        ),
        st.sampled_from(("doing", "review")),
        st.one_of(st.none(), st.just(""), TEXT),
    )
    def test_planning_returns_escalate_since_last_block(self, transitions, status, summary):
        task = make_task(status, [], None, [])
        count = 1
        for old, new in transitions:
            task = task.with_history(datetime(2026, 1, 1, tzinfo=UTC), "other", old, new)
            if new == "blocked":
                count = 1
            elif old in {"doing", "review"} and new in {"planning", "to-plan"}:
                count += 1
        result = check_edit(
            task, Edit(status="to-plan", note="\n reason\nmore", summary=summary), "fresh"
        )
        if count < 3:
            self.assertEqual(
                (result.status, result.owner, result.summary), ("to-plan", "", summary)
            )
        else:
            self.assertEqual((result.status, result.owner), ("blocked", "human"))
            self.assertIn("Escalated", result.notes[-1])
            if summary:
                self.assertEqual(result.summary, summary)
            else:
                assert result.summary is not None
                self.assertIn(str(count), result.summary)
                self.assertIn("reason", result.summary)

    @given(
        st.integers(min_value=0, max_value=5),
        st.one_of(st.none(), st.just(""), TEXT),
        st.booleans(),
    )
    def test_review_escalation_summary(self, failures, summary, has_note):
        task = make_task("done", [], None, [])
        for _ in range(failures):
            task = task.with_history(datetime(2026, 1, 1, tzinfo=UTC), "other", "review", "doing")
        result = check_edit(
            task,
            Edit(status="doing", notes=("\n  cause\nother",) if has_note else (), summary=summary),
            "fresh",
        )
        if failures + 1 < REVIEW_FAILURE_LIMIT or summary:
            self.assertEqual(result.summary, summary)
        else:
            assert result.summary is not None
            self.assertIn(str(failures + 1), result.summary)
            if has_note:
                self.assertIn("cause", result.summary)

    def test_landing_failure_is_not_a_review_transition(self):
        task = make_task("done", [], None, []).with_history(
            datetime(2026, 1, 1, tzinfo=UTC), "fresh-reviewer", "doing", "review"
        )
        edit = Edit(
            status="doing",
            note="Review failed (integration): x",
            skip_verdicts=True,
            skip_current_version=True,
        )
        self.assertEqual(check_edit(task, edit, "fresh-reviewer").status, "doing")

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
