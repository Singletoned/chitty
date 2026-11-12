import json
import os
import stat
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from tests.test_cli import CliTestCase


class TestRunErrorReporter(CliTestCase):
    def git(self, *args: str) -> None:
        subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)

    def setup_repo(self, reporter: str | None) -> None:
        config = self.root / "chitty.toml"
        text = (
            config.read_text()
            .replace("autocommit = false", 'autocommit = true\nsetup = "true"')
            .replace(
                'agent_command = "pi --chitty-{mode} {id}"', 'agent_command = "false {mode} {id}"'
            )
        )
        if reporter is not None:
            text = text.replace(
                "autocommit = true", f"autocommit = true\nerror_reporter = {reporter!r}"
            )
        config.write_text(text)
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")

    def write_reporter(self, *, exit_code: int = 0) -> tuple[str, Path]:
        record = self.tmp / "report.json"
        script = self.tmp / "bin" / "report"
        script.parent.mkdir(exist_ok=True)
        script.write_text(
            "#!" + sys.executable + "\n"
            "import json, sys\n"
            f"open({str(record)!r}, 'w').write(json.dumps(sys.argv[1:]))\n"
            f"sys.exit({exit_code})\n"
        )
        script.chmod(script.stat().st_mode | stat.S_IXUSR)
        return f"{script} {{message}} {{context}}", record

    def add_ticket(self) -> None:
        self.run_cli("add", "Work", "-d", "A task")

    def run_failing_agent(self) -> None:
        bindir = self.tmp / "agentbin"
        bindir.mkdir(exist_ok=True)
        env = os.environ.copy()
        env["PATH"] = f"{bindir}:{env['PATH']}"
        with patch.dict(os.environ, env):
            self.run_cli("run", "--mode", "work", exit_code=1)

    def test_failing_run_reports_message_and_ticket_context(self):
        reporter, record = self.write_reporter()
        self.setup_repo(reporter)
        self.add_ticket()
        self.run_failing_agent()
        message, context = json.loads(record.read_text())
        self.assertIn("agent exited with status", message)
        self.assertEqual(json.loads(context)["ticket"], "TASK-1")

    def test_failing_reporter_warns_and_preserves_failure(self):
        reporter, record = self.write_reporter(exit_code=7)
        self.setup_repo(reporter)
        self.add_ticket()
        result = self.run_cli("run", "--mode", "work", exit_code=1)
        self.assertTrue(record.exists())
        self.assertIn("error_reporter exited with status 7", result.stderr)

    def test_argument_error_reports_message_and_ticket_context(self):
        reporter, record = self.write_reporter()
        self.setup_repo(reporter)
        self.add_ticket()
        result = self.run_cli("run", "--ticket", "TASK-1", "--mode", "work", exit_code=1)
        self.assertIn("--mode cannot be used with --ticket", result.stderr)
        message, context = json.loads(record.read_text())
        self.assertEqual(message, "--mode cannot be used with --ticket")
        self.assertIn("actor", json.loads(context))

    def test_empty_queue_does_not_report(self):
        reporter, record = self.write_reporter()
        self.setup_repo(reporter)
        self.run_cli("run", "--mode", "work", exit_code=3)
        self.assertFalse(record.exists())
