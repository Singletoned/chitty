import unittest
from pathlib import Path

from chitty.store import guide


class TestWorkCommitsGuide(unittest.TestCase):
    def test_implementation_is_committed_before_review(self):
        text = " ".join(guide("work", directory=Path.cwd(), workflow="runner").split())
        for phrase in (
            "Chitty commits ticket-file edits only",
            "code, tests, or other implementation files",
            "runs the configured check and refuses if it fails",
            "Chitty adds a `Task: <ID>` trailer to each commit when it lands the ticket",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
