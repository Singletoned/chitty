from tests.test_cli import CliTestCase

TICKET = (
    "---\ntitle: {title}\nstatus: {status}\ncreated: 2026-11-11\n{extra}---\n"
    "\n## Description\n\nx\n"
)


class TestUnconfiguredDirectories(CliTestCase):
    def write_ticket(self, path: str, title: str, status: str = "todo", extra: str = "") -> None:
        file = self.root / "chitty" / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(TICKET.format(title=title, status=status, extra=extra))

    def test_finds_directory_that_exists_only_in_branch_history(self):
        import subprocess

        def git(*args):
            subprocess.run(
                ["git", *args],
                cwd=self.root,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        git("init", "--quiet", "-b", "main")
        git("config", "user.email", "test@example.com")
        git("config", "user.name", "Test")
        git("add", "chitty.toml")
        git("commit", "--quiet", "-m", "setup")
        git("switch", "--quiet", "-c", "ticket")
        self.write_ticket("other/OTHER-1--x.md", "x")
        git("add", "chitty/other/OTHER-1--x.md")
        git("commit", "--quiet", "-m", "ticket")
        git("switch", "--quiet", "main")

        self.assertIn("OTHER-1", self.run_cli("show", "OTHER-1").stdout)

    def test_show_and_list_find_tickets_in_a_directory_without_a_context(self):
        self.write_ticket("other/OTHER-1--x.md", "x")
        self.write_ticket("other/archive/OTHER-2--y.md", "y", status="done")
        self.assertIn("OTHER-1", self.run_cli("show", "OTHER-1").stdout)
        self.assertIn("OTHER-2", self.run_cli("show", "OTHER-2").stdout)
        self.assertIn("OTHER-1", self.run_cli("list").stdout)

    def test_configured_directory_accepts_ticket_with_another_prefix(self):
        self.write_ticket("tasks/OTHER-1--one.md", "One")
        self.assertIn("OTHER-1", self.run_cli("show", "OTHER-1").stdout)
        self.run_cli("check")

    def test_dependency_check_next_and_write_error(self):
        self.write_ticket("other/OTHER-1--one.md", "One")
        self.write_ticket("tasks/TASK-1--two.md", "Two", extra="depends_on:\n  - OTHER-1\n")
        self.run_cli("check")
        result = self.run_cli("next", exit_code=3)
        self.assertNotIn("TASK-1", result.stdout)
        self.assertNotIn("dependency", result.stderr.lower())
        edit = self.run_cli("edit", "OTHER-1", "-s", "doing", exit_code=1)
        self.assertIn("other", edit.stderr)
        self.assertNotIn("Traceback", edit.stderr)

    def test_check_reports_duplicate_ids_across_directories(self):
        self.write_ticket("other/OTHER-1--x.md", "One")
        self.write_ticket("more/OTHER-1--x.md", "One")
        result = self.run_cli("check", exit_code=1)
        self.assertIn("chitty/other/OTHER-1--x.md", result.stdout + result.stderr)
        self.assertIn("chitty/more/OTHER-1--x.md", result.stdout + result.stderr)
