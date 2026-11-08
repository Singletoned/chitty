import unittest

from chitty.store import guide


class TestGuideLiteralStar(unittest.TestCase):
    def test_general_and_role_guides_include_literal_single_asterisk_instruction(self):
        self.assertIn("literal single", guide())
        for role in ("work", "review", "plan"):
            with self.subTest(role=role):
                self.assertIn("literal single", guide(role))
