import unittest
from pathlib import Path


class TestReviewGuideEvidence(unittest.TestCase):
    def test_readme_review_example_uses_a_real_newline(self):
        readme = Path(__file__).parents[1] / "README.md"
        text = readme.read_text()
        example = next(line for line in text.splitlines() if "chitty edit 1 -s done --note" in line)
        self.assertIn("$'Reviewed: ready to merge.\\n1: pass", example)
        self.assertNotIn('"Reviewed: ready to merge.\\n1: pass', example)
