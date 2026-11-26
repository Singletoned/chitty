import os
import stat
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from tests.test_cli import CliTestCase


class TestRunClaimsOnBranch(CliTestCase):
    def setUp(self):
        super().setUp()
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.run_cli("init")
        self.run_cli("add", "Claim me", "-d", "Description.")
        self.logs = self.root / "logs"
        self.logs.mkdir()
        config.write_text(
            config.read_text().replace(
                'agent_command = "pi --chitty-{mode} {id}"',
                f'agent_command = "fake {{mode}} {{id}} {self.logs}"',
            )
        )
        fake = self.root / "bin" / "fake"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\n"
            "from pathlib import Path\n"
            "import subprocess, sys\n"
            "logs = Path(sys.argv[3])\n"
            "ticket = next(Path('chitty/tasks').glob('TASK-1--*.md'))\n"
            "(logs / 'agent').write_text(ticket.read_text())\n"
            "head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True)\n"
            "(logs / 'head').write_text(head)\n"
            "show = subprocess.check_output(['chitty', 'show', 'TASK-1', '--json'], "
            "cwd=logs.parent, text=True)\n"
            "(logs / 'show').write_text(show)\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "initial")
        self.path_patch = patch.dict(os.environ, {"PATH": f"{fake.parent}:{os.environ['PATH']}"})
        self.path_patch.start()
        self.addCleanup(self.path_patch.stop)

    def git(self, *args: str, cwd: Path | None = None) -> str:
        return subprocess.run(
            ["git", *args], cwd=cwd or self.root, capture_output=True, text=True, check=True
        ).stdout

    def ticket(self, root: Path) -> Path:
        return next((root / "chitty/tasks").glob("TASK-1--*.md"))

    def worktree(self) -> Path:
        self.git("branch", "task-1", "main")
        worktree = self.root / ".worktrees/task-1"
        self.git("worktree", "add", str(worktree), "task-1")
        return worktree

    def test_new_branch_claims_before_agent(self):
        main = self.git("rev-parse", "main").strip()
        self.run_cli("run")
        self.assertEqual(self.git("rev-parse", "main").strip(), main)
        rel = self.ticket(self.root).relative_to(self.root)
        self.assertIn("status: todo", self.git("show", f"main:{rel}"))
        commits = self.git("rev-list", "--reverse", "main..task-1").splitlines()
        self.assertIn("status: doing", self.git("show", f"{commits[0]}:{rel}"))
        self.assertEqual((self.logs / "head").read_text().strip(), commits[0])
        self.assertIn("status: doing", (self.logs / "agent").read_text())
        self.assertIn('"status": "doing"', (self.logs / "show").read_text())

    def test_existing_branch_keeps_note_and_claims_before_agent(self):
        worktree = self.worktree()
        subprocess.run(
            ["chitty", "edit", "TASK-1", "--note", "Branch note."],
            cwd=worktree,
            check=True,
            capture_output=True,
            text=True,
        )
        previous = self.git("rev-parse", "task-1").strip()
        main = self.git("rev-parse", "main").strip()
        self.run_cli("run")
        self.assertEqual(self.git("rev-parse", "main").strip(), main)
        claim = (self.logs / "head").read_text().strip()
        self.assertEqual(self.git("rev-parse", f"{claim}^").strip(), previous)
        self.assertIn("status: doing", (self.logs / "agent").read_text())
        self.assertIn("Branch note.", (self.logs / "agent").read_text())

    def assert_failure_leaves_main_unchanged(self, phase: str):
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace(f'{phase} = "true"', f'{phase} = "false"'))
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", f"fail {phase}")
        main = self.git("rev-parse", "main").strip()
        self.run_cli("run", exit_code=1 if phase == "check" else 0)
        self.assertEqual(self.git("rev-parse", "main").strip(), main)
        status = "todo" if phase == "check" else "error"
        self.assertIn(f"status: {status}", self.ticket(self.root / ".worktrees/task-1").read_text())
        self.assertFalse((self.logs / "agent").exists())

    def test_setup_failure_leaves_main_unchanged(self):
        self.assert_failure_leaves_main_unchanged("setup")

    def test_check_failure_leaves_main_unchanged(self):
        self.assert_failure_leaves_main_unchanged("check")

    def test_unfinished_rebase_does_not_claim(self):
        code = self.root / "code.txt"
        code.write_text("original\n")
        self.git("add", "code.txt")
        self.git("commit", "--quiet", "-m", "code")
        worktree = self.worktree()
        (worktree / "code.txt").write_text("branch\n")
        self.git("add", "code.txt", cwd=worktree)
        self.git("commit", "--quiet", "-m", "branch code", cwd=worktree)
        code.write_text("main\n")
        self.git("add", "code.txt")
        self.git("commit", "--quiet", "-m", "main code")
        rebase = subprocess.run(
            ["git", "rebase", "main"], cwd=worktree, capture_output=True, check=False
        )
        self.assertNotEqual(rebase.returncode, 0)
        main = self.git("rev-parse", "main").strip()
        branch = self.git("rev-parse", "task-1").strip()
        self.run_cli("run", exit_code=1)
        self.assertEqual(self.git("rev-parse", "main").strip(), main)
        self.assertEqual(self.git("rev-parse", "task-1").strip(), branch)
        self.assertIn("status: todo", self.ticket(self.root).read_text())
        self.assertIn("status: todo", self.ticket(worktree).read_text())

    def test_dirty_worktree_ticket_is_rejected(self):
        worktree = self.worktree()
        ticket = self.ticket(worktree)
        ticket.write_text(ticket.read_text() + "\nUncommitted.\n")
        main = self.git("rev-parse", "main").strip()
        branch = self.git("rev-parse", "task-1").strip()
        result = self.run_cli("run", exit_code=1)
        self.assertIn(str(ticket), result.stderr)
        self.assertEqual(self.git("rev-parse", "main").strip(), main)
        self.assertEqual(self.git("rev-parse", "task-1").strip(), branch)
        self.assertIn("Uncommitted.", ticket.read_text())
        self.assertFalse((self.logs / "agent").exists())
