from chitty.cli import _columns
from tests.test_cli import CliTestCase


class TestListUntestable(CliTestCase):
    def test_untestable_owner_has_distinct_marker_without_shifting_titles(self):
        self.run_cli("add", "Untestable ticket", "-d", "description", "--owner", "untestable")
        self.run_cli("add", "Alice ticket", "-d", "description", "--owner", "alice")

        lines = self.run_cli("list").stdout.splitlines()

        self.assertIn("🙋", lines[0])
        self.assertIn("👤", lines[1])
        self.assertEqual(
            _columns(lines[0][: lines[0].index("Untestable ticket")]),
            _columns(lines[1][: lines[1].index("Alice ticket")]),
        )
