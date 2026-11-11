import unittest

from click.testing import CliRunner

from chitty.cli import cli
from chitty.store import guide

WARNING = (
    "Backticks run commands inside double-quoted shell arguments, so pass such text "
    "in single quotes. Avoid an apostrophe in the text, or write it as `'\\''`."
)


class TestBacktickGuideWarning(unittest.TestCase):
    def test_warning_is_in_every_generated_guide(self):
        runner = CliRunner()
        for args in ((), ("work",), ("review",), ("plan",)):
            with self.subTest(args=args):
                # Inside Pi, `chitty guide` may append a diagnostic that `guide()` lacks.
                env = {"PI_CODING_AGENT": None}
                result = runner.invoke(cli, ["guide", *args], env=env, catch_exceptions=False)
                self.assertEqual(result.exit_code, 0, result.output)
                self.assertIn(" ".join(WARNING.split()), " ".join(result.stdout.split()))
                self.assertEqual(result.stdout, guide(*args))


if __name__ == "__main__":
    unittest.main()
