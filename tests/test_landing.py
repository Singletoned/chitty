import os
import shutil
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from chitty.errors import ChittyError
from chitty.run import _land, _land_pending
from chitty.store import NextAction, Repo
from tests.test_cli import CliTestCase


class TestLanding(CliTestCase):
    def setUp(self):
        super().setUp()
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.run_cli("add", "Landing", "-d", "Description.")
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace("autocommit = false", "autocommit = true")
            .replace('check = "true"', 'setup = "true"\ncheck = "true"')
        )
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

    def test_missing_ticket_branch_is_noop_even_when_main_is_dirty(self):
        self.finish_ticket()
        self.git("worktree", "remove", str(self.worktree))
        self.git("branch", "-D", self.branch)
        (self.root / "untracked").write_text("local change")

        self.land()

        self.assertTrue((self.root / "untracked").exists())

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

    def test_pending_tickets_land_in_order_one_per_run(self):
        self.finish_ticket()
        self.run_cli("add", "Second", "-d", "Description.")
        second = self.root / ".worktrees" / "task-2"
        self.git("worktree", "add", "--quiet", "-b", "task-2", str(second))
        task = next((second / "chitty/tasks").glob("TASK-2--*.md"))
        task.write_text(task.read_text().replace("status: todo", "status: done"))
        self.git("add", str(task), cwd=second)
        self.git("commit", "--quiet", "-m", "finish second", cwd=second)

        first = _land_pending(self.main_repo)
        assert first is not None

        self.assertEqual(str(first.action.id), "TASK-1")
        self.assertFalse(self.worktree.exists())
        self.assertTrue(second.exists())
        later = _land_pending(Repo.open(self.root))
        assert later is not None
        self.assertEqual(str(later.action.id), "TASK-2")
        self.assertFalse(second.exists())

    def test_pending_landing_failure_stops_before_later_ticket(self):
        self.finish_ticket()
        self.run_cli("add", "Second", "-d", "Description.")
        second = self.root / ".worktrees" / "task-2"
        self.git("worktree", "add", "--quiet", "-b", "task-2", str(second))
        task = next((second / "chitty/tasks").glob("TASK-2--*.md"))
        task.write_text(task.read_text().replace("status: todo", "status: done"))
        self.git("add", str(task), cwd=second)
        self.git("commit", "--quiet", "-m", "finish second", cwd=second)
        git_dir = self.git("-C", str(self.worktree), "rev-parse", "--git-dir").strip()
        (self.worktree / git_dir / "rebase-merge").mkdir(parents=True)

        with self.assertRaisesRegex(ChittyError, "unfinished"):
            _land_pending(self.main_repo)

        self.assertTrue(second.exists())
        shutil.rmtree(self.worktree / git_dir / "rebase-merge")
        landed = _land_pending(self.main_repo)
        assert landed is not None
        self.assertEqual(str(landed.action.id), "TASK-1")

    def test_run_lands_pending_before_agent_and_next_run_selects_work(self):
        self.run_cli("add", "Next", "-d", "Description.")
        self.run_cli("init")
        self.git("add", "chitty.toml", "AGENTS.md", "CLAUDE.md")
        self.git("commit", "--quiet", "-m", "setup")
        self.git("merge", "--quiet", "main", cwd=self.worktree)
        self.finish_ticket()
        fake = self.tmp / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import pathlib, subprocess\n"
            "task = pathlib.Path('chitty/tasks/TASK-2--next.md')\n"
            "task.write_text(task.read_text().replace('status: doing', 'status: blocked'))\n"
            "subprocess.run(['git', 'add', str(task)], check=True)\n"
            "subprocess.run(['git', 'commit', '--quiet', '-m', 'agent'], check=True)\n"
        )
        fake.chmod(fake.stat().st_mode | 0o100)
        previous = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake.parent}:{previous}"
        try:
            first = self.run_cli("run")
            self.assertEqual(first.stdout, "landed TASK-1\nTASK-1: done → done\n")
            second = self.run_cli("run")
        finally:
            os.environ["PATH"] = previous
        self.assertEqual(second.stdout, "TASK-2: doing → blocked\n")

    def test_pending_landing_failure_is_completed_by_a_later_run(self):
        self.finish_ticket()
        self.run_cli("init")
        self.git("add", "chitty.toml", "AGENTS.md", "CLAUDE.md")
        self.git("commit", "--quiet", "-m", "setup")
        self.git("merge", "--quiet", "main", cwd=self.worktree)
        (self.worktree / "uncommitted").write_text("block landing")

        failed = self.run_cli("run", exit_code=1)
        self.assertIn("worktree has uncommitted changes", failed.stderr)
        self.assertTrue(self.worktree.exists())

        (self.worktree / "uncommitted").unlink()
        retried = self.run_cli("run")
        self.assertIn("landed TASK-1", retried.stdout)
        self.assertFalse(self.worktree.exists())

    def test_failed_worktree_removal_is_retried_after_removal_cause_is_fixed(self):
        self.finish_ticket()
        action = NextAction("review", self.main_repo.resolve(self.ticket))
        with (
            patch("chitty.run.git.remove_worktree", side_effect=ChittyError("remove failed")),
            self.assertRaisesRegex(ChittyError, "remove failed"),
        ):
            _land(self.main_repo, self.worktree, action, "true", "true")
        self.assertTrue(self.worktree.exists())
        self.land()
        self.assertFalse(self.worktree.exists())

    def test_failed_landing_check_keeps_main_unchanged(self):
        self.finish_ticket()
        main_head = self.git("rev-parse", "HEAD")
        action = NextAction("review", self.main_repo.resolve(self.ticket))
        with self.assertRaisesRegex(ChittyError, "landing check exited"):
            _land(self.main_repo, self.worktree, action, "true", "false")
        self.assertEqual(self.git("rev-parse", "HEAD"), main_head)
        self.assertTrue(self.worktree.exists())
