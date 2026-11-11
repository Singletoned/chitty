import unittest
from contextlib import chdir
from tempfile import TemporaryDirectory

from click.testing import CliRunner

from chitty.cli import cli


def _flat(text: str) -> str:
    return " ".join(text.split())


class TestSetupGuide(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_setup_guide_works_without_a_repository(self):
        with TemporaryDirectory() as tmp, chdir(tmp):
            result = self.runner.invoke(cli, ["guide", "setup"], catch_exceptions=False)
        self.assertEqual(result.exit_code, 0, result.output)
        text = _flat(result.stdout)
        for phrase in (
            "main checkout",
            "chitty init",
            "chitty.toml",
            "[tool.chitty]",
            "pyproject.toml",
            "autocommit = true",
            "setup =",
            "check =",
            "agent_command =",
            "[agent_commands]",
            "[tool.chitty.agent_commands]",
            "PI_CODING_AGENT_DIR",
            "chitty run --agent NAME",
            "{mode}",
            "{id}",
            "{prompt}",
            "ticket worktree",
            "chitty run --ticket ID",
            "not a dry run",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_setup_is_not_ticket_specific(self):
        result = self.runner.invoke(cli, ["guide", "setup", "TASK-1"])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("does not take a ticket ID", result.output)

    def test_guide_help_names_roles_and_how_to_use_them(self):
        output = self.runner.invoke(cli, ["guide", "--help"]).output
        for example in (
            "chitty guide",
            "chitty guide setup",
            "chitty guide work TASK-12",
            "chitty guide review TASK-12",
            "chitty guide plan",
            "chitty guide cold-read TASK-12",
        ):
            with self.subTest(example=example):
                self.assertIn(example, output)


if __name__ == "__main__":
    unittest.main()
