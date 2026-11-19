import unittest
from pathlib import Path

from chitty.store import guide, managed_guide


class TestGuideLiteralStar(unittest.TestCase):
    def test_general_and_role_guides_include_literal_single_asterisk_instruction(self):
        self.assertIn("literal single", managed_guide("tickets"))
        for role in ("work", "review", "plan"):
            with self.subTest(role=role):
                self.assertIn("literal single", guide(role, directory=Path.cwd()))
