import unittest

from chitty.store import guide


class TestPlanGuide(unittest.TestCase):
    def test_hands_off_only_a_successful_current_ticket_read(self):
        planning = " ".join(guide("plan").split())
        for phrase in (
            "current ticket text",
            "no unresolved serious findings",
            "git diff <main-branch>...refs/cold-read/<ID>/<n>",
            "configured main branch",
            "check it against the current criteria",
            "git update-ref -d refs/cold-read/<ID>/<n>",
            "superseded ticket text",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, planning)


if __name__ == "__main__":
    unittest.main()
