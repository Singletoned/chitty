import os
import subprocess

from chitty.model import STATUSES
from chitty.store import Edit, Repo
from tests.test_cli import CliTestCase


class TestLeaveDoingClean(CliTestCase):
    def setUp(self):
        super().setUp()
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace("autocommit = false", "autocommit = true"))
        self.git("init", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.git("add", "--all")
        self.git("commit", "-m", "setup")
        self.run_cli("add", "One", "-d", "x", "-s", "todo")
        self.run_cli("edit", "TASK-1", "-s", "doing")
        self.worktree = self.root / ".worktrees" / "task-1"

    def git(self, *args, cwd=None):
        return subprocess.run(
            ["git", *args], cwd=cwd or self.root, check=True, capture_output=True, text=True
        ).stdout.strip()

    def make_worktree(self):
        self.git("worktree", "add", "-b", "task-1", str(self.worktree), "main")
        os.chdir(self.worktree)

    def dirty(self):
        (self.worktree / "left.py").write_text("work in progress\n")

    def test_refuses_dirty_transition(self):
        for status in STATUSES:
            if status in ("doing", "review", "done"):
                continue
            with self.subTest(status=status):
                self.make_worktree()
                try:
                    self.dirty()
                    head = self.git("rev-parse", "HEAD", cwd=self.worktree)
                    result = self.run_cli(
                        "edit", "TASK-1", "-s", status, "--note", "reason", exit_code=1
                    )
                    self.assertIn("`left.py`", result.output)
                    self.assertIn("uncommitted changes", result.output)
                    self.assertEqual(self.git("rev-parse", "HEAD", cwd=self.worktree), head)
                    shown = self.run_cli("show", "TASK-1").output
                    self.assertIn("status: doing", shown)
                    self.assertNotIn("reason", shown)
                finally:
                    os.chdir(self.root)
                    self.git("worktree", "remove", "--force", str(self.worktree))
                    self.git("branch", "-D", "task-1")

    def test_clean_transition(self):
        self.make_worktree()
        self.run_cli("edit", "TASK-1", "-s", "todo")
        self.assertIn("status: todo", self.run_cli("show", "TASK-1").output)

    def test_note_only_when_dirty(self):
        self.make_worktree()
        self.dirty()
        self.run_cli("edit", "TASK-1", "--note", "reason")
        self.assertIn("reason", self.run_cli("show", "TASK-1").output)

    def test_transition_from_todo_when_dirty(self):
        self.make_worktree()
        self.run_cli("edit", "TASK-1", "-s", "todo")
        self.dirty()
        self.run_cli("edit", "TASK-1", "-s", "planning")
        self.assertIn("status: planning", self.run_cli("show", "TASK-1").output)

    def test_main_checkout_when_dirty(self):
        (self.root / "scratch.txt").write_text("scratch\n")
        self.run_cli("edit", "TASK-1", "-s", "planning", "--note", "reason")
        self.assertIn("status: planning", self.run_cli("show", "TASK-1").output)

    def test_runner_edit_when_dirty(self):
        self.make_worktree()
        self.dirty()
        repo = Repo.open(self.worktree)
        repo.edit(
            repo.resolve("TASK-1"),
            Edit(status="error", note="runner", skip_verdicts=True, skip_current_version=True),
        )
        self.assertIn("status: error", self.run_cli("show", "TASK-1").output)
