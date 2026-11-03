import asyncio
import os
import stat
import subprocess
import sys
from pathlib import Path

from mcp.server.mcpserver.exceptions import ToolError
from mcp_types import CallToolResult

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
            self.add(f"Task {number}")
        first = next_action(Repo.open(self.root))
        self.assertEqual(str(first.id), "TASK-1")
        self.add("Dependency")
        doing = self.add("Started", status="doing", depends_on=["TASK-13"])
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
            "if os.environ.get('INTERRUPT'):\n"
            "    import signal\n"
            "    os.kill(os.getppid(), signal.SIGINT)\n"
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
            os.environ["INTERRUPT"] = "1"
            interrupted = self.run_cli("run", exit_code=130)
            self.assertIn("interrupted while Pi was running", interrupted.stderr)
        finally:
            os.environ["PATH"] = old_path
            os.environ.pop("EXPECTED_ROOT", None)
            os.environ.pop("PI_EXIT", None)
            os.environ.pop("CHANGE", None)
            os.environ.pop("TASK_PATH", None)
            os.environ.pop("INTERRUPT", None)
