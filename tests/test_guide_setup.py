import unittest
from contextlib import chdir
from tempfile import TemporaryDirectory

from click.testing import CliRunner

from chitty.cli import cli


class TestSetupGuide(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_setup_guide_works_without_a_repository(self):
        with TemporaryDirectory() as tmp, chdir(tmp):
            result = self.runner.invoke(cli, ["guide", "setup"], catch_exceptions=False)
        self.assertEqual(result.exit_code, 0, result.output)

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
