import unittest
from pathlib import Path

from chitty.store import guide


class TestColdReadSufficiencyGuide(unittest.TestCase):
    def assert_phrases(self, role, phrases):
        text = " ".join(guide(role, directory=Path.cwd(), workflow="runner").split())
        for phrase in phrases:
            with self.subTest(role=role, phrase=phrase):
                self.assertIn(phrase, text)

    def test_reader_reports_ambiguities_and_planner_checks_sufficiency(self):
        self.assert_phrases(
            "cold-read",
            (
                "Work only from its Description and Acceptance Criteria",
                "Ambiguities in individual criteria",
                "exact wording to change",
            ),
        )
        self.assert_phrases(
            "plan",
            (
                "perform a sufficiency read",
                "each criterion individually and the ticket as a whole",
                "a plausible minimal implementation",
                "a concrete counterexample",
                "a distinguishing test and observable result",
                "proposed criterion wording",
            ),
        )

    def test_sufficiency_gaps_are_resolved_before_ready(self):
        self.assert_phrases(
            "plan",
            (
                "resolve every reader finding and sufficiency gap",
                "strengthen the ticket, split it, or explicitly reject",
                "return to planning",
                "A stronger reader remains optional",
                "not mandatory",
            ),
        )


if __name__ == "__main__":
    unittest.main()
