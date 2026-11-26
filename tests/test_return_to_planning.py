import os
import unittest
from datetime import UTC, date, datetime

from hypothesis import given
from hypothesis import strategies as st
from mcp.server.mcpserver.exceptions import ToolError

from chitty.errors import ChittyError
from chitty.model import new_task
from chitty.store import Edit, check_edit
from tests.test_cli import CliTestCase
from tests.test_mcp import call

SOURCE = st.sampled_from(("doing", "review"))
TEXT = st.text(alphabet="abc xyzé中", min_size=1, max_size=30).filter(
    lambda text: bool(text.strip())
)


def task_for_return(source, criteria, owner):
    return new_task(
        "Return ticket",
        date(2026, 1, 1),
        "Original description.",
        criteria,
        {"status": source, **({"owner": owner} if owner else {})},
    ).with_note("Existing note.")


def return_note(count):
    return "Review failed (design): missing contract; planning must choose it.\n" + "\n".join(
        f"{index}: fail - missing contract" for index in range(1, count + 1)
    )


class TestReturnValidation(unittest.TestCase):
    @given(SOURCE, st.text(), st.text())
    def test_direct_return_to_planning_is_refused(self, source, note, reviewer):
        task = task_for_return(source, [], None)
        with self.assertRaisesRegex(ChittyError, "to-plan"):
            check_edit(task, Edit(status="planning", note=note), reviewer)

    def test_mixed_old_and_new_returns_escalate(self):
        task = task_for_return("doing", [], None)
        when = datetime(2026, 1, 1, tzinfo=UTC)
        task = task.with_history(when, "other", "doing", "planning")
        task = task.with_history(when, "other", "doing", "to-plan")
        result = check_edit(task, Edit(status="to-plan", note="Needs a decision"), "reviewer")
        self.assertEqual((result.status, result.owner), ("blocked", "human"))

    @given(
        SOURCE,
        st.lists(TEXT, max_size=4),
        st.one_of(st.none(), TEXT),
        st.sampled_from((None, "", " ", "\n\t")),
        st.booleans(),
    )
    def test_blank_reason_is_refused_before_mutation(
        self, source, criteria, owner, reason, repeated
    ):
        task = task_for_return(source, criteria, owner)
        original = task.render()
        edit = (
            Edit(status="to-plan", notes=(() if reason is None else (reason,)))
            if repeated
            else Edit(status="to-plan", note=reason)
        )
        with self.assertRaisesRegex(ChittyError, "to-plan requires --note"):
            check_edit(task, edit, "fresh-reviewer")
        self.assertEqual(task.render(), original)

    @given(SOURCE, st.lists(TEXT, max_size=4), st.one_of(st.none(), TEXT), TEXT, st.booleans())
    def test_return_releases_owner_and_preserves_unrelated_content(
        self, source, criteria, owner, reason, repeated
    ):
        task = task_for_return(source, criteria, owner)
        original = task.render()
        note = reason.strip() + "\n" + return_note(len(criteria))
        edit = (
            Edit(status="to-plan", notes=(note,)) if repeated else Edit(status="to-plan", note=note)
        )
        result = check_edit(task, edit, "fresh-reviewer").apply(task)
        self.assertEqual(result.frontmatter.status, "to-plan")
        self.assertIsNone(result.frontmatter.owner)
        self.assertEqual(result.criteria, task.criteria)
        self.assertIn("Original description.", result.render())
        self.assertIn("Existing note.", result.render())
        self.assertIn(note, result.render())
        self.assertEqual(task.render(), original)

    @given(st.integers(min_value=1, max_value=5), st.sampled_from(("missing", "pass", "duplicate")))
    def test_review_return_requires_complete_failing_verdict(self, count, invalid):
        task = task_for_return("review", ["Criterion"] * count, None)
        note = return_note(count)
        if invalid == "missing":
            note = return_note(count - 1)
        elif invalid == "pass":
            note = note.replace(": fail -", ": pass -")
        else:
            note += "\n1: fail - duplicated"
        with self.assertRaises(ChittyError):
            check_edit(task, Edit(status="to-plan", note=note), "fresh-reviewer")

    def test_reviewer_must_be_independent_but_worker_can_return_own_work(self):
        task = task_for_return("doing", [], "worker").with_history(
            datetime(2026, 1, 1, tzinfo=UTC), "worker", "todo", "doing"
        )
        edit = Edit(status="to-plan", note="Missing contract; planning must choose it.")
        self.assertEqual(check_edit(task, edit, "worker").status, "to-plan")
        task = task.with_field("status", "review").with_history(
            datetime(2026, 1, 1, tzinfo=UTC), "worker", "doing", "review"
        )
        with self.assertRaisesRegex(ChittyError, "cannot review this task"):
            check_edit(task, edit, "worker")


class TestReturnInterfaces(CliTestCase):
    def test_cli_and_mcp_returns_preserve_work_and_expose_planning(self):
        for source in ("doing", "review"):
            for interface in ("cli", "mcp"):
                with self.subTest(source=source, interface=interface):
                    os.environ["CHITTY_ACTOR"] = "worker"
                    ticket = self.json("add", "Return me", "-d", "Original", "--ac", "Contract")[
                        "id"
                    ]
                    self.run_cli("edit", ticket, "-s", "doing", "--owner", "worker")
                    if source == "review":
                        self.run_cli("edit", ticket, "-s", "review")
                        os.environ["CHITTY_ACTOR"] = "reviewer"
                    artifact = self.root / f"{ticket}.txt"
                    artifact.write_text("Partial implementation\n")
                    path = self.json("show", ticket)["path"]
                    before = self.root.joinpath(path).read_text()
                    if interface == "cli":
                        self.run_cli("edit", ticket, "-s", "to-plan", exit_code=1)
                        self.assertEqual(self.root.joinpath(path).read_text(), before)
                        self.run_cli("edit", ticket, "-s", "to-plan", "--note", return_note(1))
                    else:
                        with self.assertRaises(ToolError):
                            call("edit", id=ticket, status="to-plan")
                        self.assertEqual(self.root.joinpath(path).read_text(), before)
                        call("edit", id=ticket, status="to-plan", note=return_note(1))
                    task = self.json("show", ticket)
                    self.assertEqual(task["status"], "to-plan")
                    self.assertIsNone(task["owner"])
                    text = self.root.joinpath(task["path"]).read_text()
                    self.assertIn(f"{source} → to-plan", text)
                    self.assertIn("missing contract", text)
                    self.assertEqual(artifact.read_text(), "Partial implementation\n")
                    self.assertIn(ticket, self.run_cli("list", "-s", "to-plan").stdout)
        self.run_cli("next", exit_code=3)
        self.assertFalse((self.root / ".worktrees").exists())

    def test_invalid_review_verdict_does_not_write(self):
        self.run_cli("add", "Return me", "-d", "Original", "--ac", "Contract")
        self.run_cli("edit", "1", "-s", "review")
        os.environ["CHITTY_ACTOR"] = "reviewer"
        path = self.root.joinpath(self.json("show", "1")["path"])
        before = path.read_text()
        note = "Review failed (design): missing contract"
        self.run_cli("edit", "1", "-s", "to-plan", "--note", note, exit_code=1)
        self.assertEqual(path.read_text(), before)
        with self.assertRaises(ToolError):
            call("edit", id="TASK-1", status="to-plan", note=note)
        self.assertEqual(path.read_text(), before)
