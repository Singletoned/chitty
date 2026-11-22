from pathlib import Path

from chitty.store import guide
from tests.test_cli import CliTestCase


class TestRepairMissingBranchGuide(CliTestCase):
    def test_repair_guide_explains_missing_branch_recovery(self):
        flattened = " ".join(
            guide("repair", "TASK-1", directory=Path.cwd(), workflow="runner").split()
        )

        for phrase in ("if they exist", "was missing", "exactly this ID", "say what was searched"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, flattened)
