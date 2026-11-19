import subprocess
import sys
import time

from tests.test_cli import CliTestCase

HOLDER = """import fcntl, os, sys, time
from pathlib import Path
path, held, release = map(Path, sys.argv[1:])
path.parent.mkdir(parents=True, exist_ok=True)
with path.open('w') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    held.write_text('held')
    deadline = time.monotonic() + 30
    while not release.exists() and time.monotonic() < deadline:
        time.sleep(0.05)
"""


class TestMainCheckoutLock(CliTestCase):
    def setUp(self):
        super().setUp()
        self.run_cli("init")
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace("autocommit = false", "autocommit = true"))
        self.run_cli("add", "One", "-d", "description")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "seed")

    def git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.root, capture_output=True, check=True, text=True
        ).stdout

    def hold_lock(self):
        held = self.tmp / "held"
        release = self.tmp / "release"
        lock = self.root / ".git/chitty/run/main-checkout.lock"
        process = subprocess.Popen(
            [sys.executable, "-c", HOLDER, str(lock), str(held), str(release)]
        )
        deadline = time.monotonic() + 10
        while not held.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.05)
        self.assertTrue(held.exists(), "lock holder did not acquire lock")

        def stop_holder():
            release.touch()
            process.wait(timeout=10)

        self.addCleanup(stop_holder)
        return release

    def test_main_checkout_write_waits_for_lock(self):
        release = self.hold_lock()
        previous = self.git("log", "-1", "--format=%s")
        process = subprocess.Popen(
            [
                sys.executable,
                "-c",
                "from chitty.cli import main; main()",
                "edit",
                "TASK-1",
                "--note",
                "waited",
            ],
            cwd=self.root,
        )
        try:
            time.sleep(2)
            self.assertIsNone(process.poll())
            self.assertEqual(self.git("log", "-1", "--format=%s"), previous)
        finally:
            release.touch()
        self.assertEqual(process.wait(timeout=30), 0)
        self.assertTrue(self.git("log", "-1", "--format=%s").startswith("chitty: edit TASK-1"))

    def test_ticket_worktree_write_does_not_wait(self):
        worktree = self.root / ".worktrees/task-1"
        worktree.parent.mkdir()
        self.git("worktree", "add", "-b", "task-1", str(worktree))
        self.hold_lock()
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from chitty.cli import main; main()",
                "edit",
                "TASK-1",
                "--note",
                "no wait",
            ],
            cwd=worktree,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        subject = subprocess.run(
            ["git", "log", "-1", "--format=%s"],
            cwd=worktree,
            capture_output=True,
            check=True,
            text=True,
        ).stdout
        self.assertTrue(subject.startswith("chitty: edit TASK-1"))
