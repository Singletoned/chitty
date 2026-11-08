import subprocess
from pathlib import Path

from chitty.errors import ChittyError
from chitty.run import _land
from chitty.store import NextAction, Repo
from tests.test_cli import CliTestCase


class TestLanding(CliTestCase):
    def setUp(self):
        super().setUp()
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.run_cli("add", "Landing", "-d", "Description.")
        (self.root / ".gitignore").write_text(".worktrees/\n")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "base")
        self.ticket = "TASK-1"
        self.branch = self.ticket.lower()
        self.git("branch", self.branch)
        self.worktree = self.root / ".worktrees" / self.branch
        self.git("worktree", "add", "--quiet", str(self.worktree), self.branch)
        self.main_repo = Repo.open(self.root)

    def git(self, *args: str, cwd: Path | None = None) -> str:
        result = subprocess.run(
            ["git", *args], cwd=cwd or self.root, capture_output=True, text=True, check=True
        )
        return result.stdout

    def finish_ticket(self):
        task = next((self.worktree / "chitty/tasks").glob("TASK-1--*.md"))
        task.write_text(task.read_text().replace("status: todo", "status: done"))
        self.git("add", str(task), cwd=self.worktree)
        self.git("commit", "--quiet", "-m", "finish", cwd=self.worktree)

    def land(self):
        action = NextAction("review", self.main_repo.resolve(self.ticket))
        _land(self.main_repo, self.worktree, action, "true", "true")

    def test_ticket_fast_forwards_main_and_cleans_up(self):
        self.finish_ticket()
        self.land()
        commit = self.git("rev-list", "--parents", "-n", "1", "main").split()
        self.assertEqual(len(commit), 2)
        self.assertIn(
            "status: done", next((self.root / "chitty/tasks").glob("TASK-1--*.md")).read_text()
        )
        self.assertFalse(self.worktree.exists())
        self.assertEqual(self.git("branch", "--list", self.branch), "")

    def test_moved_main_is_merged_into_ticket_branch_before_landing(self):
        self.finish_ticket()
        (self.root / "main-change").write_text("main advanced\n")
        self.git("add", "main-change")
        self.git("commit", "--quiet", "-m", "move main")
        self.land()
        self.assertEqual((self.root / "main-change").read_text(), "main advanced\n")
        self.assertFalse(self.worktree.exists())
        self.assertEqual(self.git("branch", "--list", self.branch), "")

    def test_merge_conflict_keeps_main_unchanged_and_worktree_present(self):
        self.finish_ticket()
        shared = self.worktree / "shared.txt"
        shared.write_text("ticket version\n")
        self.git("add", "shared.txt", cwd=self.worktree)
        self.git("commit", "--quiet", "-m", "ticket shared change", cwd=self.worktree)
        (self.root / "shared.txt").write_text("main version\n")
        self.git("add", "shared.txt")
        self.git("commit", "--quiet", "-m", "main shared change")
        main_head = self.git("rev-parse", "HEAD")
        with self.assertRaisesRegex(ChittyError, "conflicts"):
            self.land()
        self.assertEqual(self.git("rev-parse", "HEAD"), main_head)
        self.assertTrue(self.worktree.exists())

    def test_dirty_main_checkout_refuses_without_changing_history(self):
        self.finish_ticket()
        (self.root / "untracked").write_text("local change")
        main_head = self.git("rev-parse", "HEAD")
        with self.assertRaisesRegex(ChittyError, "working tree is dirty"):
            self.land()
        self.assertEqual(self.git("rev-parse", "HEAD"), main_head)
        self.assertTrue(self.worktree.exists())

    def test_wrong_main_branch_refuses_without_changing_history(self):
        self.finish_ticket()
        self.git("switch", "-c", "not-main")
        main_head = self.git("rev-parse", "HEAD")
        with self.assertRaisesRegex(ChittyError, "must be on branch main"):
            self.land()
        self.assertEqual(self.git("rev-parse", "HEAD"), main_head)
        self.assertTrue(self.worktree.exists())

    def test_dirty_worktree_refuses_without_changing_main(self):
        self.finish_ticket()
        (self.worktree / "untracked").write_text("local change")
        main_head = self.git("rev-parse", "HEAD")
        with self.assertRaisesRegex(ChittyError, "worktree has uncommitted changes"):
            self.land()
        self.assertEqual(self.git("rev-parse", "HEAD"), main_head)
        self.assertTrue(self.worktree.exists())

    def test_ignored_main_file_does_not_prevent_landing(self):
        self.finish_ticket()
        (self.root / ".gitignore").write_text(".worktrees/\nignored.txt\n")
        self.git("add", ".gitignore")
        self.git("commit", "--quiet", "-m", "ignore file")
        (self.root / "ignored.txt").write_text("keep")
        self.land()
        self.assertEqual((self.root / "ignored.txt").read_text(), "keep")
        self.assertFalse(self.worktree.exists())

    def test_failed_landing_check_keeps_main_unchanged(self):
        self.finish_ticket()
        main_head = self.git("rev-parse", "HEAD")
        action = NextAction("review", self.main_repo.resolve(self.ticket))
        with self.assertRaisesRegex(ChittyError, "landing check exited"):
            _land(self.main_repo, self.worktree, action, "true", "false")
        self.assertEqual(self.git("rev-parse", "HEAD"), main_head)
        self.assertTrue(self.worktree.exists())
