import unittest
from pathlib import Path

from chitty.store import guide


class TestGuideReturnToPlanning(unittest.TestCase):
    def test_roles_explain_return_routing_and_note_shape(self):
        for role in ("work", "review"):
            with self.subTest(role=role):
                text = " ".join(guide(role).split())
                self.assertIn("missing or contradictory", text)
                self.assertIn("discovery, problem and decision needed", text)
                self.assertIn("preserves committed", text)
                self.assertIn("cold-read", text)
                self.assertIn("external obstacle", text)

    def test_public_docs_explain_return_routing(self):
        for path in ("README.md", "docs/plan/pipeline-and-feedback.md"):
            text = Path(path).read_text()
            with self.subTest(path=path):
                self.assertTrue("contradictory" in text or "unclear requirements" in text)
                self.assertIn("preserves", text)
                self.assertIn("planning", text)


if __name__ == "__main__":
    unittest.main()
