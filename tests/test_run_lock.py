import json
import os
import signal
import stat
import subprocess
import sys
import time
from pathlib import Path
from unittest import mock

from chitty.locks import is_locked, run_lock
from tests.test_cli import CliTestCase

WAIT_SECONDS = 60
POLL_SECONDS = 0.05

# Records whether its ticket is locked, optionally waits for `go`, then moves
# the ticket on and commits, or exits 1 if `fail` exists.
AGENT = """\
import os
import subprocess, sys, time
from pathlib import Path
from chitty.locks import is_locked
mode, ticket, logs = sys.argv[1], sys.argv[2], Path(sys.argv[3])
(logs / f"{ticket}.locked").write_text(str(is_locked(Path.cwd(), ticket)))
(logs / f"{ticket}.started").touch()
if (logs / "capture").exists():
    result = subprocess.run(
        [sys.executable, "-c", "from chitty.cli import cli; cli()", "show", ticket, "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    (logs / f"{ticket}.running.json").write_text(result.stdout)
    (logs / f"{ticket}.actor").write_text(os.environ["CHITTY_ACTOR"])
if (logs / "wait").exists():
    deadline = time.monotonic() + 60
    while not (logs / "go").exists():
        if time.monotonic() > deadline:
            sys.exit("timed out waiting for go")
        time.sleep(0.05)
if (logs / "fail").exists():
    sys.exit(1)
path = next(Path("chitty/tasks").glob(ticket + "--*.md"))
before, after = ("review", "done") if mode == "review" else ("doing", "review")
path.write_text(path.read_text().replace(f"status: {before}\\n", f"status: {after}\\n"))
subprocess.run(["git", "commit", "--quiet", "-am", "agent"], check=True)
"""

HOLDER = """\
import sys
from pathlib import Path
from chitty.locks import run_lock
with run_lock(Path(sys.argv[1]), sys.argv[2], actor="holder", mode="work"):
    print("held", flush=True)
    sys.stdin.read()
"""


class RunLockTestCase(CliTestCase):
    def setUp(self):
        super().setUp()
        self.logs = self.tmp / "logs"
        self.logs.mkdir()
        agent = self.tmp / "bin" / "fake"
        agent.parent.mkdir()
        agent.write_text("#!" + sys.executable + "\n" + AGENT)
        agent.chmod(agent.stat().st_mode | stat.S_IXUSR)
        previous_path = os.environ["PATH"]
        os.environ["PATH"] = f"{agent.parent}:{previous_path}"
        self.addCleanup(os.environ.__setitem__, "PATH", previous_path)
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace("autocommit = false", 'autocommit = true\nsetup = "true"')
            .replace(
                'agent_command = "pi --chitty-{mode} {id}"',
                f'agent_command = "fake {{mode}} {{id}} {self.logs}"',
            )
        )
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.run_cli("init")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=self.root, capture_output=True, check=True, text=True
        ).stdout

    def add(self, title: str) -> str:
        return self.run_cli("add", title, "-d", "Description.").stdout.split()[1]

    def add_review(self, title: str) -> str:
        ticket = self.add(title)
        self.run_cli("edit", ticket, "-s", "doing")
        self.run_cli("edit", ticket, "-s", "review")
        self.git("branch", ticket.lower())
        return ticket

    def wait_for(self, *paths: Path) -> None:
        deadline = time.monotonic() + WAIT_SECONDS
        while not all(path.exists() for path in paths):
            self.assertLess(time.monotonic(), deadline, f"timed out waiting for {paths}")
            time.sleep(POLL_SECONDS)


