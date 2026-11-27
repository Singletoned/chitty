import subprocess
from pathlib import Path

from tests.test_cli import CliTestCase


class TestNewPrefixNumbering(CliTestCase):
    def test_new_tickets_start_at_one_after_prefix_change(self):
        for _ in range(3):
            self.run_cli("add", "Old", "-d", "Text.")
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace('prefix = "TASK"', 'prefix = "TK"'))

        for number in (1, 2):
            result = self.run_cli("add", "New", "-d", "Text.")
            self.assertIn(f"TK-{number}", result.stdout)
        self.assertFalse((self.root / ".git").exists())


class TestOldPrefixes(CliTestCase):
    def setUp(self):
        super().setUp()
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.run_cli("add", "First", "-d", "First description.")
        self.run_cli("add", "Second", "-d", "Main description.")
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace("autocommit = false", "autocommit = true")
            .replace('check = "true"', 'setup = "true"\ncheck = "true"')
        )
        (self.root / ".gitignore").write_text(".worktrees/\n")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "base")
        config.write_text(
            config.read_text().replace('prefix = "TASK"', 'prefix = "TK"\nold_prefixes = ["TASK"]')
        )
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "change prefix")

    def git(self, *args: str, cwd: Path | None = None) -> str:
        return subprocess.run(
            ["git", *args], cwd=cwd or self.root, capture_output=True, text=True, check=True
        ).stdout

    def test_reads_old_ticket_branch(self):
        self.git("branch", "task-2")
        worktree = self.root / ".worktrees/task-2"
        self.git("worktree", "add", "--quiet", str(worktree), "task-2")
        task = next((worktree / "chitty/tasks").glob("TASK-2--*.md"))
        task.write_text(task.read_text().replace("Main description.", "Branch description."))
        self.git("add", str(task), cwd=worktree)
        self.git("commit", "--quiet", "-m", "edit ticket", cwd=worktree)
        self.assertIn("Branch description.", self.run_cli("show", "TASK-2").stdout)

    def test_references_and_dependencies(self):
        self.assertIn("First description.", self.run_cli("show", "TASK-1").stdout)
        ticket = self.json("add", "Planning", "-d", "See TASK-1.", "-s", "planning")["id"]
        self.run_cli("edit", ticket, "--depends-on", "TASK-1")
        result = self.run_cli("edit", ticket, "-s", "todo")
        self.assertIn("TASK-1 todo First", result.stdout)
