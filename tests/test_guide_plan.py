import unittest
from pathlib import Path

from chitty.store import guide


class TestPlanGuide(unittest.TestCase):
    def test_hands_off_only_a_successful_current_ticket_read(self):
        planning = " ".join(guide("plan", directory=Path.cwd(), workflow="runner").split())
        for phrase in (
            "current ticket text",
            "ticket text, the named code and documents",
            "reader report",
            "for its cold read",
            "expected route",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, planning)


if __name__ == "__main__":
    unittest.main()
