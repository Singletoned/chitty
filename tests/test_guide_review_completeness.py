import unittest

from chitty.cli import guide


class TestReviewGuideCompleteness(unittest.TestCase):
    def test_complete_inspection_before_verdict(self):
        text = " ".join(guide("review").split())
        for phrase in (
            (
                "Before writing the review note, inspect every acceptance criterion "
                "and the complete diff"
            ),
            "Do not stop at the first defect",
            "whether the changes fit together",
            "useful property-test opportunities",
            "whether the result makes sense to users",
            "The dirty-worktree stop above still applies",
            "report the verification limits and continue the checks you can safely perform",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_all_findings_in_one_note(self):
        text = " ".join(guide("review").split())
        for phrase in (
            "Report all findings from this pass together in that one note",
            "Group actionable findings under the relevant criterion",
            "a criterion may have multiple findings",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_new_discoveries_are_not_prior_process_failures(self):
        text = " ".join(guide("review").split())
        for phrase in (
            "Compare findings with earlier review notes",
            (
                "Distinguish newly discovered findings from previously reported findings "
                "that remain unresolved"
            ),
            "cite the earlier note for unresolved findings",
            "Later passes are expected to discover additional bugs",
            "not evidence of an earlier process failure",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
