from unittest.mock import patch

from chitty.cli import _columns, _list_width
from tests.test_cli import CliTestCase


class TestListTerminalWidth(CliTestCase):
    def test_list_width(self):
        self.assertEqual(_list_width(100, None), 100)
        self.assertEqual(_list_width(100, 60), 60)
        self.assertEqual(_list_width(100, 200), 100)

    def test_list_fits_terminal(self):
        self.run_cli("add", "x" * 90, "-d", "x")
        with patch("chitty.cli._terminal_columns", return_value=60, create=True):
            line = self.run_cli("list").stdout.splitlines()[0]
        self.assertLessEqual(_columns(line), 60)
        self.assertTrue(line.endswith("…"))
