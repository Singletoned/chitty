import os
import stat
import subprocess
import sys
from unittest.mock import patch

from chitty.store import Repo
from tests.test_cli import CliTestCase


class TestRunLoop(CliTestCase):
    def git(self, *args: str) -> None:
        subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)

    def setup_run(self) -> None:
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")

    def test_help_explains_loop(self):
        help_text = self.run_cli("run", "--help").output
        self.assertIn("--loop", help_text)
        self.assertIn("60 seconds", help_text)

    def test_loop_runs_agent_then_waits_for_idle_work(self):
        self.setup_run()
        self.run_cli("add", "Work", "-d", "A task")
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\n"
            "from pathlib import Path\n"
            "import subprocess, sys\n"
            "Path('agent-args').write_text(repr(sys.argv[1:]))\n"
            "subprocess.run(['chitty', 'edit', 'TASK-1', '-s', 'review'], check=True)\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        with (
            patch.dict(os.environ, {"PATH": f"{fake.parent}:{os.environ.get('PATH', '')}"}),
            patch("chitty.run.time.sleep", side_effect=[None, KeyboardInterrupt]) as sleep,
        ):
            result = self.run_cli(
                "run",
                "--loop",
                "--mode",
                "work",
                "--",
                "--model",
                "gpt-6-luna",
                exit_code=130,
            )
        self.assertEqual(result.exit_code, 130)
        task = Repo.open(self.root).find(Repo.open(self.root).resolve("TASK-1"))
        self.assertEqual(task.task.frontmatter.status, "review")
        self.assertEqual(sleep.call_count, 2)
        self.assertIn(
            "'--model', 'gpt-6-luna'", (self.root / ".worktrees/task-1/agent-args").read_text()
        )

    def test_loop_rejects_ticket_and_stops_on_errors(self):
        self.assertIn(
            "--loop cannot be used with --ticket",
            self.run_cli(
                "run",
                "--loop",
                "--ticket",
                "TASK-1",
                exit_code=2,
            ).output,
        )
        self.setup_run()
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace("autocommit = true", "autocommit = false"))
        with patch("chitty.run.time.sleep") as sleep:
            result = self.run_cli("run", "--loop", exit_code=1)
        self.assertEqual(result.exit_code, 1)
        sleep.assert_not_called()
