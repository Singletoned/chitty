import unittest
from pathlib import Path

from chitty.store import guide


class TestPlanGuideDependencyReread(unittest.TestCase):
    def test_ticket_built_on_unfinished_work_is_read_again_after_it_lands(self):
        planning = " ".join(guide("plan", directory=Path.cwd(), workflow="runner").split())
        for phrase in (
            "relies on something an unfinished ticket is building",
            "keep it in `planning`",
            "compare this one with what actually landed, cold-read it again",
            "`depends_on` is enough",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, planning)


if __name__ == "__main__":
    unittest.main()
