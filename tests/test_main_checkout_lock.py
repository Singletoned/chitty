import subprocess
import sys
import threading
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


NESTED = """import subprocess, sys
from pathlib import Path
from chitty.locks import main_checkout_lock
root, lock = Path(sys.argv[1]), sys.argv[2]
probe = ("import fcntl, sys\\nf = open(sys.argv[1], 'a')\\n"
         "try:\\n    fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)\\n    print('free')\\n"
         "except BlockingIOError:\\n    print('held')\\n")
def state():
    return subprocess.run([sys.executable, '-c', probe, lock], capture_output=True,
                          text=True, check=True).stdout.strip()
with main_checkout_lock(root):
    with main_checkout_lock(root):
        pass
    print('after inner:', state())
print('after outer:', state())
"""


class TestMainCheckoutLockReentry(CliTestCase):
    def test_nested_entry_in_one_process_does_not_deadlock(self):
        subprocess.run(["git", "init", "--quiet", "-b", "main"], cwd=self.root, check=True)
        lock = self.root / ".git/chitty/run/main-checkout.lock"
        result = subprocess.run(
            [sys.executable, "-c", NESTED, str(self.root), str(lock)],
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
        self.assertEqual(
            result.stdout.splitlines(), ["after inner: held", "after outer: free"], result.stderr
        )

    def test_different_threads_are_serialized(self):
        from chitty.locks import main_checkout_lock

        subprocess.run(["git", "init", "--quiet", "-b", "main"], cwd=self.root, check=True)
        first_entered = threading.Event()
        release_first = threading.Event()
        second_entered = threading.Event()

        def first():
            with main_checkout_lock(self.root):
                first_entered.set()
                self.assertTrue(release_first.wait(timeout=10))

        def second():
            with main_checkout_lock(self.root):
                second_entered.set()

        first_thread = threading.Thread(target=first)
        second_thread = threading.Thread(target=second)
        first_thread.start()
        self.assertTrue(first_entered.wait(timeout=10))
        second_thread.start()
        try:
            self.assertFalse(second_entered.wait(timeout=0.2))
        finally:
            release_first.set()
        first_thread.join(timeout=10)
        second_thread.join(timeout=10)
        self.assertFalse(first_thread.is_alive())
        self.assertFalse(second_thread.is_alive())
        self.assertTrue(second_entered.is_set())
