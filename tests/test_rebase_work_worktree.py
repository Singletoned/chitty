import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from chitty import git
from chitty.errors import ChittyError
from chitty.ids import TaskId
from chitty.run import _rebase_work_worktree


class RebaseWorkWorktreeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.worktree = self.root / "worktree"
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.com")
        for name in ("a.txt", "b.txt"):
            (self.repo / name).write_text("original\n")
        self.git("add", ".")
        self.git("commit", "-m", "initial")

    def git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.repo, check=True, capture_output=True, text=True
        ).stdout

    def fixture(self, conflict=False):
        self.git("branch", "task-1")
        self.git("worktree", "add", str(self.worktree), "task-1")
        (self.worktree / ("a.txt" if conflict else "b.txt")).write_text("branch\n")
        subprocess.run(
            ["git", "commit", "-am", "branch"], cwd=self.worktree, check=True, capture_output=True
        )
        (self.repo / "a.txt").write_text("main\n")
        self.git("commit", "-am", "main")

    def rebase(self):
        _rebase_work_worktree(self.worktree, TaskId("TASK", 1), "main")

    def assert_rebased(self):
        self.git("merge-base", "--is-ancestor", "main", "task-1")
        self.assertEqual(len(self.git("rev-list", "main..task-1").splitlines()), 1)

    def assert_no_ref(self):
        self.assertEqual(self.git("for-each-ref", "refs/chitty/stash/TASK-1"), "")

    def test_clean(self):
        self.fixture()
        self.rebase()
        self.assert_rebased()

    def test_saved_work(self):
        self.fixture()
        for name in ("b.txt", "s.txt", "u.txt"):
            (self.worktree / name).write_text(name)
        subprocess.run(["git", "add", "s.txt"], cwd=self.worktree, check=True)
        self.rebase()
        self.assert_rebased()
        for name in ("b.txt", "s.txt", "u.txt"):
            self.assertEqual((self.worktree / name).read_text(), name)
        self.assert_no_ref()

    def test_conflict(self):
        self.fixture(conflict=True)
        tip = self.git("rev-parse", "task-1")
        (self.worktree / "u.txt").write_text("untracked")
        self.rebase()
        self.assertFalse(git.rebase_in_progress(self.worktree))
        self.assertEqual(self.git("rev-parse", "task-1"), tip)
        self.assertEqual((self.worktree / "u.txt").read_text(), "untracked")
        self.assert_no_ref()

    def test_failure(self):
        self.fixture()
        (self.worktree / "u.txt").write_text("untracked")
        with (
            patch("chitty.run.git.rebase_onto", side_effect=ChittyError("boom")),
            self.assertRaisesRegex(ChittyError, "boom"),
        ):
            self.rebase()
        self.assertEqual((self.worktree / "u.txt").read_text(), "untracked")
        self.assert_no_ref()
