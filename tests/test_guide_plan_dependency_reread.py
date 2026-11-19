import unittest
from pathlib import Path

from chitty.store import guide


class TestPlanGuideDependencyReread(unittest.TestCase):
    def test_ticket_built_on_unfinished_work_is_read_again_after_it_lands(self):
        planning = " ".join(guide("plan", directory=Path.cwd()).split())
        for phrase in (
            "builds on what an unfinished ticket adds or changes",
            "stays in `planning`",
            "check this one against what landed, cold-read it again",
            "can go to `todo` with `depends_on`",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, planning)


if __name__ == "__main__":
    unittest.main()
