import unittest
from pathlib import Path

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

    def test_names_the_ticket_first(self):
        self.assertEqual(
            self.run_cli("guide", "cold-read", "TASK-1"),
            "Work only on Chitty ticket TASK-1.\n\n"
            + guide("cold-read", directory=Path.cwd(), workflow="runner"),
        )


if __name__ == "__main__":
    unittest.main()
