import contextlib
import io
import os
import subprocess
import sys
import threading
import time

from chitty.errors import ChittyError
from chitty.run import _run_agent
from tests.support import RepoTestCase


class TestAgentOutput(RepoTestCase):
    def run_agent(self, script, log=None, timeout=10):
        return _run_agent(
            [sys.executable, "-c", script],
            cwd=self.root,
            env=os.environ.copy(),
            timeout=timeout,
            log=log,
        )

    def test_output_is_echoed_and_logged_in_order(self):
        script = (
            "import sys\n"
            "for i in range(1, 6):\n"
            " print(f'out-{i}', flush=True)\n"
            " print(f'err-{i}', file=sys.stderr, flush=True)\n"
            "sys.stdout.write('tail'); sys.stdout.flush()\n"
        )
        expected = "".join(f"out-{i}\nerr-{i}\n" for i in range(1, 6)) + "tail"
        with (self.root / "agent.log").open("w") as log:
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                result = self.run_agent(script, log)
        self.assertEqual(log_text := (self.root / "agent.log").read_text(), expected)
        self.assertEqual(stderr.getvalue(), expected)
        self.assertEqual(result.stdout, log_text.encode())
        self.assertEqual(result.returncode, 0)

    def test_invalid_bytes_are_replaced_and_log_errors_raise(self):
        calls = []
        previous = threading.excepthook
        threading.excepthook = calls.append
        try:
            script = (
                "import sys\n"
                "sys.stdout.buffer.write(b'\\xff bad\\n'); sys.stdout.flush()\n"
                "sys.stdout.write('é\\n'); sys.stdout.flush()\n"
                "sys.stdout.buffer.write(b'\\xe2\\x82'); sys.stdout.flush()\n"
            )
            with (self.root / "agent.log").open("w") as log:
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    result = self.run_agent(script, log)
            self.assertIn(" bad", (self.root / "agent.log").read_text())
            self.assertIn("é", (self.root / "agent.log").read_text())
            self.assertTrue((self.root / "agent.log").read_text().endswith("�"))
            self.assertEqual(calls, [])
            self.assertIn(b"\xff bad", result.stdout)

            closed = (self.root / "closed.log").open("w")
            closed.close()
            with self.assertRaisesRegex(ChittyError, "^cannot write agent output"):
                self.run_agent("print('output', flush=True)", closed)
        finally:
            threading.excepthook = previous

    def test_descendant_output_after_grace_is_not_logged(self):
        log_path = self.root / "late.log"
        script = (
            "import subprocess, sys, time\n"
            "child = subprocess.Popen([sys.executable, '-c', "
            "'import time; time.sleep(4); print(\\\"LATE\\\", flush=True)'])\n"
            "open(" + repr(str(self.root / "child.pid")) + ", 'w').write(str(child.pid))\n"
        )
        started = time.monotonic()
        with log_path.open("w") as log:
            result = self.run_agent(script, log)
        self.assertEqual(result.returncode, 0)
        self.assertLess(time.monotonic() - started, 3.5)
        try:
            time.sleep(max(0, 5 - (time.monotonic() - started)))
            self.assertNotIn("LATE", log_path.read_text())
        finally:
            pid_file = self.root / "child.pid"
            if pid_file.exists():
                subprocess.run(["kill", "-9", pid_file.read_text()], check=False)

    def test_timeout_preserves_output_and_sentinel(self):
        stderr = io.StringIO()
        with (
            (self.root / "timeout.log").open("w") as log,
            contextlib.redirect_stderr(stderr),
        ):
            result = self.run_agent(
                "import time; print('TIMEOUT_MARKER', flush=True); time.sleep(60)",
                log,
                timeout=2,
            )
        self.assertEqual(result.stderr, b"timed out")
        self.assertIn(b"TIMEOUT_MARKER", result.stdout)
        self.assertIn("TIMEOUT_MARKER", (self.root / "timeout.log").read_text())
