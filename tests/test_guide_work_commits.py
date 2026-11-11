import unittest

from chitty.store import guide


class TestWorkCommitsGuide(unittest.TestCase):
    def test_implementation_is_committed_before_review(self):
        text = " ".join(guide("work").split())
        for phrase in (
            "Chitty commits ticket-file edits only",
            "code, tests, or other implementation files",
            "Task: <ID>",
            "git status --short",
            "before moving the ticket to `review`",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
