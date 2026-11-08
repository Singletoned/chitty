import unittest

from click.testing import CliRunner

from chitty.cli import cli
from chitty.store import guide


def _flat(text: str) -> str:
    return " ".join(text.split())


class TestColdReadGuide(unittest.TestCase):
    def run_cli(self, *args: str) -> str:
        result = CliRunner().invoke(cli, list(args), catch_exceptions=False)
        self.assertEqual(result.exit_code, 0, result.output)
        return result.stdout

    def test_prints_the_reader_procedure(self):
        output = _flat(self.run_cli("guide", "cold-read"))
        for phrase in (
            "git worktree add --detach .worktrees/read-<ID>",
            "UV_PROJECT_ENVIRONMENT",
            "Run no Chitty writes",
            "should fail does fail, before implementing",
            "rather than assume",
            "git update-ref refs/cold-read/<ID>/<n> HEAD",
            "git worktree remove --force .worktrees/read-<ID>",
            "nothing to run",
            "the exact wording to change",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, output)

    def test_names_the_ticket_first(self):
        self.assertEqual(
            self.run_cli("guide", "cold-read", "TASK-1"),
            f"Work only on Chitty ticket TASK-1.\n\n{guide('cold-read')}",
        )

    def test_plan_guide_points_at_the_reader_guide(self):
        planning = _flat(guide("plan"))
        self.assertIn("chitty guide cold-read <ID>", planning)
        self.assertNotIn("git update-ref refs/cold-read", planning)


if __name__ == "__main__":
    unittest.main()
