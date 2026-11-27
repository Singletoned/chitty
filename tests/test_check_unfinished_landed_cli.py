import os
import subprocess
from pathlib import Path

from tests.test_cli import CliTestCase


class TestUnfinishedLandedCli(CliTestCase):
    def setUp(self):
        super().setUp()
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.git("branch", "-M", "main")
        self.run_cli("add", "Task", "-d", "Describe.")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "base")

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=self.root, check=True, capture_output=True, text=True
        ).stdout.strip()

    def commit_work(self, message: str = "Implement task\n\nTask: TASK-1") -> str:
        source = self.root / "src/x.py"
        source.parent.mkdir(exist_ok=True)
        source.write_text("pass\n")
        self.git("add", "src/x.py")
        self.git("commit", "--quiet", "-m", message)
        return self.git("rev-parse", "HEAD")

    def test_warns_on_main_for_unfinished_landed_work(self):
        sha = self.commit_work()
        result = self.run_cli("check")
        self.assertIn(
            f"commit {sha[:10]} on main has work for TASK-1, which is todo", result.output
        )
        self.assertIn("TASK-1--task.md: warning:", result.output)

    def test_no_warning_for_ticket_only_commit(self):
        self.run_cli("edit", "1", "--note", "Update.")
        self.git("add", "chitty/tasks/TASK-1--task.md")
        self.git("commit", "--quiet", "-m", "Update\n\nTask: TASK-1")
        self.assertNotIn("has work for TASK-1", self.run_cli("check").output)

    def test_no_warning_for_chitty_commit(self):
        self.commit_work("chitty: update\n\nTask: TASK-1")
        self.assertNotIn("has work for TASK-1", self.run_cli("check").output)

    def test_no_warning_for_archived_ticket(self):
        self.commit_work()
        self.run_cli("archive", "1")
        self.assertNotIn("has work for TASK-1", self.run_cli("check").output)

    def test_no_warning_in_linked_worktree(self):
        self.commit_work()
        worktree = self.tmp / "task-1"
        self.git("worktree", "add", "--quiet", "-b", "task-1", str(worktree))
        self.addCleanup(self.git, "worktree", "remove", "--force", str(worktree))
        previous = Path.cwd()
        try:
            os.chdir(worktree)
            self.assertNotIn("has work for TASK-1", self.run_cli("check").output)
        finally:
            os.chdir(previous)
