import unittest
from unittest.mock import patch

from click.testing import CliRunner

from chitty.cli import cli
from chitty.config import CHITTY_VERSION


class TestVersion(unittest.TestCase):
    def test_runtime_version_comes_from_the_source_package(self):
        from chitty import __version__

        self.assertEqual(CHITTY_VERSION, __version__)

    @patch("importlib.metadata.version", return_value="0.0.0")
    def test_cli_version_uses_running_code_version(self, _version: object) -> None:
        result = CliRunner().invoke(cli, ["--version"], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(result.output, f"chitty, version {CHITTY_VERSION}\n")
