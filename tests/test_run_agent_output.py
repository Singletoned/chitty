import os
import subprocess
import sys
import tempfile
import time

from chitty.run import _run_agent
from tests.support import RepoTestCase


class TestAgentOutput(RepoTestCase):
    def call_agent(self, function, script, log, timeout=10):
        return function(
            [sys.executable, "-c", script],
            cwd=self.root,
            env=os.environ.copy(),
            timeout=timeout,
            log=log,
        )

    def check_append_behavior(self, function):
        outputs = (
            b"out-1\nerr-1\nout-2\nerr-2\nout-3\nerr-3\n\xff\ntail",
            b"",
            b"\xe2\x82",
        )
        scripts = (
            (
                "import sys\n"
                "for i in range(1, 4):\n"
                " print(f'out-{i}', flush=True)\n"
                " print(f'err-{i}', file=sys.stderr, flush=True)\n"
                "sys.stdout.buffer.write(b'\\xff\\ntail'); sys.stdout.flush()\n"
            ),
            "pass\n",
            "import sys; sys.stdout.buffer.write(b'\\xe2\\x82'); sys.stdout.flush()\n",
        )
        with tempfile.TemporaryFile() as log:
            log.write(b"earlier\n")
            log.seek(0)
            returned = [self.call_agent(function, script, log) for script in scripts]
            self.assertEqual([result.returncode for result in returned], [0, 0, 0])
            self.assertEqual([result.stdout for result in returned], list(outputs))
            log.seek(0)
            self.assertEqual(log.read(), b"earlier\n" + b"".join(outputs))

    def test_output_is_appended_and_results_are_per_call(self):
        self.check_append_behavior(_run_agent)

        def returns_whole_log(*args, **kwargs):
            result = _run_agent(*args, **kwargs)
            log = kwargs["log"]
            log.flush()
            log.seek(0)
            result.stdout = log.read()
            return result

        def does_not_seek_to_end(command, *, cwd, env, timeout, log):
            log.flush()
            offset = log.tell()
            process = subprocess.Popen(
                command, cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT
            )
            process.wait(timeout=timeout or None)
            end = os.fstat(log.fileno()).st_size
            log.seek(offset)
            return subprocess.CompletedProcess(
                command, process.returncode, stdout=log.read(end - offset)
            )

        for wrong in (returns_whole_log, does_not_seek_to_end):
            with (
                self.subTest(implementation=wrong.__name__),
                self.assertRaises(AssertionError),
            ):
                self.check_append_behavior(wrong)

    def check_descendant_behavior(self, function):
        pid_file = self.root / "descendant.pid"
        script = (
            "import subprocess, sys\n"
            "child = subprocess.Popen([sys.executable, '-c', "
            "'import time; time.sleep(4); print(\\\"LATE\\\", flush=True)'])\n"
            f"open({str(pid_file)!r}, 'w').write(str(child.pid))\n"
        )
        with tempfile.TemporaryFile() as log:
            log.write(b"earlier\n")
            pid = None
            try:
                started = time.monotonic()
                result = self.call_agent(function, script, log)
                self.assertLess(time.monotonic() - started, 3)
                self.assertNotIn(b"LATE", result.stdout)
                self.assertNotIn(b"earlier", result.stdout)
                pid = int(pid_file.read_text())
                deadline = time.monotonic() + 10
                while time.monotonic() < deadline:
                    state = subprocess.run(
                        ["ps", "-o", "stat=", "-p", str(pid)],
                        check=False,
                        capture_output=True,
                        text=True,
                    ).stdout.strip()
                    if not state or state.startswith("Z"):
                        break
                    time.sleep(0.05)
                else:
                    self.fail("descendant did not exit")
                log.seek(0)
                self.assertIn(b"LATE", log.read())
            finally:
                if pid is None and pid_file.exists():
                    pid = int(pid_file.read_text())
                if pid is not None:
                    subprocess.run(["kill", "-9", str(pid)], check=False)

    def test_descendant_does_not_hold_call_open(self):
        self.check_descendant_behavior(_run_agent)

        def waits_for_descendant(*args, **kwargs):
            result = _run_agent(*args, **kwargs)
            pid = int((self.root / "descendant.pid").read_text())
            subprocess.run(["kill", "-0", str(pid)], check=False)
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                state = subprocess.run(
                    ["ps", "-o", "stat=", "-p", str(pid)],
                    check=False,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                if not state or state.startswith("Z"):
                    break
                time.sleep(0.05)
            return result

        with self.assertRaises(AssertionError):
            self.check_descendant_behavior(waits_for_descendant)

    def check_timeout_behavior(self, function):
        with tempfile.TemporaryFile() as log:
            result = self.call_agent(
                function,
                "import time; print('TIMEOUT_MARKER', flush=True); time.sleep(60)",
                log,
                timeout=2,
            )
            self.assertEqual(result.stderr, b"timed out")
            self.assertIn(b"TIMEOUT_MARKER", result.stdout)
            log.seek(0)
            self.assertIn(b"TIMEOUT_MARKER", log.read())

    def test_timeout_retains_output(self):
        self.check_timeout_behavior(_run_agent)

        def drops_timeout_output(*args, **kwargs):
            result = _run_agent(*args, **kwargs)
            result.stdout = b""
            return result

        with self.assertRaises(AssertionError):
            self.check_timeout_behavior(drops_timeout_output)
