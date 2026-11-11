import re
import unittest
from pathlib import Path

from chitty.cli import guide


class TestReviewGuideEvidence(unittest.TestCase):
    def test_readme_review_example_uses_a_real_newline(self):
        readme = Path(__file__).parents[1] / "README.md"
        text = readme.read_text()
        example = next(line for line in text.splitlines() if "chitty edit 1 -s done --note" in line)
        self.assertIn("$'Reviewed: ready to merge.\\n1: pass", example)
        self.assertNotIn('"Reviewed: ready to merge.\\n1: pass', example)

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
        for phrase in (
            "one line for every criterion",
            "<number>: pass - <evidence>",
            "<number>: fail - <reason>",
            "fails without the change",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
        self.assertNotRegex(text, re.compile(r"\bmake\b"))
