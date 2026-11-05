import asyncio
import hashlib
import json
import os
import stat
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from mcp.server.mcpserver.exceptions import ToolError
from mcp_types import CallToolResult

from chitty.config import CHITTY_VERSION
from chitty.mcp import server
from chitty.store import Repo, guide, next_action
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
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Todo")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        worker = self.tmp / "ticket-worktree"
        self.git("worktree", "add", "--quiet", "-b", "task-1", str(worker))
        self.addCleanup(self.git, "worktree", "remove", "--force", str(worker))
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import os, pathlib, subprocess, time\n"
            "assert pathlib.Path.cwd() == pathlib.Path(os.environ['WORKER'])\n"
            "path = pathlib.Path(os.environ['WORKER']) / 'chitty/tasks/TASK-1--todo.md'\n"
            "path.write_text(path.read_text().replace('status: doing', 'status: blocked'))\n"
            "time.sleep(1)\n"
            "subprocess.run(['git', 'add', str(path)], cwd=os.environ['WORKER'], check=True)\n"
            "subprocess.run(\n"
            "    ['git', 'commit', '--quiet', '-m', 'worker change'],\n"
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
        self.assertEqual(result.stdout, "TASK-1: doing → blocked\n")
        self.assertEqual(self.git("-C", str(worker), "branch", "--show-current").strip(), "task-1")
        self.assertIn(
            "status: todo",
            (self.root / "chitty/tasks/TASK-1--todo.md").read_text(),
        )
        self.assertIn(
            "chitty: edit TASK-1",
            self.git("log", "--format=%s", "main..task-1"),
        )

    def test_run_reports_success_when_agent_merges_and_removes_worktree(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Todo")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        worker = self.root / ".worktrees" / "task-1"
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import os, pathlib, subprocess\n"
            "worker = pathlib.Path.cwd()\n"
            "path = worker / 'chitty/tasks/TASK-1--todo.md'\n"
            "path.write_text(path.read_text().replace('status: doing', 'status: done'))\n"
            "subprocess.run(['git', 'add', str(path)], check=True)\n"
            "subprocess.run(['git', 'commit', '--quiet', '-m', 'finish'], check=True)\n"
            "main = pathlib.Path(os.environ['MAIN'])\n"
            "subprocess.run(['git', '-C', str(main), 'merge', '--quiet', 'task-1'], check=True)\n"
            "subprocess.run([\n"
            "    'git', '-C', str(main), 'worktree', 'remove', '--force', str(worker)\n"
            "], check=True)\n"
            "subprocess.run(['git', '-C', str(main), 'branch', '-D', 'task-1'], check=True)\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        previous = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake.parent}:{previous}"
        os.environ["MAIN"] = str(self.root)
        try:
            result = self.run_cli("run")
        finally:
            os.environ["PATH"] = previous
            os.environ.pop("MAIN", None)
        self.assertEqual(result.stdout, "TASK-1: doing → done\n")
        self.assertFalse(worker.exists())
        self.assertEqual(self.git("branch", "--list", "task-1"), "")

    def test_run_reports_status_when_agent_removes_worktree_but_keeps_branch(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Work")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import os, pathlib, subprocess\n"
            "worker = pathlib.Path.cwd()\n"
            "path = next((worker / 'chitty/tasks').glob('TASK-*.md'))\n"
            "status = os.environ['TARGET_STATUS']\n"
            "text = path.read_text().replace('status: doing', f'status: {status}')\n"
            "text = text.replace('status: review', f'status: {status}')\n"
            "path.write_text(text)\n"
            "subprocess.run(['git', 'add', str(path)], check=True)\n"
            "subprocess.run(['git', 'commit', '--quiet', '-m', 'finish'], check=True)\n"
            "subprocess.run([\n"
            "    'git', '-C', os.environ['MAIN'], 'worktree', 'remove', '--force', str(worker)\n"
            "], check=True)\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        previous = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake.parent}:{previous}"
        os.environ["MAIN"] = str(self.root)
        os.environ["TARGET_STATUS"] = "blocked"
        try:
            result = self.run_cli("run")
        finally:
            os.environ["PATH"] = previous
            os.environ.pop("MAIN", None)
            os.environ.pop("TARGET_STATUS", None)
        self.assertEqual(result.stdout, "TASK-1: doing → blocked\n")

        self.add("Review", status="review")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "review")
        self.git("branch", "task-2")
        os.environ["PATH"] = f"{fake.parent}:{previous}"
        os.environ["MAIN"] = str(self.root)
        os.environ["TARGET_STATUS"] = "done"
        try:
            result = self.run_cli("run")
        finally:
            os.environ["PATH"] = previous
            os.environ.pop("MAIN", None)
            os.environ.pop("TARGET_STATUS", None)
        self.assertEqual(result.stdout, "TASK-2: review → done\n")

    def test_run_rejects_lost_ticket_when_worktree_and_branch_are_removed(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Work")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import os, pathlib, subprocess\n"
            "main = pathlib.Path(os.environ['MAIN'])\n"
            "worker = pathlib.Path.cwd()\n"
            "branch = subprocess.check_output(\n"
            "    ['git', 'branch', '--show-current'], text=True\n"
            ").strip()\n"
            "subprocess.run([\n"
            "    'git', '-C', str(main), 'worktree', 'remove', '--force', str(worker)\n"
            "], check=True)\n"
            "subprocess.run(['git', '-C', str(main), 'branch', '-D', branch], check=True)\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        previous = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake.parent}:{previous}"
        os.environ["MAIN"] = str(self.root)
        try:
            result = self.run_cli("run", exit_code=1)
        finally:
            os.environ["PATH"] = previous
            os.environ.pop("MAIN", None)
        self.assertIn("TASK-1", result.stderr)
        self.assertIn("worktree and branch were removed", result.stderr)

        self.add("Review", status="review")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "review")
        self.git("branch", "task-2")
        os.environ["PATH"] = f"{fake.parent}:{previous}"
        os.environ["MAIN"] = str(self.root)
        try:
            result = self.run_cli("run", exit_code=1)
        finally:
            os.environ["PATH"] = previous
            os.environ.pop("MAIN", None)
        self.assertIn("TASK-2", result.stderr)
        self.assertIn("worktree and branch were removed", result.stderr)

    def test_run_inherits_stdin(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Todo")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
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
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
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
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
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
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
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
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
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

    def test_run_refuses_preflight_without_mutating(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Todo")
        cases = (
            (
                "autocommit",
                lambda text: text.replace("autocommit = true", "autocommit = false"),
                None,
            ),
            ("setup", lambda text: text.replace('setup = "true"\n', ""), None),
            (
                "unset",
                lambda text: text.replace('agent_command = "pi --chitty-{mode} {id}"\n', ""),
                None,
            ),
            (
                "blank",
                lambda text: text.replace(
                    'agent_command = "pi --chitty-{mode} {id}"', 'agent_command = " "'
                ),
                None,
            ),
            (
                "quotes",
                lambda text: text.replace(
                    'agent_command = "pi --chitty-{mode} {id}"',
                    'agent_command = "pi \' --chitty-{mode} {id}"',
                ),
                None,
            ),
            ("mode", lambda text: text.replace("{mode}", "work"), None),
            ("id", lambda text: text.replace("{id}", "TASK-1"), None),
            ("relative", lambda text: text.replace("pi --chitty", "bin/pi --chitty"), None),
            ("missing", lambda text: text.replace("pi --chitty", "missing-agent --chitty"), None),
            ("branch", lambda text: text, None),
        )
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        original = config.read_text()
        for name, change, path in cases:
            with self.subTest(name):
                config.write_text(change(original))
                if name != "branch":
                    self.git("add", "chitty.toml")
                    self.git("commit", "--quiet", "-m", f"invalid {name} agent command")
                if name == "branch":
                    self.git("branch", "-M", "wrong")
                previous = os.environ.get("PATH")
                if path is not None:
                    os.environ["PATH"] = path
                try:
                    result = self.run_cli("run", exit_code=1)
                finally:
                    if path is not None:
                        if previous is None:
                            os.environ.pop("PATH")
                        else:
                            os.environ["PATH"] = previous
                    if name == "branch":
                        self.git("branch", "-M", "main")
                expected = {
                    "autocommit": "requires autocommit",
                    "setup": "requires setup",
                    "unset": "agent_command",
                    "blank": "agent_command",
                    "quotes": "agent_command",
                    "mode": "agent_command",
                    "id": "agent_command",
                    "relative": "agent_command",
                    "missing": "agent_command",
                    "branch": "must be on branch main",
                }[name]
                self.assertIn(expected, result.stderr)
                self.assertFalse((self.root / ".worktrees").exists())
                self.assertEqual(
                    Repo.open(self.root)
                    .find(Repo.open(self.root).resolve("TASK-1"))
                    .task.frontmatter.status,
                    "todo",
                )
                config.write_text(original)

    def test_run_setup_failure_does_not_start_pi_or_claim_ticket(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "false"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Todo")
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "configure setup")
        marker = self.root / "started"
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text(
            "#!"
            + sys.executable
            + "\nfrom pathlib import Path\nPath('started').write_text('yes')\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        previous = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake.parent}:{previous}"
        try:
            result = self.run_cli("run", exit_code=1)
        finally:
            os.environ["PATH"] = previous
        self.assertIn("setup exited with status 1", result.stderr)
        self.assertFalse(marker.exists())
        worktree = self.root / ".worktrees" / "task-1"
        self.assertTrue(worktree.is_dir())
        self.assertEqual(
            Repo.open(worktree).find(Repo.open(worktree).resolve("TASK-1")).task.frontmatter.status,
            "todo",
        )

    def test_run_adds_worktree_for_existing_branch_and_refuses_unbranched_review(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Todo")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        self.git("branch", "task-1")
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import os\n"
            "assert os.getcwd() == os.environ['EXPECTED_ROOT']\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        previous = os.environ.get("PATH", "")
        previous_root = os.environ.get("EXPECTED_ROOT")
        os.environ["PATH"] = f"{fake.parent}:{previous}"
        os.environ["EXPECTED_ROOT"] = str(self.root / ".worktrees" / "task-1")
        try:
            unchanged = self.run_cli("run", exit_code=1)
        finally:
            os.environ["PATH"] = previous
            if previous_root is None:
                os.environ.pop("EXPECTED_ROOT", None)
            else:
                os.environ["EXPECTED_ROOT"] = previous_root
        self.assertIn("TASK-1 was unchanged", unchanged.stderr)
        worktree = self.root / ".worktrees" / "task-1"
        self.assertEqual(
            self.git("-C", str(worktree), "branch", "--show-current").strip(), "task-1"
        )
        self.assertEqual(
            Repo.open(worktree).find(Repo.open(worktree).resolve("TASK-1")).task.frontmatter.status,
            "doing",
        )

        self.git("worktree", "remove", "--force", str(worktree))
        self.git("branch", "-D", "task-1")
        self.run_cli("edit", "TASK-1", "--status", "review")
        result = self.run_cli("run", exit_code=1)
        self.assertIn("review ticket TASK-1 has no branch task-1", result.stderr)
        self.assertFalse(worktree.exists())

    def test_run_reviews_branch_with_newer_config_key(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Review me")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        self.run_cli("edit", "TASK-1", "--status", "review")
        self.git("branch", "task-1")
        branch_worktree = self.root / ".worktrees" / "prepare-task-1"
        self.git("worktree", "add", "--quiet", str(branch_worktree), "task-1")
        branch_config = branch_worktree / "chitty.toml"
        branch_config.write_text(
            branch_config.read_text().replace(
                f'chitty_version = "{CHITTY_VERSION}"',
                'chitty_version = "99.0.0"\nnew_setting = "supported later"',
            )
        )
        self.git("-C", str(branch_worktree), "add", "chitty.toml")
        self.git("-C", str(branch_worktree), "commit", "--quiet", "-m", "new config")
        self.git("worktree", "remove", "--force", str(branch_worktree))
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import subprocess\n"
            "path = 'chitty/tasks/TASK-1--review-me.md'\n"
            "text = open(path).read().replace('status: review', 'status: done')\n"
            "open(path, 'w').write(text)\n"
            "subprocess.run(['git', 'add', path], check=True)\n"
            "subprocess.run(['git', 'commit', '--quiet', '-m', 'finish review'], check=True)\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        previous = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake.parent}:{previous}"
        try:
            result = self.run_cli("run")
        finally:
            os.environ["PATH"] = previous

        self.assertEqual(result.stdout, "TASK-1: review → done\n")

    def test_run_cases(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.run_cli("init")
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Todo")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        main_head = self.git("rev-parse", "main").strip()
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import os, subprocess, sys\n"
            "assert os.getcwd() == os.environ['EXPECTED_ROOT']\n"
            "assert sys.stdin.read() == ''\n"
            "if os.environ.get('CHANGE'):\n"
            "    path = os.environ['TASK_PATH']\n"
            "    text = open(path).read()\n"
            "    open(path, 'w').write(text.replace('status: doing', 'status: blocked'))\n"
            "    subprocess.run(['git', 'add', path], check=True)\n"
            "    subprocess.run(['git', 'commit', '--quiet', '-m', 'worker change'], check=True)\n"
            "sys.exit(int(os.environ.get('PI_EXIT', '0')))\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        old_path = os.environ.get("PATH", "")
        main_status = self.git("status", "--porcelain")
        os.environ["PATH"] = f"{fake.parent}:{old_path}"
        os.environ["EXPECTED_ROOT"] = str(self.root / ".worktrees" / "task-1")
        try:
            unchanged = self.run_cli("run", exit_code=1)
            self.assertIn("TASK-1 was unchanged", unchanged.stderr)
            worktree = self.root / ".worktrees" / "task-1"
            self.assertEqual(
                self.git("-C", str(worktree), "branch", "--show-current").strip(), "task-1"
            )
            self.assertEqual(
                Repo.open(worktree)
                .find(Repo.open(worktree).resolve("TASK-1"))
                .task.frontmatter.status,
                "doing",
            )
            self.assertEqual(self.git("rev-parse", "main").strip(), main_head)
            self.assertEqual(self.git("status", "--porcelain"), main_status)
            self.assertEqual(self.git("rev-list", "--count", "main..task-1").strip(), "1")
            os.environ["PI_EXIT"] = "7"
            failed = self.run_cli("run", exit_code=1)
            self.assertIn("agent exited with status 7", failed.stderr)
            self.assertEqual(self.git("rev-list", "--count", "main..task-1").strip(), "1")
            os.environ.pop("PI_EXIT")
            os.environ["CHANGE"] = "1"
            os.environ["TASK_PATH"] = str(
                self.root / ".worktrees" / "task-1" / "chitty/tasks/TASK-1--todo.md"
            )
            changed = self.run_cli("run")
            self.assertEqual(changed.stdout, "TASK-1: doing → blocked\n")
            no_next = self.run_cli("run", exit_code=1)
            self.assertIn("no next ticket", no_next.stderr)
            self.add("Again")
            os.environ["PATH"] = "/usr/bin:/bin"
            missing = self.run_cli("run", exit_code=1)
            self.assertIn("agent_command executable is not on PATH", missing.stderr)
            os.environ["PATH"] = f"{fake.parent}:{old_path}"
        finally:
            os.environ["PATH"] = old_path
            os.environ.pop("EXPECTED_ROOT", None)
            os.environ.pop("PI_EXIT", None)
            os.environ.pop("CHANGE", None)
            os.environ.pop("TASK_PATH", None)

    def test_run_records_usage_outside_repository_and_appends_runs(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("First")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import json, os, pathlib, subprocess\n"
            "root = pathlib.Path.cwd()\n"
            "ticket = next((root / 'chitty/tasks').glob('*.md'))\n"
            "ticket.write_text(ticket.read_text().replace('status: doing', 'status: blocked'))\n"
            "sessions = {\n"
            "  'first-session': [\n"
            "    {'provider': 'p', 'model': 'a', 'input': 1, 'output': 2,\n"
            "     'cacheRead': 3, 'cacheWrite': 4, 'cost': 0.5},\n"
            "    {'provider': 'p', 'model': 'a', 'input': 5, 'output': 6,\n"
            "     'cacheRead': 7, 'cacheWrite': 8, 'cost': 1.5}],\n"
            "  'second-session': [{'provider': 'p', 'model': 'b',\n"
            "    'input': 9, 'output': 10, 'cacheRead': 11,\n"
            "    'cacheWrite': 12, 'cost': 2.5}]\n"
            "}\n"
            "path = pathlib.Path(os.environ['CHITTY_USAGE_FILE'])\n"
            "path.write_text(json.dumps({'sessions': sessions}))\n"
            "subprocess.run(['git', 'add', str(ticket)], check=True)\n"
            "subprocess.run(['git', 'commit', '--quiet', '-m', 'worker change'], check=True)\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        old_path = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake.parent}:{old_path}"
        try:
            self.assertEqual(self.run_cli("run").stdout, "TASK-1: doing → blocked\n")
            self.add("Second")
            self.git("add", "--all")
            self.git("commit", "--quiet", "-m", "second ticket")
            self.assertEqual(self.run_cli("run").stdout, "TASK-2: doing → blocked\n")
        finally:
            os.environ["PATH"] = old_path

        log = self.tmp / "data" / "chitty" / "usage" / "repo.jsonl"
        records = [json.loads(line) for line in log.read_text().splitlines()]
        self.assertEqual(len(records), 2)
        self.assertEqual(
            set(records[0]),
            {
                "ticket",
                "mode",
                "actor",
                "started",
                "seconds",
                "status_before",
                "status_after",
                "models",
            },
        )
        self.assertEqual(
            records[0]["models"],
            [
                {
                    "provider": "p",
                    "model": "a",
                    "input": 6,
                    "output": 8,
                    "cacheRead": 10,
                    "cacheWrite": 12,
                    "cost": 2.0,
                },
                {
                    "provider": "p",
                    "model": "b",
                    "input": 9,
                    "output": 10,
                    "cacheRead": 11,
                    "cacheWrite": 12,
                    "cost": 2.5,
                },
            ],
        )
        self.assertEqual(records[0]["status_before"], "doing")
        self.assertEqual(records[0]["status_after"], "blocked")
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_run_forwards_arguments_and_uses_a_fresh_actor_per_invocation(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("First")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import os, pathlib, subprocess, sys\n"
            "root = pathlib.Path(os.getcwd())\n"
            "(root / 'pi-arguments').write_text(repr(sys.argv[1:]))\n"
            "(root / 'pi-session-id').write_text(os.environ['CHITTY_PI_SESSION_ID'])\n"
            "chitty = str(pathlib.Path(sys.executable).with_name('chitty'))\n"
            "subprocess.run([chitty, 'edit', sys.argv[2], '--status', 'blocked', "
            "'--note', 'fake Pi write'], check=True, stdout=subprocess.DEVNULL)\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        previous = {
            name: os.environ.get(name)
            for name in ("PATH", "CHITTY_ACTOR", "CLAUDE_CODE_SESSION_ID")
        }
        os.environ["PATH"] = f"{fake.parent}:{previous['PATH']}"
        os.environ["CHITTY_ACTOR"] = "fixed-actor"
        os.environ["CLAUDE_CODE_SESSION_ID"] = "fixed-session"
        try:
            self.assertEqual(
                self.run_cli("run", "--", "--from-test").stdout, "TASK-1: doing → blocked\n"
            )
            worktree = self.root / ".worktrees" / "task-1"
            self.assertEqual(
                (worktree / "pi-arguments").read_text(),
                "['--chitty-work', 'TASK-1', '--from-test']",
            )
            history = (
                Repo.open(worktree)
                .find(Repo.open(worktree).resolve("TASK-1"))
                .task.section("History")
            )
            assert history is not None
            actors = {
                line.split()[2]
                for line in history.splitlines()
                if "todo → doing" in line or "doing → blocked" in line
            }
            self.assertEqual(len(actors), 1)
            self.assertNotIn("fixed-actor", actors)
            first_session_id = (worktree / "pi-session-id").read_text()

            os.environ["CHITTY_ACTOR"] = "test-agent"
            self.add("Second")
            self.git("add", "--all")
            self.git("commit", "--quiet", "-m", "add second ticket")
            os.environ["CHITTY_ACTOR"] = "fixed-actor"
            os.environ["CLAUDE_CODE_SESSION_ID"] = "fixed-session"
            self.assertEqual(self.run_cli("run").stdout, "TASK-2: doing → blocked\n")
            second = self.root / ".worktrees" / "task-2"
            second_history = (
                Repo.open(second).find(Repo.open(second).resolve("TASK-2")).task.section("History")
            )
            assert second_history is not None
            second_actor = second_history.splitlines()[-1].split()[2]
            self.assertNotIn("fixed-actor", {second_actor})
            second_session_id = (second / "pi-session-id").read_text()
            self.assertNotEqual(first_session_id, second_session_id)
        finally:
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

    def test_run_pulls_inbox_only_for_a_project(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace('project = "chitty"\n', "")
            .replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        config.write_text(
            "\n".join(
                line for line in config.read_text().splitlines() if not line.startswith("project =")
            )
            + "\n"
        )
        self.add("Todo")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text("#!" + sys.executable + "\n")
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        previous = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake.parent}:{previous}"
        self.assertIsNone(Repo.open(self.root).config.project)
        try:
            config.write_text('project = "demo"\n' + config.read_text())
            self.git("add", "chitty.toml")
            self.git("commit", "--quiet", "-m", "configure project")
            worktree = self.root / ".worktrees" / "task-1"

            def pull_before_selection(repo: Repo) -> list[str]:
                # Inbox pull must finish before selecting or claiming the ticket.
                self.assertEqual(repo.find(repo.resolve("TASK-1")).task.frontmatter.status, "todo")
                self.assertFalse(worktree.exists())
                self.assertEqual(self.git("branch", "--list", "task-1"), "")
                return []

            with patch("chitty.run.pull_suggestions", side_effect=pull_before_selection) as pull:
                self.run_cli("run", exit_code=1)
                pull.assert_called_once()

            config.write_text(
                "\n".join(
                    line
                    for line in config.read_text().splitlines()
                    if not line.startswith("project =")
                )
                + "\n"
            )
            self.git("add", "chitty.toml")
            self.git("commit", "--quiet", "-m", "remove project")
            with patch("chitty.run.pull_suggestions") as pull:
                self.run_cli("run", exit_code=1)
                pull.assert_not_called()
        finally:
            os.environ["PATH"] = previous

    def test_run_runs_setup_before_claim_and_leaves_review_unchanged(self):
        setup = self.root / "setup.py"
        setup.write_text(
            "from pathlib import Path\n"
            "import sys\n"
            "assert sys.argv[1:] == ['&&', 'touch', 'interpreted']\n"
            "ticket = Path('chitty/tasks/TASK-1--todo.md')\n"
            "if 'status: todo' in ticket.read_text():\n"
            "    assert ticket.read_text().count('status: todo') == 1\n"
            "count = int(Path('setup-ran').read_text()) if Path('setup-ran').exists() else 0\n"
            "Path('setup-ran').write_text(str(count + 1))\n"
        )
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace(
                "autocommit = false",
                f'autocommit = true\nsetup = "{sys.executable} {setup} && touch interpreted"',
            )
            .replace(
                'agent_command = "pi --chitty-{mode} {id}"',
                'agent_command = "~/bin/fake-agent \\"{prompt}\\""',
            )
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Todo")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        fake = self.tmp / "home" / "bin" / "fake-agent"
        fake.parent.mkdir(parents=True)
        fake.write_text(
            "#!" + sys.executable + "\n"
            "from pathlib import Path\n"
            "import os, sys\n"
            "status = Path('chitty/tasks/TASK-1--todo.md').read_text()\n"
            "name = 'work' if 'status: doing' in status else 'review'\n"
            "Path('agent-arguments-' + name).write_text(repr(sys.argv[1:]))\n"
            "assert len(sys.argv[1:]) == 1\n"
            "assert '\\n' in sys.argv[1]\n"
            "assert os.getcwd() == os.environ['EXPECTED_ROOT']\n"
            "assert Path('setup-ran').read_text() in {'1', '2', '3'}\n"
            "Path('pi-ran').write_text('yes')\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        previous = os.environ.get("PATH", "")
        previous_root = os.environ.get("EXPECTED_ROOT")
        worktree = self.root / ".worktrees" / "task-1"
        os.environ["PATH"] = f"{fake.parent}:{previous}"
        os.environ["EXPECTED_ROOT"] = str(worktree)
        try:
            result = self.run_cli("run", exit_code=1)
            repeated = self.run_cli("run", exit_code=1)
        finally:
            os.environ["PATH"] = previous
            if previous_root is None:
                os.environ.pop("EXPECTED_ROOT", None)
            else:
                os.environ["EXPECTED_ROOT"] = previous_root
        self.assertIn("TASK-1 was unchanged", result.stderr)
        self.assertIn("TASK-1 was unchanged", repeated.stderr)
        self.assertTrue((worktree / "pi-ran").exists())
        self.assertEqual(
            (worktree / "agent-arguments-work").read_text(), repr([guide("work", "TASK-1")])
        )
        self.assertEqual((worktree / "setup-ran").read_text(), "2")
        self.assertFalse((worktree / "interpreted").exists())

        self.git("worktree", "remove", "--force", str(worktree))
        self.git("branch", "-D", "task-1")
        self.run_cli("edit", "TASK-1", "--status", "review")
        self.git("worktree", "add", "--quiet", "-b", "task-1", str(worktree))
        os.environ["PATH"] = f"{fake.parent}:{previous}"
        os.environ["EXPECTED_ROOT"] = str(worktree)
        try:
            review = self.run_cli("run", exit_code=1)
        finally:
            os.environ["PATH"] = previous
            os.environ.pop("EXPECTED_ROOT", None)
        self.assertIn("TASK-1 was unchanged", review.stderr)
        review_prompt = (worktree / "agent-arguments-review").read_text()
        self.assertEqual(review_prompt, repr([guide("review", "TASK-1")]))
        self.assertIn('"', review_prompt)
        self.assertEqual(
            Repo.open(worktree).find(Repo.open(worktree).resolve("TASK-1")).task.frontmatter.status,
            "review",
        )

    def test_run_from_linked_worktree_refuses_older_main_setup(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Todo")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        worktree = self.tmp / "worker"
        self.git("worktree", "add", "--quiet", "-b", "worker", str(worktree))
        self.addCleanup(self.git, "worktree", "remove", "--force", str(worktree))
        config.write_text(config.read_text().replace(CHITTY_VERSION, "0.0.1"))
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "older setup")
        before = self.git("rev-parse", "HEAD")
        main_config = config.read_text()
        marker = self.tmp / "agent-started"
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\n"
            "from pathlib import Path\n"
            "Path(" + repr(str(marker)) + ").touch()\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        previous_path = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake.parent}:{previous_path}"
        previous_cwd = os.getcwd()
        os.chdir(worktree)
        try:
            result = self.run_cli("run", exit_code=1)
        finally:
            os.chdir(previous_cwd)
            os.environ["PATH"] = previous_path
        self.assertIn(CHITTY_VERSION, result.stderr)
        self.assertIn("0.0.1", result.stderr)
        self.assertIn("from the main checkout", result.stderr)
        self.assertEqual(self.git("rev-parse", "HEAD"), before)
        self.assertEqual(config.read_text(), main_config)
        self.assertFalse(marker.exists())

    def test_run_from_another_worktree_uses_the_branch_not_main(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Todo")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        self.git("branch", "task-1")
        self.run_cli("edit", "TASK-1", "--note", "newer copy on main")
        other = self.tmp / "other"
        self.git("worktree", "add", "--quiet", "-b", "other", str(other))
        self.addCleanup(self.git, "worktree", "remove", "--force", str(other))
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import os, subprocess\n"
            "assert os.getcwd() == os.environ['EXPECTED_ROOT']\n"
            "path = 'chitty/tasks/TASK-1--todo.md'\n"
            "text = open(path).read().replace('status: doing', 'status: blocked')\n"
            "open(path, 'w').write(text)\n"
            "subprocess.run(['git', 'add', path], check=True)\n"
            "subprocess.run(['git', 'commit', '--quiet', '-m', 'worker change'], check=True)\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        previous_path = os.environ.get("PATH", "")
        previous_root = os.environ.get("EXPECTED_ROOT")
        target = self.root / ".worktrees" / "task-1"
        os.environ["PATH"] = f"{fake.parent}:{previous_path}"
        os.environ["EXPECTED_ROOT"] = str(target)
        previous_cwd = os.getcwd()
        os.chdir(other)
        try:
            result = self.run_cli("run", exit_code=1)
        finally:
            os.chdir(previous_cwd)
            os.environ["PATH"] = previous_path
            if previous_root is None:
                os.environ.pop("EXPECTED_ROOT", None)
            else:
                os.environ["EXPECTED_ROOT"] = previous_root
        self.assertIn("latest committed version is on branch main", result.stderr)
        self.assertEqual(self.git("-C", str(target), "branch", "--show-current").strip(), "task-1")

    def test_run_refuses_an_uncommitted_ticket_in_main(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Todo")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text("#!" + sys.executable + "\n")
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        ticket = self.root / "chitty/tasks/TASK-1--todo.md"
        ticket.write_text(ticket.read_text().replace("Description.", "Description changed."))
        previous = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake.parent}:{previous}"
        try:
            result = self.run_cli("run", exit_code=1)
        finally:
            os.environ["PATH"] = previous
        self.assertIn("has uncommitted changes in the main checkout", result.stderr)
        self.assertFalse((self.root / ".worktrees").exists())
