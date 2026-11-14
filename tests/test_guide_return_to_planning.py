import unittest

from chitty.run import continuation_prompt
from chitty.store import guide


class TestGuideReturnToPlanning(unittest.TestCase):
    def test_both_roles_route_requirement_problems_to_planning(self):
        for role in ("work", "review"):
            text = " ".join(guide(role).split())
            for phrase in (
                "missing or contradictory requirements or an unresolved design decision",
                "set `-s planning`",
                "what was discovered",
                "why the current ticket cannot guide the work",
                "what decision is needed",
                "Preserve the existing branch and worktree",
                "ownership is cleared",
                "external obstacles requiring help",
            ):
                with self.subTest(role=role, phrase=phrase):
                    self.assertIn(phrase, text)

    def test_worker_keeps_cheap_reversible_choices(self):
        text = " ".join(guide("work").split())
        self.assertIn("For a cheap-to-reverse default, choose it", text)
        self.assertNotIn("what you found and set `-s blocked`", text)

    def test_review_keeps_verdicts_and_work_fix_route(self):
        text = " ".join(guide("review").split())
        self.assertIn("implementation defects against clear requirements", text)
        self.assertIn("Set `-s doing`", text)
        self.assertIn("one line for every criterion", text)
        self.assertIn("Review failed (design):", text)

    def test_continuation_prompts_offer_planning_for_both_roles(self):
        for role in ("work", "review"):
            with self.subTest(role=role):
                text = continuation_prompt(role, "TASK-1")
                self.assertIn("`planning`", text)
                self.assertIn("decision", text)
                self.assertIn("`blocked`", text)
