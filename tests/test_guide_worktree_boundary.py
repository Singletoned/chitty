import unittest

from chitty.store import guide


class TestWorktreeBoundaryGuide(unittest.TestCase):
    def test_work_and_review_guides_define_worktree_boundary(self):
        for role in ("work", "review"):
            with self.subTest(role=role):
                text = " ".join(guide(role, "TASK-254").split()).lower()
                self.assertIn("read and change only files inside the ticket", text)
                self.assertIn("including scratch files", text)
                self.assertIn(
                    "do not touch the main checkout, other worktrees or "
                    "files elsewhere on the machine",
                    text,
                )
                self.assertIn("reading other branches through git or `chitty` is fine", text)
