import unittest

from chitty.store import guide


class TestPlanGuideConvergence(unittest.TestCase):
    def test_module_tests_start_with_importable_stubs(self):
        planning = " ".join(guide("plan").split())
        self.assertIn("names the tests import", planning)
        self.assertIn("NotImplementedError", planning)

    def test_ticket_reads_share_a_fixed_mutant_list(self):
        planning = " ".join(guide("plan").split())
        self.assertIn("same fixed list of mutants", planning)
        self.assertIn("survivors you fixed", planning)

    def test_crowded_criteria_are_split(self):
        planning = " ".join(guide("plan").split())
        self.assertIn("more than about five separate checks", planning)
        self.assertIn("Split a ticket", planning)


if __name__ == "__main__":
    unittest.main()
