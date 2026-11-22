import re
import unittest
from pathlib import Path

from chitty.store import guide


class TestReadOnlyColdReadGuide(unittest.TestCase):
    def test_cold_read_is_one_read_only_scan(self):
        text = " ".join(guide("cold-read", directory=Path.cwd(), workflow="runner").split())
        required = (
            "Run no Chitty writes",
            "no worktree, branch, ref or commit",
            "Try behaviour rather than assume",
            "What done means",
            "would change",
            "Ambiguities",
            "Missed properties",
            "Unverified behaviour",
            "Wrong claims",
            "the exact wording to change",
            "Weak tests",
            "outside the checkout",
            "not building it",
        )
        forbidden = (
            "worktree add",
            "worktree remove",
            "update-ref",
            "refs/cold-read",
            "implement it",
            "Implement the simplest",
            "mutant",
            "failed before the fix",
            "UV_PROJECT_ENVIRONMENT",
            "Commit your work",
            "nothing to run",
        )
        for phrase in required:
            with self.subTest(kind="required", phrase=phrase):
                self.assertIn(phrase, text)
        for phrase in forbidden:
            with self.subTest(kind="forbidden", phrase=phrase):
                self.assertNotIn(phrase, text)

    def test_plan_guide_describes_read_only_cold_reads(self):
        text = " ".join(guide("plan", directory=Path.cwd(), workflow="runner").split())
        required = (
            "for its cold read",
            "cheap model",
            "expected route",
            "NotImplementedError",
            "a plausible minimal implementation",
            "must fail without the fix",
        )
        forbidden = (
            "mutant",
            "A read that only probed",
            "until a read finds none",
            "Repeat the cold read",
            "implementing",
            "throwaway worktree",
            "with and without the fix",
            "refs/cold-read",
            "possible starting point",
        )
        for phrase in required:
            with self.subTest(kind="required", phrase=phrase):
                self.assertIn(phrase, text)
        for phrase in forbidden:
            with self.subTest(kind="forbidden", phrase=phrase):
                self.assertNotIn(phrase, text)

    def test_design_cold_read_section_is_read_only(self):
        design = Path("docs/plan/pipeline-and-feedback.md").read_text()
        section = re.search(r"^## Cold read\n(.*?)(?=^## |\Z)", design, re.MULTILINE | re.DOTALL)
        if section is None:
            self.fail("Cold read section is missing")
        text = " ".join(section.group(1).split())
        self.assertIn("read-only", text)
        for phrase in ("refs/cold-read", "mutant", "worktree", "implementing"):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
