import asyncio
import hashlib
import os
import signal
import stat
import subprocess
import sys
import time
from pathlib import Path

from mcp.server.mcpserver.exceptions import ToolError
from mcp_types import CallToolResult

from chitty.config import CHITTY_VERSION
from chitty.mcp import server
from chitty.store import Repo, next_action
from tests.test_cli import CliTestCase


class TestNext(CliTestCase):
    def add(self, title: str, *, status: str = "todo", **fields: object) -> str:
        args = ["add", title, "-d", "Description.", "-s", status]
        if priority := fields.get("priority"):
            args.extend(["--priority", str(priority)])
        if owner := fields.get("owner"):
            args.extend(["--owner", str(owner)])
        depends_on = fields.get("depends_on", [])
        assert isinstance(depends_on, list)
        for dependency in depends_on:
            args.extend(["--depends-on", str(dependency)])
        context = fields.get("context")
        if context:
            args.extend(["-c", str(context)])
        return self.json(*args)["id"]

    def test_selection_order_and_exclusions(self):
        cases = (
            (
                "review before all work",
                (("Todo", {}), ("Review", {"status": "review"})),
                ("review", "TASK-2"),
            ),
            (
                "doing before todo",
                (("Todo", {}), ("Doing", {"status": "doing"})),
                ("work", "TASK-2"),
            ),
            (
                "priority before identifier",
                (("Low", {"priority": "low"}), ("High", {"priority": "high"})),
                ("work", "TASK-2"),
            ),
            (
                "unset priority before low",
                (("Low", {"priority": "low"}), ("Unset", {})),
                ("work", "TASK-2"),
            ),
            (
                "unset priority ties medium and uses identifier",
                (("Unset", {}), ("Medium", {"priority": "medium"})),
                ("work", "TASK-1"),
            ),
        )
        for name, tasks, expected in cases:
            with self.subTest(name):
                for title, fields in tasks:
                    self.add(title, **fields)
                action = next_action(Repo.open(self.root))
                self.assertEqual((action.mode, str(action.id)), expected)
                for path in (self.root / "chitty/tasks").glob("*.md"):
                    path.unlink()

    def test_numeric_id_ordering_and_unmet_doing_dependency(self):
        for number in range(1, 13):
            self.add(f"Task {number}", status="blocked" if number < 9 else "todo")
        first = next_action(Repo.open(self.root))
        self.assertEqual(str(first.id), "TASK-9")
        dependency = self.add("Dependency")
        doing = self.add("Started", status="doing", depends_on=[dependency])
        self.assertEqual(str(next_action(Repo.open(self.root)).id), "TASK-14")
        self.assertEqual(doing, "TASK-14")

    def test_tie_breaks_across_contexts_by_task_id(self):
        config = self.root / "chitty.toml"
        config.write_text(config.read_text() + '\n[contexts.alpha]\nprefix = "ALPHA"\n')
        self.add("Task")
        self.add("Alpha", context="alpha")
        self.assertEqual(str(next_action(Repo.open(self.root)).id), "ALPHA-1")

    def test_selection_excludes_each_ineligible_ticket(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("[contexts.tasks]", "review = false\n\n[contexts.tasks]")
        )
        cases = (
            ("backlog", {"status": "backlog"}),
            ("blocked", {"status": "blocked"}),
            ("done", {"status": "done"}),
            ("human context", {"context": "human"}),
            ("human owner", {"owner": "human"}),
        )
        for title, fields in cases:
            with self.subTest(title):
                fallback = self.add("Fallback")
                self.add(title, **fields)
                self.assertEqual(str(next_action(Repo.open(self.root)).id), fallback)
                for path in (self.root / "chitty").glob("*/*.md"):
                    path.unlink()
        dependency = self.add("Unfinished", status="blocked")
        fallback = self.add("Fallback")
        self.add("Waiting", depends_on=[dependency])
        self.assertEqual(str(next_action(Repo.open(self.root)).id), fallback)
        for path in (self.root / "chitty/tasks").glob("*.md"):
            path.unlink()
        completed = self.add("Complete", status="done")
        ready = self.add("Ready", depends_on=[completed])
        self.assertEqual(str(next_action(Repo.open(self.root)).id), ready)
        for path in (self.root / "chitty/tasks").glob("*.md"):
            path.unlink()
        archived = self.add("Archived dependency")
        Repo.open(self.root).archive(Repo.open(self.root).resolve(archived))
        ready = self.add("Ready after archive", depends_on=[archived])
        self.assertEqual(str(next_action(Repo.open(self.root)).id), ready)

    def test_dependencies_human_and_ids(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("[contexts.tasks]", "review = false\n\n[contexts.tasks]")
        )
        completed = self.add("Complete", status="done")
        self.add("Ready", depends_on=[completed])
        dangling = self.add("Blocked")
        path = self.root / "chitty/tasks" / f"{dangling}--blocked.md"
        path.write_text(path.read_text().replace("created:", "depends_on:\n  - TASK-99\ncreated:"))
        self.add("Human context", context="human")
        self.add("Human owner", owner="human")
        with self.assertRaisesRegex(Exception, "TASK-99"):
            next_action(Repo.open(self.root))

    def test_cli_and_mcp_return_the_same_action(self):
        self.add("Todo")
        cli = self.json("next")
        result = asyncio.run(server.call_tool("next", {}))
        assert isinstance(result, CallToolResult)
        content = result.structured_content
        assert content is not None
        self.assertEqual(content.get("result", content), cli)

    def test_next_output_and_empty_queue(self):
        for number in range(1, 12):
            self.add(f"Blocked {number}", status="blocked")
        self.add("Todo")
        self.assertEqual(self.run_cli("next").stdout, "work TASK-12\n")
        self.assertEqual(
            self.run_cli("next", "--json").stdout, '{\n  "mode": "work",\n  "id": "TASK-12"\n}\n'
        )
        for path in (self.root / "chitty/tasks").glob("*.md"):
            path.unlink()
        result = self.run_cli("next", exit_code=1)
        self.assertEqual(result.stdout, "")
        self.assertIn("no next ticket", result.stderr)
        with self.assertRaisesRegex(ToolError, "no next ticket"):
            asyncio.run(server.call_tool("next", {}))

    def test_run_uses_committed_change_from_ticket_worktree(self):
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Todo")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        worker = self.tmp / "ticket-worktree"
        self.git("worktree", "add", "--quiet", "-b", "ticket", str(worker))
        self.addCleanup(self.git, "worktree", "remove", "--force", str(worker))
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import os, pathlib, subprocess, time\n"
            "path = pathlib.Path(os.environ['WORKER']) / 'chitty/tasks/TASK-1--todo.md'\n"
            "path.write_text(path.read_text().replace('status: todo', 'status: blocked'))\n"
            "time.sleep(1)\n"
            "subprocess.run(['git', 'add', str(path)], cwd=os.environ['WORKER'], check=True)\n"
            "subprocess.run(\n"
            "    ['git', 'commit', '-m', 'worker change'],\n"
            "    cwd=os.environ['WORKER'], check=True,\n"
            ")\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        old_path = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake.parent}:{old_path}"
        os.environ["WORKER"] = str(worker)
        try:
            result = self.run_cli("run")
        finally:
            os.environ["PATH"] = old_path
            os.environ.pop("WORKER", None)
        self.assertEqual(result.stdout, "TASK-1: todo → blocked\n")

    def test_run_inherits_stdin(self):
        self.add("Todo")
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import sys\n"
            "assert sys.stdin.read() == 'inherited input\\n'\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        command = [str(Path(sys.executable).parent / "chitty"), "run"]
        environment = os.environ | {"PATH": f"{fake.parent}:{os.environ.get('PATH', '')}"}
        result = subprocess.run(
            command,
            cwd=self.root,
            env=environment,
            input="inherited input\n",
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("TASK-1 was unchanged", result.stderr)

    def test_run_refreshes_setup_before_starting_pi(self):
        self.add("Todo")
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "base")
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace(CHITTY_VERSION, "0.0.0"))
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "stale setup")
        agent = self.tmp / "pi-agent"
        extension = agent / "extensions" / "chitty.ts"
        extension.parent.mkdir(parents=True)
        extension.write_text("old extension")
        (agent / "chitty-extension.sha256").write_text(
            hashlib.sha256(b"old extension").hexdigest() + "\n"
        )
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        seen = self.tmp / "seen-version"
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import os, pathlib, tomllib\n"
            "config = tomllib.loads(pathlib.Path('chitty.toml').read_text())\n"
            "pathlib.Path(os.environ['SEEN']).write_text(config['chitty_version'])\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        old_path = os.environ.get("PATH", "")
        os.environ.update(
            PATH=f"{fake.parent}:{old_path}", PI_CODING_AGENT_DIR=str(agent), SEEN=str(seen)
        )
        try:
            result = self.run_cli("run", exit_code=1)
        finally:
            os.environ["PATH"] = old_path
            os.environ.pop("PI_CODING_AGENT_DIR", None)
            os.environ.pop("SEEN", None)

        self.assertEqual(seen.read_text(), CHITTY_VERSION)
        self.assertNotEqual(extension.read_text(), "old extension")
        self.assertIn(str(config), result.stderr)
        self.assertNotIn("re-run `chitty init`", result.stderr)
        self.assertEqual(
            self.git("log", "-1", "--format=%s").strip(), "chitty: upgrade repository setup"
        )
        changed = self.git("show", "--format=", "--name-only", "HEAD").splitlines()
        self.assertTrue(set(changed) <= {"chitty.toml", "AGENTS.md", ".gitignore", "CLAUDE.md"})

    def test_run_replaces_an_outdated_extension_before_starting_pi(self):
        self.add("Todo")
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.run_cli("init")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "base")
        agent = self.tmp / "pi-agent"
        extension = agent / "extensions" / "chitty.ts"
        extension.parent.mkdir(parents=True)
        extension.write_text("old extension")
        (agent / "chitty-extension.sha256").write_text(
            hashlib.sha256(b"old extension").hexdigest() + "\n"
        )
        seen = self.tmp / "seen-extension"
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import os, pathlib\n"
            "agent = pathlib.Path(os.environ['PI_CODING_AGENT_DIR'])\n"
            "pathlib.Path(os.environ['SEEN']).write_bytes(\n"
            "    (agent / 'extensions/chitty.ts').read_bytes()\n)\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        old_path = os.environ.get("PATH", "")
        os.environ.update(
            PATH=f"{fake.parent}:{old_path}", PI_CODING_AGENT_DIR=str(agent), SEEN=str(seen)
        )
        try:
            self.run_cli("run", exit_code=1)
        finally:
            os.environ["PATH"] = old_path
            os.environ.pop("PI_CODING_AGENT_DIR", None)
            os.environ.pop("SEEN", None)

        self.assertNotEqual(seen.read_bytes(), b"old extension")

    def test_run_stops_before_pi_when_refresh_fails_or_setup_is_dirty(self):
        self.add("Todo")
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.run_cli("init")
        (self.root / "AGENTS.md").write_text("# Agents\n")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "base")
        marker = self.tmp / "pi-started"
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import os, pathlib\npathlib.Path(os.environ['MARKER']).touch()\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        old_path = os.environ.get("PATH", "")
        os.environ.update(PATH=f"{fake.parent}:{old_path}", MARKER=str(marker))
        try:
            config = self.root / "chitty.toml"
            config.write_text(config.read_text().replace(CHITTY_VERSION, "99.0.0"))
            self.git("add", "chitty.toml")
            self.git("commit", "--quiet", "-m", "newer setup")
            newer = self.run_cli("run", exit_code=1)
            self.assertIn("needs Chitty 99.0.0 or later", newer.stderr)
            self.assertFalse(marker.exists())
            config.write_text(config.read_text().replace("99.0.0", CHITTY_VERSION))
            self.git("add", "chitty.toml")
            self.git("commit", "--quiet", "-m", "current setup")
            agents = self.root / "AGENTS.md"
            agents.write_text(agents.read_text() + "local edit\n")
            dirty = self.run_cli("run", exit_code=1)
            self.assertIn("AGENTS.md", dirty.stderr)
            self.assertFalse(marker.exists())
            self.assertIn("local edit", agents.read_text())
            self.assertIn(" M AGENTS.md", self.git("status", "--short"))
        finally:
            os.environ["PATH"] = old_path
            os.environ.pop("MARKER", None)

    def test_run_refresh_is_silent_when_current_or_in_a_worktree(self):
        self.add("Todo")
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.run_cli("init")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "base")
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text("#!" + sys.executable + "\n")
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        old_path = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake.parent}:{old_path}"
        try:
            before = self.git("rev-parse", "HEAD")
            current = self.run_cli("run", exit_code=1)
            self.assertEqual(self.git("rev-parse", "HEAD"), before)
            self.assertNotIn("setup", current.stderr)
            worktree = self.tmp / "worktree"
            self.git("worktree", "add", "--quiet", "-b", "worker", str(worktree))
            self.addCleanup(self.git, "worktree", "remove", "--force", str(worktree))
            previous = Path.cwd()
            os.chdir(worktree)
            try:
                linked = self.run_cli("run", exit_code=1)
            finally:
                os.chdir(previous)
            self.assertEqual(self.git("rev-parse", "HEAD"), before)
            self.assertNotIn("setup", linked.stderr)
        finally:
            os.environ["PATH"] = old_path

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=self.root, capture_output=True, text=True, check=True
        ).stdout

    def test_run_cases(self):
        self.add("Todo")
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import os, sys\n"
            "assert os.getcwd() == os.environ['EXPECTED_ROOT']\n"
            "assert sys.stdin.read() == ''\n"
            "if os.environ.get('CHANGE'):\n"
            "    path = os.environ['TASK_PATH']\n"
            "    text = open(path).read()\n"
            "    open(path, 'w').write(text.replace('status: todo', 'status: blocked'))\n"
            "sys.exit(int(os.environ.get('PI_EXIT', '0')))\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        old_path = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake.parent}:{old_path}"
        os.environ["EXPECTED_ROOT"] = str(self.root)
        try:
            unchanged = self.run_cli("run", exit_code=1)
            self.assertIn("TASK-1 was unchanged", unchanged.stderr)
            os.environ["PI_EXIT"] = "7"
            failed = self.run_cli("run", exit_code=1)
            self.assertIn("pi exited with status 7", failed.stderr)
            os.environ.pop("PI_EXIT")
            os.environ["CHANGE"] = "1"
            os.environ["TASK_PATH"] = str(self.root / "chitty/tasks/TASK-1--todo.md")
            changed = self.run_cli("run")
            self.assertEqual(changed.stdout, "TASK-1: todo → blocked\n")
            no_next = self.run_cli("run", exit_code=1)
            self.assertIn("no next ticket", no_next.stderr)
            self.add("Again")
            os.environ["PATH"] = "/usr/bin:/bin"
            missing = self.run_cli("run", exit_code=1)
            self.assertIn("pi is not on PATH", missing.stderr)
            os.environ["PATH"] = f"{fake.parent}:{old_path}"
            signal_script = self.root / "bin" / "pi"
            signal_script.write_text(
                "#!" + sys.executable + "\n"
                "import os, sys, time\n"
                "sys.stderr = open(os.devnull, 'w')\n"
                "open(os.environ['CHILD_PID'], 'w').write(str(os.getpid()))\n"
                "time.sleep(60)\n"
            )
            child_pid = self.root / "child.pid"
            environment = os.environ | {"CHILD_PID": str(child_pid)}
            process = subprocess.Popen(
                [str(Path(sys.executable).parent / "chitty"), "run"],
                cwd=self.root,
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            try:
                for _ in range(100):
                    if child_pid.exists():
                        break
                    time.sleep(0.01)
                self.assertTrue(child_pid.exists())
                os.kill(int(child_pid.read_text()), signal.SIGINT)
                stdout, stderr = process.communicate(timeout=5)
            finally:
                if process.poll() is None:
                    process.kill()
                    process.communicate()
            self.assertEqual(process.returncode, 130, stdout + stderr)
            self.assertEqual(stdout, "")
            self.assertIn("interrupted while Pi was running", stderr)
            self.assertNotIn("Traceback", stderr)
        finally:
            os.environ["PATH"] = old_path
            os.environ.pop("EXPECTED_ROOT", None)
            os.environ.pop("PI_EXIT", None)
            os.environ.pop("CHANGE", None)
            os.environ.pop("TASK_PATH", None)
