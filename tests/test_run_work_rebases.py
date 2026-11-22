import subprocess
from unittest import mock

from chitty.model import ChittyError
from tests.test_review_merge import ReviewMergeTestCase


class TestWorkRebases(ReviewMergeTestCase):
    def setUp(self):
        super().setUp()
        (self.tmp / "setup.py").write_text(
            "import subprocess, sys\n"
            "from pathlib import Path\n"
            "Path(sys.argv[1]).write_text(\n"
            "    subprocess.check_output(['git', 'log', '--format=%s'], text=True))\n"
        )

    def prepare_branch(self, status):
        self.git("switch", "--quiet", "-c", "task-1")
        if status in ("doing", "error"):
            self.run_cli("edit", "1", "-s", status)
        self.git("switch", "--quiet", "main")
        self.move_main()

    def test_doing_rebases_before_setup(self):
        self.prepare_branch("doing")
        self.run_cli("run", "--mode", "work")
        self.assertIn("main moved", (self.logs / "setup").read_text())
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", "main", "task-1"],
            cwd=self.root,
            check=True,
        )

    def test_rebase_failure_is_recorded(self):
        self.prepare_branch("doing")
        self.git("worktree", "add", ".worktrees/task-1", "task-1")
        untracked = self.root / ".worktrees/task-1/u.txt"
        untracked.write_text("saved contents\n")
        with mock.patch("chitty.run.git.rebase_onto", side_effect=ChittyError("boom")):
            self.run_cli("run", "--mode", "work")
        ticket_path = self.git("ls-tree", "-r", "--name-only", "task-1", "chitty/tasks").strip()
        ticket = self.git("show", f"task-1:{ticket_path}")
        self.assertIn("status: error", ticket)
        self.assertIn("Runner error (rebase)", ticket)
        self.assertIn("boom", ticket)
        self.assertFalse((self.logs / "agent").exists())
        self.assertEqual(untracked.read_text(), "saved contents\n")
        result = subprocess.run(
            ["git", "show-ref", "--verify", "--quiet", "refs/chitty/stash/TASK-1"],
            cwd=self.root,
            check=False,
        )
        self.assertEqual(result.returncode, 1)

    def test_todo_rebases_before_setup(self):
        self.prepare_branch("todo")
        self.run_cli("run", "--mode", "work")
        self.assertIn("main moved", (self.logs / "setup").read_text())
        log = subprocess.check_output(
            ["git", "log", "-p", "task-1", "--", "chitty/tasks"], cwd=self.root, text=True
        )
        self.assertIn("+status: doing", log)

    def test_error_rebases_before_setup(self):
        self.prepare_branch("error")
        self.run_cli("run", "--errors")
        self.assertIn("main moved", (self.logs / "setup").read_text())
        self.assertTrue((self.logs / "agent").exists())
