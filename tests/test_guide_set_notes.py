import unittest

from chitty.store import guide


class TestGuideSetNotes(unittest.TestCase):
    def test_plan_guide_recommends_replacing_converged_notes(self):
        text = guide("plan")
        self.assertIn("replace its notes", text)
        self.assertIn("verified facts", text)
        self.assertIn("reviewer checklist", text)
