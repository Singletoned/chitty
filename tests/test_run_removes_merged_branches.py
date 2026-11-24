import shutil
import subprocess

from chitty import locks
from chitty.model import STATUSES
from tests.test_landing import LandingTestCase


class TestRunRemovesMergedBranches(LandingTestCase):
    def run_cleanup(self):
        return self.run_cli("run", "--errors", exit_code=3)

    def exists(self, branch):
        return bool(self.git("branch", "--list", branch).strip())

    def test_removes_done_and_unknown_branches(self):
        self.git("worktree", "remove", str(self.worktree))
        self.git("branch", "-D", self.branch)
        second = self.json("add", "Done too", "-d", "Description.")["id"]
        for ticket in (self.ticket, second):
            task = next((self.root / "chitty/tasks").glob(f"{ticket}--*.md"))
            task.write_text(task.read_text().replace("status: todo", "status: done"))
            self.git("add", str(task))
        self.git("commit", "--quiet", "-m", "finish tickets")
        self.git("branch", second.lower())
        self.git("branch", "task-999")
        self.git("commit", "--allow-empty", "--quiet", "-m", "advance main")
        self.branch = self.ticket.lower()
        self.worktree = self.root / ".worktrees" / self.branch
        self.git("branch", self.branch)
        self.git("worktree", "add", "--quiet", str(self.worktree), self.branch)
        result = self.run_cleanup()
        for branch in (self.branch, second.lower(), "task-999"):
            self.assertFalse(self.exists(branch))
            self.assertIn(f"removed merged branch {branch}", result.stderr)
        self.assertFalse(self.worktree.exists())

    def test_removes_archived_tickets_in_non_done_statuses(self):
        branches = []
        for status in STATUSES:
            if status == "done":
                continue
            ticket = self.json("add", f"Archived {status}", "-d", "Description.", "-s", status)[
                "id"
            ]
            self.run_cli("archive", ticket)
            branch = ticket.lower()
            self.git("branch", branch)
            branches.append(branch)
        result = self.run_cleanup()
        for branch in branches:
            self.assertFalse(self.exists(branch))
            self.assertIn(f"removed merged branch {branch}", result.stderr)

    def test_keeps_non_done_statuses(self):
        tickets = {}
        for status in ("todo", "doing", "review", "error", "blocked"):
            ticket = self.json("add", f"Ticket {status}", "-d", "Description.", "-s", status)["id"]
            tickets[ticket] = status
            self.git("branch", ticket.lower())
        result = self.run_cli("run", "--mode", "review", "--owner", "nobody", exit_code=3)
        for ticket, status in tickets.items():
            self.assertTrue(self.exists(ticket.lower()))
            self.assertIn(
                f"kept merged branch {ticket.lower()}: {ticket} is {status}", result.stderr
            )

    def test_keeps_locked_branch(self):
        self.git("branch", "task-999")
        with locks.run_lock(self.root, "TASK-999", actor="test", mode="work"):
            result = self.run_cleanup()
        self.assertTrue(self.exists("task-999"))
        self.assertIn("kept merged branch task-999: run lock is held", result.stderr)

    def test_keeps_archived_ticket_with_untracked_worktree(self):
        ticket = self.json("add", "Archived planning", "-d", "Description.", "-s", "planning")["id"]
        self.run_cli("archive", ticket)
        branch = ticket.lower()
        self.git("branch", branch)
        worktree = self.root / ".worktrees" / branch
        self.git("worktree", "add", "--quiet", str(worktree), branch)
        (worktree / "untracked.txt").write_text("untracked")
        result = self.run_cleanup()
        self.assertTrue(self.exists(branch))
        self.assertIn(
            f"kept merged branch {branch}: worktree has uncommitted changes",
            result.stderr,
        )

    def test_keeps_untracked_worktree(self):
        self.git("branch", "task-999")
        worktree = self.root / ".worktrees/task-999"
        self.git("worktree", "add", "--quiet", str(worktree), "task-999")
        (worktree / "x.txt").write_text("untracked")
        result = self.run_cleanup()
        self.assertTrue(self.exists("task-999"))
        self.assertIn("kept merged branch task-999:", result.stderr)

    def test_prunes_deleted_worktree(self):
        shutil.rmtree(self.worktree)
        self.run_cleanup()
        self.assertTrue(self.exists(self.branch))

    def test_keeps_invalid_ticket_branch(self):
        self.git("branch", "task-feature-extra")
        result = self.run_cleanup()
        self.assertTrue(self.exists("task-feature-extra"))
        self.assertNotIn("removed merged branch task-feature-extra", result.stderr)

    def test_keeps_ahead_non_ticket_and_remote(self):
        self.git("branch", "feature")
        self.git("update-ref", "refs/remotes/origin/task-999", "main")
        (self.worktree / "ahead").write_text("ahead")
        self.git("add", "ahead", cwd=self.worktree)
        self.git("commit", "--quiet", "-m", "ahead", cwd=self.worktree)
        self.run_cleanup()
        self.assertTrue(self.exists(self.branch))
        self.assertTrue(self.exists("feature"))
        self.assertTrue(self.git("show-ref", "--verify", "refs/remotes/origin/task-999"))

    def conflict(self, command):
        (self.root / "a.txt").write_text("base\n")
        self.git("add", "a.txt")
        self.git("commit", "--quiet", "-m", "base file")
        self.git("merge", "--quiet", "main", cwd=self.worktree)
        (self.worktree / "a.txt").write_text("branch\n")
        self.git("add", "a.txt", cwd=self.worktree)
        self.git("commit", "--quiet", "-m", "branch change", cwd=self.worktree)
        (self.root / "a.txt").write_text("main\n")
        self.git("add", "a.txt")
        self.git("commit", "--quiet", "-m", "main change")
        result = subprocess.run(
            ["git", command, "main"], cwd=self.worktree, capture_output=True, check=False
        )
        self.assertNotEqual(result.returncode, 0)
        self.run_cleanup()
        self.assertTrue(self.exists(self.branch))

    def test_rebase_in_progress(self):
        self.conflict("rebase")

    def test_merge_in_progress(self):
        self.conflict("merge")