class TestRunLock(RunLockTestCase):
    def test_the_lock_is_free_once_its_holder_is_killed(self):
        holder = subprocess.Popen(
            [sys.executable, "-c", HOLDER, str(self.root), "TASK-1"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(holder.wait)
        assert holder.stdout is not None
        self.assertEqual(holder.stdout.readline(), "held\n")
        self.assertTrue(is_locked(self.root, "TASK-1"))
        self.assertFalse(is_locked(self.root, "TASK-2"))

        holder.send_signal(signal.SIGKILL)
        holder.wait()
        assert holder.stdin is not None and holder.stdout is not None
        holder.stdin.close()
        holder.stdout.close()

        self.assertFalse(is_locked(self.root, "TASK-1"))

    def test_show_and_list_report_the_lock_record(self):
        ticket = self.add("Visible")

        with run_lock(self.root, ticket, actor="alice", mode="review"):
            record = self.json("show", ticket)["running"]
            self.assertEqual(record["actor"], "alice")
            self.assertEqual(record["mode"], "review")
            self.assertEqual(record["pid"], os.getpid())
            self.assertIn("running: review by alice, process", self.run_cli("show", ticket).stdout)
            self.assertIn("▶ running", self.run_cli("list").stdout)

            lock_path = next((self.root / ".git/chitty/run").glob(f"{ticket}.lock"))
            lock_path.write_text("12345\n")
            self.assertEqual(self.json("show", ticket)["running"], {"pid": "12345"})
            self.assertIn("running: process 12345", self.run_cli("show", ticket).stdout)

    def test_next_skips_a_locked_ticket_and_run_ticket_refuses_it(self):
        first = self.add("First")
        second = self.add("Second")

        with run_lock(self.root, first, actor="test", mode="work"):
            self.assertEqual(self.run_cli("next").stdout, f"work {second}\n")
            refused = self.run_cli("run", "--ticket", first, exit_code=1)
            self.assertIn(f"{first} is being run by process {os.getpid()}", refused.stderr)
            with run_lock(self.root, second, actor="test", mode="work"):
                self.run_cli("next", exit_code=3)

        self.assertEqual(self.run_cli("next").stdout, f"work {first}\n")
        self.assertFalse((self.logs / f"{first}.started").exists())

    def test_agent_can_read_its_running_record(self):
        ticket = self.add("Captured")
        (self.logs / "capture").touch()

        self.run_cli("run", "--ticket", ticket)

        record = json.loads((self.logs / f"{ticket}.running.json").read_text())["running"]
        self.assertEqual(record["actor"], (self.logs / f"{ticket}.actor").read_text())
        self.assertEqual(record["mode"], "work")

    def test_a_run_holds_the_lock_and_frees_it_however_it_ends(self):
        succeeded = self.add("Succeeds")
        self.assertEqual(
            self.run_cli("run").stdout.splitlines()[-1], f"{succeeded}: doing → review"
        )
        self.assertEqual((self.logs / f"{succeeded}.locked").read_text(), "True")
        self.assertFalse(is_locked(self.root, succeeded))

        failed = self.add("Fails")
        (self.logs / "fail").touch()
        self.run_cli("run", "--ticket", failed, exit_code=1)
        self.assertEqual((self.logs / f"{failed}.locked").read_text(), "True")
        self.assertFalse(is_locked(self.root, failed))
        (self.logs / "fail").unlink()

        with mock.patch("chitty.git.rebase", side_effect=KeyboardInterrupt):
            self.run_cli("run", "--ticket", succeeded, exit_code=130)
        self.assertFalse(is_locked(self.root, succeeded))

    def test_concurrent_reviewers_take_different_tickets(self):
        tickets = {self.add_review("Review one"), self.add_review("Review two")}
        (self.logs / "wait").touch()
        command = [sys.executable, "-c", "from chitty.cli import cli; cli()", "run"]
        reviewers = [
            subprocess.Popen(
                [*command, "--mode", "review"],
                cwd=self.root,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for _ in tickets
        ]
        try:
            self.wait_for(*(self.logs / f"{ticket}.started" for ticket in tickets))
            idle = self.run_cli("run", "--mode", "review", exit_code=3)
            self.assertEqual(idle.stderr.splitlines()[-1], "no next ticket for --mode review")
        finally:
            (self.logs / "go").touch()
            outputs = [reviewer.communicate(timeout=WAIT_SECONDS) for reviewer in reviewers]

        for reviewer, (_, stderr) in zip(reviewers, outputs, strict=True):
            self.assertEqual(reviewer.returncode, 0, stderr)
        self.assertEqual(
            sorted(stdout.splitlines()[-1] + "\n" for stdout, _ in outputs),
            sorted(f"{ticket}: review → done\n" for ticket in tickets),
        )
