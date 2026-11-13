import unittest
from datetime import date

from hypothesis import given
from hypothesis import strategies as st

from chitty.errors import ChittyError
from chitty.model import new_task
from chitty.run import continuation_prompt
from chitty.store import Edit, check_edit
from tests.test_cli import CliTestCase
from tests.test_mcp import call

TEXT = st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=12)


def task(status: str, criteria: list[str], owner: str | None):
    return new_task(
        "Generated task",
        date(2026, 1, 1),
        "Description.",
        criteria,
        {"status": status, **({"owner": owner} if owner else {})},
    )


class TestReturnToPlanningValidation(unittest.TestCase):
    @given(st.sampled_from(("doing", "review")), st.booleans(), st.booleans())
    def test_returns_require_meaningful_note_and_do_not_mutate(self, source, has_note, repeated):
        original = task(source, ["criterion"], "worker")
        note = " discovery, problem, decision " if has_note else "   "
        if source == "review" and has_note:
            note += "\n1: fail - requirements are unclear"
        edit = Edit(
            status="planning",
            note=note if not repeated else None,
            notes=(note,) if repeated else (),
        )
        if has_note:
            returned = check_edit(original, edit, "reviewer")
            self.assertEqual(returned.owner, "")
        else:
            with self.assertRaises(ChittyError):
                check_edit(original, edit, "reviewer")
        self.assertEqual(original.frontmatter.status, source)
        self.assertEqual(original.frontmatter.owner, "worker")

    def test_review_return_requires_failed_verdicts_and_independence(self):
        original = task("review", ["criterion"], "reviewer")
        edit = Edit(status="planning", note="Discovery.\n1: pass - looks good")
        with self.assertRaisesRegex(ChittyError, "at least one fail"):
            check_edit(original, edit, "reviewer")
        self.assertEqual(original.frontmatter.status, "review")


class TestReturnToPlanningInterface(CliTestCase):
    def test_cli_return_preserves_artifacts_and_is_selectable_only_by_planning(self):
        ticket = self.run_cli("add", "Return", "-d", "x", "-s", "todo").output.strip().split()[1]
        self.run_cli("edit", ticket, "-s", "doing", "--owner", "worker")
        self.run_cli(
            "edit", ticket, "-s", "planning", "--note", "Discovery: x\nProblem: y\nDecision: z"
        )
        shown = self.json("show", ticket)
        self.assertEqual(shown["status"], "planning")
        self.assertEqual(shown.get("owner"), None)
        self.assertIn("Discovery: x", shown["notes"])
        self.assertIn(ticket, self.run_cli("list", "-s", "planning").stdout)
        self.run_cli("next", exit_code=3)

    def test_mcp_return_clears_owner_and_rejects_invalid_review(self):
        ticket = self.json("add", "Return MCP", "-d", "x", "-s", "todo")["id"]
        self.run_cli("edit", ticket, "-s", "doing", "--owner", "worker")
        returned = call(
            "edit",
            id=ticket,
            status="planning",
            note="Discovery: x\nProblem: y\nDecision: z",
        )
        self.assertEqual(returned["status"], "planning")
        self.assertIsNone(returned["owner"])

        review = self.json("add", "Review return", "-d", "x", "--ac", "One")["id"]
        self.run_cli("edit", review, "-s", "review")
        before = self.json("show", review)
        with self.assertRaisesRegex(Exception, "missing 1"):
            call("edit", id=review, status="planning", note="Discovery only")
        self.assertEqual(self.json("show", review), before)

    def test_continuation_prompts_offer_planning(self):
        for mode in ("work", "review"):
            with self.subTest(mode=mode):
                self.assertIn("planning", continuation_prompt(mode, "TASK-1"))


if __name__ == "__main__":
    unittest.main()
