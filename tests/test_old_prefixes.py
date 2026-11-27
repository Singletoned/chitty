from tests.test_cli import CliTestCase


class TestOldPrefixes(CliTestCase):
    def test_new_tickets_start_at_one_after_prefix_change(self):
        for _ in range(3):
            self.run_cli("add", "Old", "-d", "Text.")
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace('prefix = "TASK"', 'prefix = "TK"'))

        for number in (1, 2):
            result = self.run_cli("add", "New", "-d", "Text.")
            self.assertIn(f"TK-{number}", result.stdout)
        self.assertFalse((self.root / ".git").exists())
