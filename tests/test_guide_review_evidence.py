import re
import unittest

from chitty.cli import guide


class TestReviewGuideEvidence(unittest.TestCase):
    def test_review_guide_requires_evidence_for_failures(self):
        text = " ".join(guide("review").split())
        for phrase in (
            "A criterion is unmet if nothing exercises it",
            "A ticket that is itself wrong also fails",
            "must be run first",
            "Reasoning alone demonstrates nothing",
            "file a ticket instead of failing",
            "earliest stage that should have caught it",
            "If you ran code, the note gives what was run and what it printed",
            "says what is missing or wrong",
            "what stopped you",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
        self.assertIn("Review failed (<cause>):", text)
        self.assertIn("--uncheck", text)
        self.assertIn("-s doing", text)
        self.assertNotIn("such as a throwaway failing test", text)
        self.assertNotRegex(text, re.compile(r"\bmake\b"))
