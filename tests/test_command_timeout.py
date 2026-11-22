import json
import shlex
import subprocess
import sys

from chitty.run import CommandTimedOut, run_logged
from tests import test_next
from tests.test_cli import CliTestCase


class TestCommandTimeout(CliTestCase):
    git = test_next.TestNext.git

    def test_logged_timeout_and_disabled_timeout(self):
        self.git("init", "--quiet")
        script = self.tmp / "slow.py"
        pids = self.tmp / "pids"
        script.write_text(
            "import os, subprocess, sys\n"
            "from pathlib import Path\n"
            "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(5)'])\n"
            "Path(sys.argv[1]).write_text(f'{os.getpid()} {child.pid}')\n"
            "print('marker', end='', flush=True)\n"
            "child.wait()\n"
            "raise SystemExit(7)\n"
        )
        command = shlex.join([sys.executable, str(script), str(pids)])
        with self.assertRaises(CommandTimedOut) as raised:
            run_logged("setup", command, self.root, 1)
        self.assertEqual(
            str(raised.exception),
            "setup timed out after 1 seconds; output in `.chitty/check.log`",
        )
        log = (self.root / ".chitty/check.log").read_bytes()
        self.assertEqual(
            log, f"# chitty setup: {command}\nmarker\n# timed out after 1 seconds\n".encode()
        )
        for pid in pids.read_text().split():
            result = subprocess.run(
                ["ps", "-p", pid, "-o", "stat="], capture_output=True, text=True, check=False
            )
            self.assertTrue(not result.stdout.strip() or result.stdout.strip().startswith("Z"))
        self.assertEqual(run_logged("setup", command, self.root, 0), 7)
        self.assertTrue(
            (self.root / ".chitty/check.log").read_bytes().endswith(b"marker\n# exit 7\n")
        )


class TestCommandTimeoutRouting(CliTestCase):
    git = test_next.TestNext.git
    check_project = test_next.TestNext.check_project
    commit_ticket = test_next.TestNext.commit_ticket
    add = test_next.TestNext.add
    install_fake_pi = test_next.TestNext.install_fake_pi

    def slow_project(self, phase):
        script = self.tmp / "slow.py"
        script.write_text("import time\nprint('slow', flush=True)\ntime.sleep(5)\n")
        self.check_project(f"{sys.executable} {script}" if phase == "check" else "true")
        config = self.root / "chitty.toml"
        text = config.read_text().replace(
            "autocommit = true", "autocommit = true\ncommand_timeout = 1"
        )
        if phase == "setup":
            text = text.replace(
                'setup = "true"', f"setup = {json.dumps(f'{sys.executable} {script}')}"
            )
        config.write_text(text)

    def test_todo_setup_timeout(self):
        self.assert_todo_timeout("setup")

    def test_todo_check_timeout(self):
        self.assert_todo_timeout("check")

    def assert_todo_timeout(self, phase):
        self.slow_project(phase)
        self.commit_ticket("Todo", "todo")
        marker = self.tmp / "agent-started"
        self.install_fake_pi(f"from pathlib import Path\nPath({str(marker)!r}).write_text('yes')\n")
        result = self.run_cli("run", "--mode", "work")
        self.assertEqual(result.stdout, "TASK-1: todo → error\n", result.stderr)
        self.assertFalse(marker.exists())
        ticket = self.git("show", "task-1:chitty/tasks/TASK-1--todo.md")
        self.assertIn(f"Runner error ({phase}): {phase} timed out after 1 seconds", ticket)
        log = (self.root / ".worktrees/task-1/.chitty/check.log").read_text()
        self.assertTrue(log.endswith("# timed out after 1 seconds\n"))

    def test_doing_check_timeout_continues(self):
        self.slow_project("check")
        self.commit_ticket("Doing", "doing")
        self.git("branch", "task-1")
        marker = self.tmp / "agent-started"
        self.install_fake_pi(
            "from pathlib import Path\nimport subprocess\n"
            f"Path({str(marker)!r}).write_text('yes')\n"
            "path = next(Path('chitty/tasks').glob('*.md'))\n"
            "path.write_text(path.read_text().replace('status: doing', 'status: review'))\n"
            "subprocess.run(['git', 'add', str(path)], check=True)\n"
            "subprocess.run(['git', 'commit', '--quiet', '-m', 'review'], check=True)\n"
        )
        result = self.run_cli("run", "--mode", "work")
        self.assertEqual(result.stdout, "TASK-1: doing → review\n", result.stderr)
        self.assertTrue(marker.exists())
        ticket = self.git("show", "task-1:chitty/tasks/TASK-1--doing.md")
        self.assertIn("Check failed before this session: check timed out", ticket)
