import unittest

from chitty.store import guide


class TestReviewCleanlinessGuide(unittest.TestCase):
    def test_dirty_review_branch_goes_directly_to_a_human(self):
        text = " ".join(guide("review").split())
        for phrase in (
            "git status --short",
            "uncommitted changes",
            "-s blocked",
            "--owner human",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
