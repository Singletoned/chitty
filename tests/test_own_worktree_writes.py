import os
import subprocess

from chitty import ids
from chitty.model import parse
from chitty.store import ChittyError, Repo, StoredTask
from tests.test_cli import CliTestCase


class TestOwnWorktreeWrites(CliTestCase):
    def setUp(self):
        super().setUp()
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace("autocommit = false", "autocommit = true"))
        self.git(self.root, "init", "-b", "main")
        self.git(self.root, "config", "user.email", "test@example.com")
        self.git(self.root, "config", "user.name", "Test")
        self.git(self.root, "add", "--all")
        self.git(self.root, "commit", "-m", "config")
        for number in range(1, 7):
            self.run_cli("add", f"Task {number}", "-d", "Description.")
        self.path = next((self.root / "chitty/tasks").glob("TASK-6--*.md"))
        self.relative = self.path.relative_to(self.root)
        self.worktree = self.tmp / "task-6"
        self.git(self.root, "worktree", "add", "-b", "task-6", str(self.worktree), "main")

    def git(self, cwd, *args):
        return subprocess.run(
            ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
        ).stdout.strip()

    def stored(self, root, branch):
        path = root / self.relative
        return StoredTask(
            ids.parse_filename(path.name)[0], "tasks", path, False, parse(path.read_text()), branch
        )

    def change_main(self):
        self.path.write_text(self.path.read_text().replace("Description.", "Main change."))
        self.git(self.root, "add", str(self.relative))
        self.git(self.root, "commit", "-m", "main change")

    def test_cli_write_then_refuse_after_merge_and_main_change(self):
        before = self.git(self.worktree, "rev-parse", "HEAD")
        os.chdir(self.worktree)
        self.run_cli("edit", "TASK-6", "--note", "x")
        after = self.git(self.worktree, "rev-parse", "HEAD")
        self.assertNotEqual(before, after)
        self.assertIn("x", (self.worktree / self.relative).read_text())
        self.git(self.root, "merge", "--ff-only", "task-6")
        self.change_main()
        result = self.run_cli("edit", "TASK-6", "--note", "x", exit_code=1)
        self.assertIn("latest committed version is on branch main", result.output)
        self.assertEqual(after, self.git(self.worktree, "rev-parse", "HEAD"))

    def test_guard_allows_unchanged_main(self):
        Repo.open(self.worktree)._require_current_version(self.stored(self.worktree, "main"))

    def test_guard_refuses_changed_main(self):
        self.change_main()
        with self.assertRaisesRegex(ChittyError, "branch main"):
            Repo.open(self.worktree)._require_current_version(self.stored(self.worktree, "main"))

    def test_guard_refuses_other_source(self):
        self.git(self.root, "branch", "feature", "main")
        with self.assertRaisesRegex(ChittyError, "branch feature"):
            Repo.open(self.worktree)._require_current_version(self.stored(self.worktree, "feature"))

    def test_guard_refuses_other_checkout(self):
        feature = self.tmp / "feature"
        self.git(self.root, "worktree", "add", "-b", "feature", str(feature), "main")
        with self.assertRaisesRegex(ChittyError, "branch main"):
            Repo.open(feature)._require_current_version(self.stored(feature, "main"))
