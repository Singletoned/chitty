import json
import os
import subprocess
import sys
import time
from unittest.mock import patch

from chitty import config as config_module
from chitty.config import load_repo_config
from chitty.run import _run_agent
from tests.support import RepoTestCase
from tests.test_cli import CliTestCase


class TestAgentTimeout(CliTestCase):
    def test_run_timeout_records_usage_and_exits_one(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace(
                "autocommit = false",
                'autocommit = true\nsetup = "true"\nagent_timeout = 2\nproject = "timeout-test"',
            )
            .replace(
                'agent_command = "pi --chitty-{mode} {id}"',
                'agent_command = "fake-agent {mode} {id}"',
            )
        )
        subprocess.run(["git", "init", "--quiet", "-b", "main"], cwd=self.root, check=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"], cwd=self.root, check=True
        )
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.root, check=True)
        self.run_cli("add", "Timeout test", "-d", "Exercise timeout")
        subprocess.run(["git", "add", "--all"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "--quiet", "-m", "setup"], cwd=self.root, check=True)

        bindir = self.tmp / "bin"
        bindir.mkdir()
        pid_file = self.tmp / "agent-pids"
        fake = bindir / "fake-agent"
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import os, subprocess, sys, time\n"
            "print('TIMEOUT_MARKER', flush=True)\n"
            "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
            f"open({str(pid_file)!r}, 'w').write(str(os.getpid()) + ' ' + str(child.pid))\n"
            "time.sleep(60)\n"
        )
        fake.chmod(0o755)
        env = os.environ.copy()
        env["PATH"] = f"{bindir}:{env['PATH']}"
        with patch.dict(os.environ, env):
            result = self.run_cli("run", "--mode", "work")
        self.assertEqual(result.stdout, "TASK-1: todo → error\n")
        error = self.run_cli("show", "TASK-1").stdout
        self.assertIn("agent timed out after 2 seconds", error)
        self.assertIn("TIMEOUT_MARKER", error)
        usage = self.tmp / "data/chitty/usage/timeout-test.jsonl"
        self.assertTrue(usage.exists())
        entries = [json.loads(line) for line in usage.read_text().splitlines()]
        self.assertEqual(len(entries), 1)
        agent, child = map(int, pid_file.read_text().split())
        for pid in (agent, child):
            state = subprocess.run(
                ["ps", "-o", "stat=", "-p", str(pid)],
                check=False,
                capture_output=True,
                text=True,
            ).stdout.strip()
            self.assertTrue(not state or state.startswith("Z"))


class TestDirectAgentTimeout(RepoTestCase):
    def test_timeout_terminates_agent_and_child_but_preserves_process_group(self):
        record = self.root / "pids"
        script = (
            "import os, subprocess, sys, time\n"
            "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
            f"open({str(record)!r}, 'w').write("
            "str(os.getpid()) + ' ' + str(child.pid) + ' ' + str(os.getpgid(0)))\n"
            "time.sleep(60)\n"
        )
        started_group = os.getpgid(0)
        result = _run_agent(
            [sys.executable, "-c", script], cwd=self.root, env=os.environ.copy(), timeout=1
        )
        self.assertEqual(result.stderr, b"timed out")

        agent, child, group = map(int, record.read_text().split())
        self.assertEqual(group, started_group)
        for pid in (agent, child):
            result = subprocess.run(
                ["ps", "-o", "stat=", "-p", str(pid)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertTrue(not result.stdout.strip() or result.stdout.strip().startswith("Z"))

    def test_descendant_gets_grace_period_after_agent_exits(self):
        marker = self.root / "child-cleanup"
        child_script = (
            "import signal, time\n"
            "def cleanup(signum, frame):\n"
            "    time.sleep(0.5)\n"
            f"    open({str(marker)!r}, 'w').write('done')\n"
            "    raise SystemExit(0)\n"
            "signal.signal(signal.SIGTERM, cleanup)\n"
            "time.sleep(60)\n"
        )
        agent_script = (
            "import subprocess, sys, time\n"
            f"subprocess.Popen([sys.executable, '-c', {child_script!r}])\n"
            "time.sleep(60)\n"
        )
        result = _run_agent(
            [sys.executable, "-c", agent_script],
            cwd=self.root,
            env=os.environ.copy(),
            timeout=1,
        )
        self.assertEqual(result.stderr, b"timed out")
        self.assertTrue(marker.exists(), "descendant cleanup was cut short by SIGKILL")

    def test_patched_default_enforces_two_second_deadline(self):
        with patch.object(config_module, "DEFAULT_AGENT_TIMEOUT", 2):
            timeout = load_repo_config(self.root).agent_timeout
        result = _run_agent(
            [sys.executable, "-c", "import time; time.sleep(60)"],
            cwd=self.root,
            env=os.environ.copy(),
            timeout=timeout,
        )
        self.assertEqual(result.stderr, b"timed out")

    def test_zero_timeout_waits_for_normal_completion(self):
        started = time.monotonic()
        result = _run_agent(
            [sys.executable, "-c", "import time; time.sleep(3)"],
            cwd=self.root,
            env=os.environ.copy(),
            timeout=0,
        )
        self.assertEqual(result.returncode, 0)
        self.assertGreaterEqual(time.monotonic() - started, 3)
