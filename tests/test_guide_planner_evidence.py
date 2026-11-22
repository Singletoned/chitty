import unittest
from pathlib import Path

from chitty.store import guide


class TestPlannerEvidence(unittest.TestCase):
    def setUp(self):
        self.planning = " ".join(guide("plan", directory=Path.cwd(), workflow="runner").split())

    def test_existing_code_uses_wrong_versions_not_a_stub(self):
        self.assertIn("a stub cannot show the tests fail", self.planning)
        self.assertIn("plausible wrong versions of the code", self.planning)

    def test_wrong_versions_are_committed_tests(self):
        self.assertIn("commit each wrong version as a test", self.planning)
        self.assertNotIn("record in a note which test failed", self.planning)

    def test_recipes_are_probed_against_existing_code(self):
        self.assertIn("run each specified generator recipe against it", self.planning)

    def test_distractors_come_from_the_drawn_value(self):
        self.assertIn("from the drawn value itself", self.planning)

    def test_status_changes_with_the_text_it_depends_on(self):
        self.assertIn("in the same edit command as the text", self.planning)


if __name__ == "__main__":
    unittest.main()
