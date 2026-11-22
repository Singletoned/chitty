import unittest
from pathlib import Path

from chitty.run import continuation_prompt
from chitty.store import guide, managed_guide

DEFECT_PHRASES = (
    "missing or contradictory requirements",
    "an unresolved design decision",
    "a wrong claim about the code, files or other tickets",
    "a criterion that cannot be verified as written or would pass with nothing built",
    (
        "a test a criterion needs that the ticket does not describe "
        "(its fixture, action and assertions)"
    ),
    "a ticket too large to finish in one session",
)


class TestGuideReturnScope(unittest.TestCase):
    def test_work_and_review_route_each_ticket_defect_to_planning(self):
        for role in ("work", "review"):
            text = " ".join(guide(role, directory=Path.cwd(), workflow="runner").split())
            for phrase in DEFECT_PHRASES:
                with self.subTest(role=role, phrase=phrase):
                    self.assertIn(phrase, text)
            self.assertIn("set `-s planning`", text)

    def test_continuation_prompts_name_ticket_defects_and_blocked(self):
        for role in ("work", "review"):
            with self.subTest(role=role):
                text = continuation_prompt(role, "TASK-1")
                self.assertIn("a defect in the ticket", text)
                self.assertIn("`blocked`", text)

    def test_runner_guide_routes_each_ticket_defect_to_planning(self):
        text = " ".join(managed_guide("runner").split())
        for phrase in DEFECT_PHRASES:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
