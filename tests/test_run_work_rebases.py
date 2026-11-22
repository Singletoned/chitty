import subprocess
import sys
from importlib.resources import files
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


class TestConflictAgent(ReviewMergeTestCase):
    def setUp(self):
        super().setUp()
        agent = self.tmp / "bin" / "fake-prompt"
        agent.write_text(
            f"#!{sys.executable}\n"
            "import subprocess, sys\n"
            "from pathlib import Path\n"
            f"with Path({str(self.logs / 'prompt')!r}).open('a') as log:\n"
            "    state = subprocess.run(['git', 'rev-parse', '-q', '--verify', "
            "'REBASE_HEAD'], stdout=subprocess.DEVNULL).returncode\n"
            "    log.write(str(state) + '\\n' + sys.argv[-1] + '\\n')\n"
        )
        agent.chmod(0o755)
        config = self.root / "chitty.toml"
        text = config.read_text()
        import re

        text = re.sub(r'agent_command = ".*"', 'agent_command = "fake-prompt {prompt}"', text)
        config.write_text(text)
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "prompt agent")

    def conflict(self, status, dirty=False):
        self.git("switch", "--quiet", "-c", "task-1")
        self.run_cli("edit", "1", "-s", status)
        (self.root / "shared.txt").write_text("branch\n")
        self.git("add", "shared.txt")
        self.git("commit", "--quiet", "-m", "branch change")
        self.git("switch", "--quiet", "main")
        self.move_main(shared="main\n")
        if dirty:
            self.git("worktree", "add", ".worktrees/task-1", "task-1")
            (self.worktree / "uncommitted.txt").write_text("dirty\n")
        self.run_cli(
            "run",
            "--errors" if status == "error" else "--mode",
            *([] if status == "error" else ["work"]),
            exit_code=1 if status == "error" else 0,
        )

    def assert_stopped(self):
        prompt = (self.logs / "prompt").read_text()
        rebase = files("chitty").joinpath("roles/rebase.md").read_text().rstrip()
        self.assertTrue(prompt.startswith("0\nWork only on Chitty ticket TASK-1.\n\n" + rebase))
        self.assertFalse((self.logs / "setup").exists())

    def test_conflict_doing_starts_agent_with_rebase(self):
        self.conflict("doing")
        self.assert_stopped()

    def test_conflict_error_starts_agent_with_rebase(self):
        self.conflict("error")
        self.assert_stopped()

    def test_dirty_conflict_aborts_rebase(self):
        self.conflict("doing", dirty=True)
        self.assertTrue((self.logs / "prompt").read_text().startswith("1\n"))
        self.assertTrue((self.logs / "setup").exists())
