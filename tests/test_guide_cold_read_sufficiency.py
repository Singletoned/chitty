import unittest

from chitty.store import guide


class TestColdReadSufficiencyGuide(unittest.TestCase):
    def assert_phrases(self, role, phrases):
        text = " ".join(guide(role).split())
        for phrase in phrases:
            with self.subTest(role=role, phrase=phrase):
                self.assertIn(phrase, text)

    def test_fresh_reader_implements_literally_and_reports_ambiguities(self):
        self.assert_phrases(
            "cold-read",
            (
                (
                    "Implement the simplest solution the written Description "
                    "and Acceptance Criteria permit"
                ),
                "Examine every criterion individually for vague phrases and bundled behaviours",
                "do not silently add missing requirements",
                (
                    "The original planner uses your implementation and report "
                    "for the sufficiency judgement"
                ),
                "Ambiguities in individual criteria and decisions left to the worker",
            ),
        )

    def test_original_planner_challenges_individual_and_combined_coverage(self):
        self.assert_phrases(
            "plan",
            (
                "In the original planning session, perform a sufficiency read",
                "Inspect the implementing commit, its tests and report",
                "each criterion individually and the ticket as a whole",
                (
                    "could a plausible minimal implementation satisfy the criteria "
                    "yet reasonably fail a good review?"
                ),
                (
                    "For a read with nothing to run, inspect the proposed text, "
                    "referenced code and report instead"
                ),
                "a concrete counterexample",
                "relevant inputs or state",
                "a distinguishing test and observable result",
                "proposed criterion wording",
                "Prefer a general property over accumulating examples",
                "Do not invent speculative features",
            ),
        )

    def test_sufficiency_gaps_are_resolved_before_ready(self):
        self.assert_phrases(
            "plan",
            (
                "Before moving to `todo`, resolve every reader finding and sufficiency gap",
                "strengthen the ticket, split it, or explicitly reject the finding as out of scope",
                "Write requirements needed to reject the implementation into the ticket",
                "not just the planning conversation",
                "Repeat the cold read after fixing a serious finding",
                "fresh stronger reader is optional",
                "uncertainty or repeated work–review failures",
                "not another mandatory session",
            ),
        )
