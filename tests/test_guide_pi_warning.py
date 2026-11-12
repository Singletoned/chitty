import unittest

from click.testing import CliRunner

from chitty.cli import cli

WARNING = "Pi needs Chitty's extension"


class TestGuidePiWarning(unittest.TestCase):
    def guide(self, env: dict[str, str | None]) -> str:
        result = CliRunner().invoke(cli, ["guide"], env=env, catch_exceptions=False)
        self.assertEqual(result.exit_code, 0, result.output)
        return result.stdout

    def test_pi_without_extension_or_actor_is_warned(self):
        env = {"PI_CODING_AGENT": "true", "CHITTY_PI_SESSION_ID": None, "CHITTY_ACTOR": None}
        self.assertIn(WARNING, self.guide(env))

    def test_pi_with_actor_set_is_not_warned(self):
        # `chitty run` sets CHITTY_ACTOR for print-mode Pi, which has no extension.
        env = {"PI_CODING_AGENT": "true", "CHITTY_PI_SESSION_ID": None, "CHITTY_ACTOR": "x"}
        self.assertNotIn(WARNING, self.guide(env))


if __name__ == "__main__":
    unittest.main()
