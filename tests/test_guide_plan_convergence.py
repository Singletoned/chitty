import unittest
from pathlib import Path

from chitty.store import guide


class TestPlanGuideConvergence(unittest.TestCase):
    def test_module_tests_start_with_importable_stubs(self):
        planning = " ".join(guide("plan", directory=Path.cwd(), workflow="runner").split())
        self.assertIn("tell its worker to first create it", planning)
        self.assertIn("names the tests import", planning)
        self.assertIn("NotImplementedError", planning)

    def test_read_problems_return_to_planning(self):
        planning = " ".join(guide("plan", directory=Path.cwd(), workflow="runner").split())
        self.assertIn("expected route", planning)
        self.assertIn("return to planning", planning)

    def test_crowded_criteria_are_split(self):
        planning = " ".join(guide("plan", directory=Path.cwd(), workflow="runner").split())
        self.assertIn("more than about five separate checks", planning)
        self.assertIn("Split a ticket", planning)


if __name__ == "__main__":
    unittest.main()
