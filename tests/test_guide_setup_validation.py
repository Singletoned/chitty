import unittest
from contextlib import chdir
from tempfile import TemporaryDirectory

from click.testing import CliRunner

from chitty.cli import cli


def _flat(text: str) -> str:
    return " ".join(text.split())


class TestSetupGuideValidation(unittest.TestCase):
    def test_setup_guide_validates_setup_in_a_throwaway_worktree(self):
        with TemporaryDirectory() as tmp, chdir(tmp):
            result = CliRunner().invoke(cli, ["guide", "setup"], catch_exceptions=False)
        self.assertEqual(result.exit_code, 0, result.output)
        text = _flat(result.stdout)
        for phrase in (
            "throwaway detached worktree",
            "run the configured `setup` and `check` commands",
            "without `chitty run`",
            "Before declaring the runner ready",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_setup_guide_bootstraps_targets_for_the_first_ticket(self):
        with TemporaryDirectory() as tmp, chdir(tmp):
            result = CliRunner().invoke(cli, ["guide", "setup"], catch_exceptions=False)
        self.assertEqual(result.exit_code, 0, result.output)
        text = _flat(result.stdout)
        for phrase in (
            "first ticket creates the real setup and check targets",
            "commit placeholder targets",
            "replace them",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
