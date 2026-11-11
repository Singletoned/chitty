from tests.test_cli import CliTestCase

TICKET = """---
title: x
status: todo
created: 2026-11-11
---

## Description

Written directly by a test.
"""


class TestAlphanumericIds(CliTestCase):
    def setUp(self):
        super().setUp()
        config = self.root / "chitty.toml"
        config.write_text(config.read_text() + '\n[contexts.backlog]\nprefix = "BACKLOG"\n')
        directory = self.root / "chitty" / "backlog"
        directory.mkdir(parents=True)
        (directory / "BACKLOG-K3F9X2AB--x.md").write_text(TICKET)

    def test_show_edit_and_dependency_accept_suffix(self):
        shown = self.json("show", "backlog-k3f9x2ab")
        self.assertEqual(shown["id"], "BACKLOG-K3F9X2AB")
        self.run_cli("note", "backlog-k3f9x2ab", "Looked at it.")
        self.run_cli(
            "add",
            "Dependent",
            "-c",
            "tasks",
            "-d",
            "x",
            "--depends-on",
            "backlog-k3f9x2ab",
        )
        self.run_cli("check")

    def test_order_check_and_add_ignore_alphanumeric_for_allocation(self):
        (self.root / "chitty" / "backlog" / "BACKLOG-12--x.md").write_text(TICKET)
        self.run_cli("check")
        listed = self.run_cli("list", "-c", "backlog").stdout
        self.assertLess(listed.index("BACKLOG-12"), listed.index("BACKLOG-K3F9X2AB"))
        self.run_cli("add", "Next", "-c", "backlog", "-s", "backlog")
        self.run_cli("check")

    def test_show_reports_updated_invalid_id_error(self):
        result = self.run_cli("show", "backlog-013", exit_code=1)
        self.assertIn("expected PREFIX-N or PREFIX-SUFFIX", result.stderr)
