import asyncio
import hashlib
import io
import json
import os
import stat
import subprocess
import sys
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch
from uuid import UUID

from mcp.server.mcpserver.exceptions import ToolError
from mcp_types import CallToolResult

from chitty.config import CHITTY_VERSION
from chitty.errors import ChittyError
from chitty.inbox import suggest
from chitty.mcp import server
from chitty.run import _record_usage, run_loop
from chitty.store import Repo, guide, next_action, ticket_action
from tests.test_cli import CliTestCase


class TestNext(CliTestCase):
    def install_fake_pi(self, body: str) -> None:
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir(exist_ok=True)
        fake.write_text("#!" + sys.executable + "\n" + body)
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        environment = patch.dict(
            os.environ, {"PATH": f"{fake.parent}:{os.environ.get('PATH', '')}"}
        )
        environment.start()
        self.addCleanup(environment.stop)

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

    def test_configured_job_order_and_omitted_status(self):
        self.add("Review", status="review")
        todo = self.add("Todo")
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace(
                "autocommit = false", 'job_order = ["todo", "review"]\nautocommit = false'
            )
        )
        self.assertEqual(str(next_action(Repo.open(self.root)).id), todo)
        config.write_text(config.read_text().replace('["todo", "review"]', '["todo"]'))
        for path in (self.root / "chitty/tasks").glob("*.md"):
            if path.name.startswith(f"{todo}--"):
                path.unlink()
        with self.assertRaisesRegex(ChittyError, "no next ticket"):
            next_action(Repo.open(self.root))

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

    def test_unselected_owner_dependency_is_not_read(self):
        dependency = self.add("Dependency", status="blocked")
        self.add("Agent-owned", owner="agent", depends_on=[dependency])
        ready = self.add("Ready")
        with patch("chitty.store._dependency_is_done", side_effect=AssertionError("read")):
            self.assertEqual(str(next_action(Repo.open(self.root)).id), ready)

    def test_todo_dependency_must_be_done_on_main(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", "autocommit = false\nreview = false")
        )
        dependency = self.add("Dependency")
        waiting = self.add("Waiting", depends_on=[dependency])
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "test")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        self.git("branch", "worker")
        self.git("checkout", "--quiet", "worker")
        self.run_cli("edit", dependency, "-s", "done")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "finish dependency")
        self.git("checkout", "--quiet", "main")

        with self.assertRaisesRegex(ChittyError, "no next ticket"):
            next_action(Repo.open(self.root))

        self.git("merge", "--quiet", "worker")
        self.git("branch", "-D", "worker")
        self.assertEqual(str(next_action(Repo.open(self.root)).id), waiting)

        self.git("checkout", "--quiet", "-b", "rename")
        self.run_cli("edit", dependency, "--title", "Renamed dependency")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "rename dependency")
        self.git("checkout", "--quiet", "main")
        self.git("merge", "--quiet", "rename")
        self.git("branch", "-D", "rename")
        self.assertEqual(str(next_action(Repo.open(self.root)).id), waiting)

    def test_unmerged_archive_does_not_complete_dependency(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", "autocommit = false\nreview = false")
        )
        dependency = self.add("Dependency", status="blocked")
        waiting = self.add("Waiting", depends_on=[dependency])
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "test")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        self.git("branch", "worker")
        self.git("checkout", "--quiet", "worker")
        self.run_cli("edit", dependency, "-s", "done")
        self.run_cli("archive", dependency)
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "archive dependency")
        self.git("checkout", "--quiet", "main")
        with self.assertRaisesRegex(ChittyError, "no next ticket"):
            next_action(Repo.open(self.root))
        self.git("merge", "--quiet", "worker")
        self.git("branch", "-D", "worker")
        self.assertEqual(str(next_action(Repo.open(self.root)).id), waiting)

    def test_no_main_keeps_dependency_behavior_and_human_context_works(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", "autocommit = false\nreview = false")
        )
        dependency = self.add("Dependency", status="done")
        waiting = self.add("Waiting", depends_on=[dependency])
        human_dependency = self.add("Human dependency", context="human", status="done")
        human_waiting = self.add("Human waiting", depends_on=[human_dependency])
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "test")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        self.assertEqual(str(next_action(Repo.open(self.root)).id), waiting)
        self.assertNotEqual(waiting, human_waiting)

    def test_dependencies_human_and_ids(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("[contexts.tasks]", "review = false\n\n[contexts.tasks]")
        )
        completed = self.add("Complete", status="done")
        ready = self.add("Ready", depends_on=[completed])
        dangling = self.add("Blocked")
        path = self.root / "chitty/tasks" / f"{dangling}--blocked.md"
        path.write_text(path.read_text().replace("created:", "depends_on:\n  - TASK-99\ncreated:"))
        self.add("Human context", context="human")
        self.add("Human owner", owner="human")
        self.assertEqual(str(next_action(Repo.open(self.root)).id), ready)

    def test_cli_and_mcp_return_the_same_action(self):
        self.add("Todo")
        cli = self.json("next")
        result = asyncio.run(server.call_tool("next", {}))
        assert isinstance(result, CallToolResult)
        content = result.structured_content
        assert content is not None
        self.assertEqual(content.get("result", content), cli)

    def test_explicit_ticket_action_validates_status_and_dependencies(self):
        cases = (
            ("blocked", {"status": "blocked"}, "status is blocked"),
            ("human owner", {"owner": "human"}, "owner is human"),
        )
        for title, fields, message in cases:
            with self.subTest(title):
                task_id = self.add(title, **fields)
                with self.assertRaisesRegex(ChittyError, message):
                    ticket_action(Repo.open(self.root), Repo.open(self.root).resolve(task_id))
                path = self.root / "chitty/tasks" / f"{task_id}--{title.lower().replace(' ', '-')}"
                path = path.with_suffix(".md")
                path.unlink()
        human_ticket = self.add("Human ticket", context="human")
        with self.assertRaisesRegex(ChittyError, "human ticket"):
            ticket_action(Repo.open(self.root), Repo.open(self.root).resolve(human_ticket))
        dependency = self.add("Unfinished", status="blocked")
        waiting = self.add("Waiting", depends_on=[dependency])
        with self.assertRaisesRegex(ChittyError, "unfinished dependencies"):
            ticket_action(Repo.open(self.root), Repo.open(self.root).resolve(waiting))
        repo = Repo.open(self.root)
        archived = self.add("Archived")
        repo.archive(repo.resolve(archived))
        with self.assertRaisesRegex(ChittyError, "archived"):
            ticket_action(repo, repo.resolve(archived))
        with self.assertRaisesRegex(ChittyError, "unknown ticket"):
            ticket_action(repo, repo.resolve("99"))

    def test_run_help_describes_explicit_ticket(self):
        result = self.run_cli("run", "--help")
        self.assertIn("--ticket ID", result.stdout)
        self.assertIn("or the one named by --ticket", result.stdout)

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
        # An idle queue is not an error, so it gets no `Error:` prefix.
        result = self.run_cli("next", exit_code=3)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "no next ticket\n")
        result = self.run_cli("next", "--json", exit_code=3)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "no next ticket\n")
        with self.assertRaisesRegex(ToolError, "no next ticket"):
            asyncio.run(server.call_tool("next", {}))

    def test_next_mode_selects_only_its_own_tickets(self):
        self.add("Todo")
        review = self.add("Review", status="review")
        doing = self.add("Doing", status="doing")
        self.assertEqual(self.run_cli("next").stdout, f"review {review}\n")
        self.assertEqual(self.run_cli("next", "--mode", "review").stdout, f"review {review}\n")
        self.assertEqual(self.run_cli("next", "--mode", "work").stdout, f"work {doing}\n")
        self.assertEqual(self.json("next", "--mode", "work"), {"mode": "work", "id": doing})
        self.assertIn("'work'", self.run_cli("next", "--mode", "other", exit_code=2).stderr)

        # A bad reference on a ticket in the other mode does not stop this mode.
        path = next((self.root / "chitty/tasks").glob(f"{review}--*.md"))
        path.write_text(
            path.read_text().replace(
                "status: review\n", "status: review\ndepends_on:\n  - TASK-99\n"
            )
        )
        self.assertEqual(self.run_cli("next").stdout, f"review {review}\n")
        self.assertEqual(self.run_cli("next", "--mode", "work").stdout, f"work {doing}\n")
        path.unlink()

        result = self.run_cli("next", "--mode", "review", exit_code=3)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "no next ticket for --mode review\n")

    def test_next_repeated_modes_include_both_modes(self):
        todo = self.add("Todo")
        review = self.add("Review", status="review")
        self.assertEqual(
            self.run_cli("next", "--mode", "review", "--mode", "work").stdout,
            f"review {review}\n",
        )
        self.assertEqual(self.run_cli("next", "--mode", "work").stdout, f"work {todo}\n")
        for path in (self.root / "chitty/tasks").glob("*.md"):
            path.unlink()
        result = self.run_cli("next", "--mode", "review", "--mode", "work", exit_code=3)
        self.assertEqual(result.stderr, "no next ticket for --mode review or work\n")

    def test_owner_filter_reserves_work_and_review(self):
        unowned = self.add("Unowned")
        opus_todo = self.add("Opus todo", owner="opus")
        opus_review = self.add("Opus review", status="review", owner="opus")
        self.assertEqual(self.run_cli("next").stdout, f"work {unowned}\n")
        self.assertEqual(self.run_cli("next", "--mode", "work").stdout, f"work {unowned}\n")
        self.assertEqual(self.run_cli("next", "--owner", "opus").stdout, f"review {opus_review}\n")
        self.assertEqual(
            self.run_cli("next", "--owner", "opus", "--mode", "work").stdout,
            f"work {opus_todo}\n",
        )
        result = asyncio.run(server.call_tool("next", {"owner": "opus"}))
        assert isinstance(result, CallToolResult)
        self.assertEqual(
            result.structured_content.get("result", result.structured_content),
            {
                "mode": "review",
                "id": opus_review,
            },
        )

    def test_run_owner_refusals_happen_before_preflight(self):
        for args, message in (
            (("--owner", "human"), "human or empty"),
            (("--owner", ""), "human or empty"),
            (("--ticket", "1", "--owner", "opus"), "--ticket"),
        ):
            with self.subTest(args=args):
                result = self.run_cli("run", *args, exit_code=1)
                self.assertIn(message, result.stderr)

    def test_run_explicit_ticket_accepts_agent_owner_but_not_human(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace(
                'agent_command = "pi --chitty-{mode} {id}"',
                'agent_command = "fake {mode} {id}"',
            )
            .replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        opus = self.add("Opus work", owner="opus")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")

        fake = self.root / "bin" / "fake"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import subprocess, sys\n"
            "from pathlib import Path\n"
            "path = next(Path('chitty/tasks').glob(sys.argv[2] + '--*.md'))\n"
            "path.write_text(path.read_text().replace('status: doing', 'status: blocked'))\n"
            "subprocess.run(['git', 'add', str(path)], check=True)\n"
            "subprocess.run(['git', 'commit', '--quiet', '-m', 'agent'], check=True)\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        old_path = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake.parent}:{old_path}"
        try:
            result = self.run_cli("run", "--ticket", opus)
        finally:
            os.environ["PATH"] = old_path
        self.assertEqual(result.stdout, f"{opus}: doing → blocked\n")

        human = self.add("Human work", owner="human")
        result = self.run_cli("run", "--ticket", human, exit_code=1)
        self.assertIn("owner is human", result.stderr)

    def test_run_mode_selects_only_its_own_tickets_and_is_not_forwarded(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace(
                'agent_command = "pi --chitty-{mode} {id}"', 'agent_command = "fake {mode} {id}"'
            )
            .replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        todo = self.add("Todo")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        fake = self.root / "bin" / "fake"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import subprocess, sys\n"
            "from pathlib import Path\n"
            "Path('invocation').write_text(' '.join(sys.argv[1:]))\n"
            "path = next(Path('chitty/tasks').glob(sys.argv[2] + '--*.md'))\n"
            "text = path.read_text()\n"
            "for status in ('doing', 'review'):\n"
            "    text = text.replace(f'status: {status}\\n', 'status: blocked\\n')\n"
            "path.write_text(text)\n"
            "subprocess.run(['git', 'commit', '--quiet', '-am', 'agent'], check=True)\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        old_path = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake.parent}:{old_path}"
        try:
            idle = self.run_cli("run", "--mode", "review", exit_code=3)
            self.assertEqual(idle.stdout, "")
            self.assertEqual(idle.stderr.splitlines()[-1], "no next ticket for --mode review")

            review = self.add("Review", status="review")
            self.git("add", "--all")
            self.git("commit", "--quiet", "-m", "review")
            self.git("branch", review.lower())
            worked = self.run_cli("run", "--mode", "work", "--", "--forwarded")
            self.assertEqual(worked.stdout, f"{todo}: doing → blocked\n")
            invocation = (self.root / f".worktrees/{todo.lower()}/invocation").read_text()
            self.assertEqual(invocation, f"work {todo} --forwarded")

            self.add("Another todo")  # `autocommit` commits it on `main`.
            reviewed = self.run_cli("run", "--mode", "review", "--", "--forwarded")
            self.assertEqual(reviewed.stdout, f"{review}: review → blocked\n")
            invocation = (self.root / f".worktrees/{review.lower()}/invocation").read_text()
            self.assertEqual(invocation, f"review {review} --forwarded")

            idle = self.run_cli("run", "--mode", "review", exit_code=3)
            self.assertEqual(idle.stdout, "")
            self.assertEqual(idle.stderr.splitlines()[-1], "no next ticket for --mode review")
        finally:
            os.environ["PATH"] = old_path

    def test_run_repeated_modes_selects_available_work(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace(
                'agent_command = "pi --chitty-{mode} {id}"', 'agent_command = "fake {mode} {id}"'
            )
            .replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        todo = self.add("Todo")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        fake = self.root / "bin" / "fake"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import subprocess, sys\n"
            "from pathlib import Path\n"
            "path = next(Path('chitty/tasks').glob(sys.argv[2] + '--*.md'))\n"
            "path.write_text(path.read_text().replace('status: doing\\n', 'status: blocked\\n'))\n"
            "subprocess.run(['git', 'commit', '--quiet', '-am', 'agent'], check=True)\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        previous = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake.parent}:{previous}"
        try:
            result = self.run_cli("run", "--mode", "review", "--mode", "work")
        finally:
            os.environ["PATH"] = previous
        self.assertEqual(result.stdout, f"{todo}: doing → blocked\n")

    def test_run_loop_forwards_every_mode(self):
        with (
            patch("chitty.run.Path.is_file", return_value=True),
            patch(
                "chitty.run.subprocess.run", return_value=subprocess.CompletedProcess([], 1)
            ) as run,
        ):
            self.assertEqual(run_loop(("--mode", "review", "--mode", "work")), 1)
        self.assertEqual(run.call_args.args[0][-4:], ["--mode", "review", "--mode", "work"])

    def test_run_overlaps_one_worker_and_one_reviewer(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace(
                'agent_command = "pi --chitty-{mode} {id}"',
                'agent_command = "fake-agent {mode} {id}"',
            )
            .replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        exclude = self.root / ".git" / "info" / "exclude"
        exclude.write_text(exclude.read_text() + "\n/bin/\n")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        worker_id = self.add("Work")
        reviewer_id = self.add("Review", status="review")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        self.git("branch", reviewer_id.lower())

        fake = self.root / "bin" / "fake-agent"
        fake.parent.mkdir()
        chitty = str(Path(sys.executable).parent / "chitty")
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import os, pathlib, subprocess, sys\n"
            "root = pathlib.Path.cwd()\n"
            "mode, ticket = sys.argv[1:3]\n"
            f"chitty = {chitty!r}\n"
            "if mode == 'work':\n"
            "    subprocess.run([chitty, 'run', '--mode', 'review'], check=True,\n"
            "                    stdout=subprocess.DEVNULL)\n"
            "    command = [chitty, 'edit', ticket, '--status', 'blocked',\n"
            "               '--note', 'worker finished']\n"
            "else:\n"
            "    command = [chitty, 'edit', ticket, '--status', 'done',\n"
            "               '--note', 'Reviewed: overlap test']\n"
            "subprocess.run(command, check=True, stdout=subprocess.DEVNULL)\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        self.addCleanup(
            self.git,
            "worktree",
            "remove",
            "--force",
            str(self.root / ".worktrees" / worker_id.lower()),
        )
        reviewer_worktree = self.root / ".worktrees" / reviewer_id.lower()
        self.addCleanup(
            lambda: (
                self.git("worktree", "remove", "--force", str(reviewer_worktree))
                if reviewer_worktree.exists()
                else None
            )
        )
        previous_path = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake.parent}:{previous_path}"
        try:
            result = self.run_cli("run", "--mode", "work")
        finally:
            os.environ["PATH"] = previous_path

        self.assertEqual(result.stdout, f"{worker_id}: doing → blocked\n")
        worker = self.root / ".worktrees" / worker_id.lower()
        self.assertTrue(worker.exists())
        worker_task = Repo.open(worker).find(Repo.open(worker).resolve(worker_id)).task
        review_task = Repo.open(self.root).find(Repo.open(self.root).resolve(reviewer_id)).task
        self.assertEqual(worker_task.frontmatter.status, "blocked")
        self.assertEqual(review_task.frontmatter.status, "done")
        worker_history = worker_task.section("History") or ""
        review_history = review_task.section("History") or ""
        worker_actors = {
            line.split()[2]
            for line in worker_history.splitlines()
            if "todo → doing" in line or "doing → blocked" in line
        }
        review_actors = {
            line.split()[2] for line in review_history.splitlines() if "review → done" in line
        }
        self.assertEqual(len(worker_actors), 1)
        self.assertEqual(len(review_actors), 1)
        self.assertNotEqual(worker_actors, review_actors)

    def test_run_refuses_mode_with_ticket_before_anything_else(self):
        # Outside Git, so any later step would fail with a different error.
        self.add("Todo")
        result = self.run_cli("run", "--mode", "work", "--ticket", "1", exit_code=1)
        self.assertIn("--mode cannot be used with --ticket", result.stderr)
        self.assertEqual(list(self.root.glob(".worktrees")), [])

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
        exclude = self.root / ".git" / "info" / "exclude"
        exclude.write_text(exclude.read_text() + "\n/bin/\n")
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
            "(main / 'main-change.txt').write_text('new main commit\\n')\n"
            "subprocess.run(['git', '-C', str(main), 'add', 'main-change.txt'], check=True)\n"
            "subprocess.run(['git', '-C', str(main), 'commit', '--quiet', "
            "'-m', 'move main'], check=True)\n"
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
        self.assertEqual((self.root / "main-change.txt").read_text(), "new main commit\n")

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
            "import os, pathlib, subprocess, sys\n"
            "worker = pathlib.Path.cwd()\n"
            "path = next((worker / 'chitty/tasks').glob(sys.argv[2] + '--*.md'))\n"
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

    def test_run_uses_runner_chitty_and_strips_worktree_environment(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace(
                'agent_command = "pi --chitty-{mode} {id}"',
                'agent_command = "fake-agent {mode} {id}"',
            )
            .replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        exclude = self.root / ".git" / "info" / "exclude"
        exclude.write_text(exclude.read_text() + "\n/bin/\n")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Todo")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")

        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        report = self.tmp / "agent-environment.json"
        fake_chitty = bin_dir / "chitty"
        fake_chitty.write_text(
            "#!" + sys.executable + "\n"
            "import pathlib, sys\n"
            f"pathlib.Path({str(report)!r}).write_text('fake chitty')\n"
            "sys.exit(99)\n"
        )
        fake_chitty.chmod(fake_chitty.stat().st_mode | stat.S_IXUSR)
        agent = bin_dir / "fake-agent"
        runner_chitty = Path(sys.executable).parent / "chitty"
        agent.write_text(
            "#!" + sys.executable + "\n"
            "import json, os, pathlib, shutil, subprocess, sys\n"
            f"report = pathlib.Path({str(report)!r})\n"
            "report.write_text(json.dumps({\n"
            "    'chitty': shutil.which('chitty'),\n"
            "    'virtual_env': os.environ.get('VIRTUAL_ENV'),\n"
            "    'uv_project_environment': os.environ.get('UV_PROJECT_ENVIRONMENT'),\n"
            "    'usage_file': os.environ.get('CHITTY_USAGE_FILE'),\n"
            "}))\n"
            "task = next(pathlib.Path('chitty/tasks').glob('TASK-1--*.md'))\n"
            "task.write_text(task.read_text().replace('status: doing', 'status: done'))\n"
            "subprocess.run(['git', 'add', str(task)], check=True)\n"
            "subprocess.run(['git', 'commit', '--quiet', '-m', 'agent'], check=True)\n"
        )
        agent.chmod(agent.stat().st_mode | stat.S_IXUSR)
        previous = {
            key: os.environ.get(key) for key in ("PATH", "VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT")
        }
        os.environ["PATH"] = f"{bin_dir}:{os.environ.get('PATH', '')}"
        os.environ["VIRTUAL_ENV"] = "/branch/.venv"
        os.environ["UV_PROJECT_ENVIRONMENT"] = "/branch/.venv"
        try:
            result = self.run_cli("run")
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
        self.assertEqual(result.stdout, "TASK-1: doing → done\n")
        environment = json.loads(report.read_text())
        self.assertEqual(environment["chitty"], str(runner_chitty))
        self.assertIsNone(environment["virtual_env"])
        self.assertIsNone(environment["uv_project_environment"])
        self.assertIsNone(environment["usage_file"])

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
        self.assertEqual(result.returncode, 0)
        self.assertIn("TASK-1: todo → error", result.stdout)

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
            result = self.run_cli("run")
        finally:
            os.environ["PATH"] = old_path
            os.environ.pop("PI_CODING_AGENT_DIR", None)
            os.environ.pop("SEEN", None)

        self.assertEqual(seen.read_text(), CHITTY_VERSION)
        self.assertNotEqual(extension.read_text(), "old extension")
        self.assertIn(str(config), result.stderr)
        self.assertNotIn("re-run `chitty init`", result.stderr)
        self.assertIn(
            "chitty: upgrade repository setup",
            self.git("log", "-3", "--format=%s"),
        )
        changed = self.git("show", "--format=", "--name-only", "HEAD").splitlines()
        self.assertTrue(
            set(changed)
            <= {
                "chitty.toml",
                "AGENTS.md",
                ".gitignore",
                "CLAUDE.md",
                "chitty/tasks/TASK-1--todo.md",
            }
        )

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
            self.run_cli("run")
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
            current = self.run_cli("run")
            self.assertNotEqual(self.git("rev-parse", "HEAD"), before)
            self.assertNotIn("setup", current.stderr)
            worktree = self.tmp / "worktree"
            self.git("worktree", "add", "--quiet", "-b", "worker", str(worktree))
            self.addCleanup(self.git, "worktree", "remove", "--force", str(worktree))
            previous = Path.cwd()
            os.chdir(worktree)
            try:
                linked = self.run_cli("run", exit_code=3)
            finally:
                os.chdir(previous)
            self.assertNotEqual(self.git("rev-parse", "HEAD"), before)
            self.assertNotIn("setup", linked.stderr)
        finally:
            os.environ["PATH"] = old_path

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=self.root, capture_output=True, text=True, check=True
        ).stdout

    def test_run_reports_all_missing_preflight_settings_together(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace("autocommit = false", "autocommit = true")
            .replace('check = "true"\n', "")
            .replace('agent_command = "pi --chitty-{mode} {id}"\n', "")
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Todo")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")

        result = self.run_cli("run", exit_code=1)

        self.assertIn("`chitty run` configuration is incomplete in chitty.toml", result.stderr)
        self.assertIn('setup = "make install"', result.stderr)
        self.assertIn('check = "make check"', result.stderr)
        self.assertIn("agent_command = ", result.stderr)
        self.assertIn("requires `setup`", result.stderr)
        self.assertIn("requires `check`", result.stderr)
        self.assertFalse((self.root / ".worktrees").exists())

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
            ("check", lambda text: text.replace('check = "true"\n', ""), None),
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
                    "autocommit": (
                        "`chitty run` requires `autocommit = true` in chitty.toml, "
                        "so ticket changes reach every branch; `chitty init --autocommit` sets it"
                    ),
                    "setup": (
                        "`chitty run` requires `setup` in chitty.toml: the command that installs "
                        "a new ticket worktree's environment before the agent starts, for example "
                        'setup = "make install"'
                    ),
                    "check": "requires `check` in chitty.toml",
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

    def test_run_preflight_message_names_pyproject_config(self):
        config = self.root / "chitty.toml"
        pyproject = self.root / "pyproject.toml"
        config_text = config.read_text().replace(
            "autocommit = false", 'autocommit = true\nsetup = "true"'
        )
        config.unlink()
        pyproject.write_text(
            "[tool.chitty]\n" + config_text.replace("[contexts.", "[tool.chitty.contexts.")
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Todo")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        pyproject.write_text(pyproject.read_text().replace('setup = "true"\n', ""))
        self.git("add", "pyproject.toml")
        self.git("commit", "--quiet", "-m", "remove setup")

        result = self.run_cli("run", exit_code=1)

        self.assertIn(
            "`chitty run` requires `setup` in pyproject.toml: the command that installs "
            "a new ticket worktree's environment before the agent starts, for example "
            'setup = "make install"',
            result.stderr,
        )

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
            result = self.run_cli("run")
        finally:
            os.environ["PATH"] = previous
        self.assertIn("todo → error", result.stdout)
        self.assertFalse(marker.exists())
        worktree = self.root / ".worktrees" / "task-1"
        self.assertTrue(worktree.is_dir())
        self.assertEqual(
            Repo.open(worktree).find(Repo.open(worktree).resolve("TASK-1")).task.frontmatter.status,
            "error",
        )

    def test_run_check_failure_records_output_and_does_not_claim_or_start_agent(self):
        config = self.root / "chitty.toml"
        checker = self.root / "check.py"
        checker.write_text(
            "from pathlib import Path\n"
            "import sys\n"
            "ticket = next(Path('chitty/tasks').glob('*.md'))\n"
            "Path('check-args').write_text(repr(sys.argv[1:]) + '\\n' + ticket.read_text())\n"
            "for number in range(1, 26): print(f'check line {number}')\n"
            "raise SystemExit(1)\n"
        )
        config.write_text(
            config.read_text()
            .replace('check = "true"', f"check = \"{sys.executable} {checker} 'quoted argument'\"")
            .replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Todo")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")

        self.install_fake_pi("from pathlib import Path\nPath('started').write_text('yes')\n")
        result = self.run_cli("run")

        self.assertIn("todo → error", result.stdout)
        self.assertEqual(result.stdout.count("TASK-1"), 1)
        checked = (self.root / ".worktrees/task-1/check-args").read_text()
        self.assertIn("['quoted argument']", checked)
        self.assertIn("status: todo", checked)
        self.assertIn("Running check", result.stderr)
        self.assertFalse((self.root / ".worktrees/task-1/started").exists())
        repo = Repo.open(self.root)
        task = repo.find(repo.resolve("TASK-1")).task
        self.assertEqual(task.frontmatter.status, "error")
        self.assertIn("check line 6", task.section("Notes") or "")

    def test_run_check_failure_records_markdown_like_output(self):
        config = self.root / "chitty.toml"
        checker = self.root / "check.py"
        checker.write_text(
            "print('FAIL: test_something')\n"
            "print('-' * 70)\n"
            "print('```')\n"
            "print('# not a heading')\n"
            "raise SystemExit(1)\n"
        )
        config.write_text(
            config.read_text()
            .replace('check = "true"', f'check = "{sys.executable} {checker}"')
            .replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Todo")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")

        self.install_fake_pi("from pathlib import Path\nPath('started').write_text('yes')\n")
        result = self.run_cli("run")

        self.assertIn("todo → error", result.stdout)
        repo = Repo.open(self.root)
        task = repo.find(repo.resolve("TASK-1")).task
        self.assertEqual(task.frontmatter.status, "error")
        notes = task.section("Notes") or ""
        self.assertIn("FAIL: test_something", notes)
        self.assertIn("# not a heading", notes)

    def test_run_check_failure_on_doing_ticket_starts_agent(self):
        config = self.root / "chitty.toml"
        checker = self.root / "check.py"
        checker.write_text(
            "for number in range(1, 4): print(f'check line {number}')\nraise SystemExit(1)\n"
        )
        config.write_text(
            config.read_text()
            .replace('check = "true"', f'check = "{sys.executable} {checker}"')
            .replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Todo")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        self.run_cli("edit", "TASK-1", "--status", "doing")
        self.git("branch", "task-1")
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
            result = self.run_cli("run")
        finally:
            os.environ["PATH"] = previous

        self.assertIn("doing → error", result.stdout)
        self.assertFalse((self.root / ".worktrees/task-1/started").exists())
        repo = Repo.open(self.root)
        task = repo.find(repo.resolve("TASK-1")).task
        self.assertEqual(task.frontmatter.status, "error")
        notes = task.section("Notes") or ""
        self.assertIn("check line 1", notes)
        self.assertIn("check line 1", notes)
        self.assertIn("```text", notes)

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
            unchanged = self.run_cli("run")
        finally:
            os.environ["PATH"] = previous
            if previous_root is None:
                os.environ.pop("EXPECTED_ROOT", None)
            else:
                os.environ["EXPECTED_ROOT"] = previous_root
        self.assertIn("todo → error", unchanged.stdout)
        worktree = self.root / ".worktrees" / "task-1"
        self.assertEqual(
            self.git("-C", str(worktree), "branch", "--show-current").strip(), "task-1"
        )
        self.assertEqual(
            Repo.open(worktree).find(Repo.open(worktree).resolve("TASK-1")).task.frontmatter.status,
            "error",
        )

        self.git("worktree", "remove", "--force", str(worktree))
        self.git("branch", "-D", "task-1")
        self.git("add", "bin/pi")
        self.git("commit", "--quiet", "-m", "install test agent")
        self.run_cli("edit", "TASK-1", "--status", "review")
        os.environ["PATH"] = f"{fake.parent}:{previous}"
        try:
            result = self.run_cli("run")
        finally:
            os.environ["PATH"] = previous
        self.assertEqual(result.stdout, "TASK-1: review → blocked\n")
        ticket = Repo.open(self.root).find(Repo.open(self.root).resolve("TASK-1")).task
        self.assertIn("TASK-1", ticket.section("Notes") or "")
        self.assertIn("task-1", ticket.section("Notes") or "")
        self.assertFalse(worktree.exists())

    def test_run_reviews_branch_with_changed_config(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.run_cli("init")
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
        branch_config.write_text(branch_config.read_text() + "\n# branch change\n")
        self.git("-C", str(branch_worktree), "add", "chitty.toml")
        self.git("-C", str(branch_worktree), "commit", "--quiet", "-m", "change config")
        self.git("worktree", "remove", "--force", str(branch_worktree))
        marker = self.root / "started"
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\nfrom pathlib import Path\nPath('started').touch()\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        previous = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake.parent}:{previous}"
        try:
            result = self.run_cli("run", "--mode", "review")
        finally:
            os.environ["PATH"] = previous

        self.assertEqual(
            result.stdout,
            "TASK-1: review → doing\n",
        )
        task = Repo.open(self.root).find(Repo.open(self.root).resolve("TASK-1")).task
        self.assertEqual(
            task.section("Notes"),
            "Review failed (work): the branch changes `chitty.toml`; "
            "only `chitty init` on the main checkout may change it.",
        )
        self.assertFalse(marker.exists())

    def test_run_reviews_branch_with_deleted_config(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.run_cli("init")
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
        (branch_worktree / "chitty.toml").unlink()
        self.git("-C", str(branch_worktree), "add", "--all")
        self.git("-C", str(branch_worktree), "commit", "--quiet", "-m", "delete config")
        self.git("worktree", "remove", "--force", str(branch_worktree))
        marker = self.root / "started"
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\nfrom pathlib import Path\nPath('started').touch()\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        previous = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake.parent}:{previous}"
        try:
            result = self.run_cli("run", "--mode", "review")
        finally:
            os.environ["PATH"] = previous

        self.assertEqual(result.stdout, "TASK-1: review → doing\n")
        task = Repo.open(self.root).find(Repo.open(self.root).resolve("TASK-1")).task
        self.assertEqual(
            task.section("Notes"),
            "Review failed (work): the branch changes `chitty.toml`; "
            "only `chitty init` on the main checkout may change it.",
        )
        self.assertFalse(marker.exists())

    def test_run_review_compares_only_tool_chitty_in_pyproject(self):
        config = self.root / "chitty.toml"
        pyproject = self.root / "pyproject.toml"
        pyproject.write_text(
            "[tool.chitty]\n"
            + config.read_text().replace("[contexts.", "[tool.chitty.contexts.")
            + "\n[tool.other]\nvalue = 1\n"
        )
        config.unlink()
        self.run_cli("init")
        pyproject.write_text(
            pyproject.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        exclude = self.root / ".git" / "info" / "exclude"
        exclude.write_text(exclude.read_text() + "\n/bin/\n")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Unrelated change")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        self.run_cli("edit", "TASK-1", "--status", "review")
        self.git("branch", "task-1")
        branch_worktree = self.root / ".worktrees" / "prepare-task-1"
        self.git("worktree", "add", "--quiet", str(branch_worktree), "task-1")
        branch_pyproject = branch_worktree / "pyproject.toml"
        branch_pyproject.write_text(branch_pyproject.read_text().replace("value = 1", "value = 2"))
        self.git("-C", str(branch_worktree), "add", "pyproject.toml")
        self.git("-C", str(branch_worktree), "commit", "--quiet", "-m", "change other tool")
        self.git("worktree", "remove", "--force", str(branch_worktree))
        self.install_fake_pi(
            "import subprocess, sys\n"
            "path = next(\n"
            "    __import__('pathlib').Path('chitty/tasks').glob(sys.argv[-1] + '--*.md')\n"
            ")\n"
            "path.write_text(path.read_text().replace('status: review', 'status: done'))\n"
            "subprocess.run(['git', 'add', str(path)], check=True)\n"
            "subprocess.run(['git', 'commit', '--quiet', '-m', 'finish'], check=True)\n"
        )
        passed = self.run_cli("run", "--ticket", "TASK-1")
        self.assertEqual(passed.stdout, "TASK-1: review → done\n")

        self.add("Config change")
        self.run_cli("edit", "TASK-2", "--status", "review")
        self.git("branch", "task-2")
        branch_worktree = self.root / ".worktrees" / "prepare-task-2"
        self.git("worktree", "add", "--quiet", str(branch_worktree), "task-2")
        branch_pyproject = branch_worktree / "pyproject.toml"
        branch_pyproject.write_text(
            branch_pyproject.read_text().replace("review = true", "review = false")
        )
        self.git("-C", str(branch_worktree), "add", "pyproject.toml")
        self.git("-C", str(branch_worktree), "commit", "--quiet", "-m", "change chitty config")
        self.git("worktree", "remove", "--force", str(branch_worktree))
        result = self.run_cli("run", "--ticket", "TASK-2")
        self.assertEqual(result.stdout, "TASK-2: review → doing\n")
        task = Repo.open(self.root).find(Repo.open(self.root).resolve("TASK-2")).task
        self.assertEqual(
            task.section("Notes"),
            "Review failed (work): the branch changes `pyproject.toml`; "
            "only `chitty init` on the main checkout may change it.",
        )

    def test_run_agent_rejects_unknown_and_invalid_without_claiming(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace(
                'agent_command = "pi --chitty-{mode} {id}"',
                'agent_command = "pi --chitty-{mode} {id}"\n\n[agent_commands]\nclaude = "pi"',
            )
            .replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Todo")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")

        unknown = self.run_cli("run", "--agent", "missing", exit_code=1)
        self.assertIn("available names: claude", unknown.stderr)
        self.assertFalse((self.root / ".worktrees").exists())
        self.assertEqual(
            Repo.open(self.root)
            .find(Repo.open(self.root).resolve("TASK-1"))
            .task.frontmatter.status,
            "todo",
        )

        invalid = self.run_cli("run", "--agent", "claude", exit_code=1)
        self.assertIn("agent_commands.claude", invalid.stderr)
        self.assertFalse((self.root / ".worktrees").exists())
        self.assertEqual(
            Repo.open(self.root)
            .find(Repo.open(self.root).resolve("TASK-1"))
            .task.frontmatter.status,
            "todo",
        )

    def test_run_agent_selects_command_and_forwards_arguments(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace(
                'agent_command = "pi --chitty-{mode} {id}"',
                'agent_command = "fake-agent default {mode} {id}"\n\n'
                '[agent_commands]\nchosen = "fake-agent chosen {mode} {id}"',
            )
            .replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("First")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        fake = self.root / "bin" / "fake-agent"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import subprocess, sys\n"
            "from pathlib import Path\n"
            "Path('invocation').write_text(' '.join(sys.argv[1:]))\n"
            "path = next(Path('chitty/tasks').glob('*.md'))\n"
            "path.write_text(path.read_text().replace('status: doing', 'status: blocked'))\n"
            "subprocess.run(['git', 'add', str(path)], check=True)\n"
            "subprocess.run(['git', 'commit', '--quiet', '-m', 'agent'], check=True)\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        old_path = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake.parent}:{old_path}"
        try:
            self.run_cli("run", "--agent", "chosen", "--", "--forwarded", "value")
        finally:
            os.environ["PATH"] = old_path
        invocation = (self.root / ".worktrees/task-1/invocation").read_text()
        self.assertIn("chosen work TASK-1 --forwarded value", invocation)
        self.assertNotIn("--agent", invocation)

        self.add("Second")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "second")
        os.environ["PATH"] = f"{fake.parent}:{old_path}"
        try:
            self.run_cli("run")
        finally:
            os.environ["PATH"] = old_path
        default_invocation = (self.root / ".worktrees/task-2/invocation").read_text()
        self.assertIn("default work TASK-2", default_invocation)

    def test_run_cases(self):
        # The fake agent reads descriptor 0; keep this test independent of the
        # caller's potentially open stdin while restoring it after the test.
        saved_stdin = os.dup(0)
        devnull = os.open(os.devnull, os.O_RDONLY)
        os.dup2(devnull, 0)
        self.addCleanup(os.close, saved_stdin)
        self.addCleanup(os.dup2, saved_stdin, 0)
        self.addCleanup(os.close, devnull)

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
            "import os, signal, subprocess, sys\n"
            "assert os.getcwd() == os.environ['EXPECTED_ROOT']\n"
            "assert sys.stdin.read() == ''\n"
            "if os.environ.get('CHANGE'):\n"
            "    path = os.environ['TASK_PATH']\n"
            "    text = open(path).read()\n"
            "    text = text.replace('status: doing', 'status: blocked')\n"
            "    text = text.replace('status: error', 'status: blocked')\n"
            "    open(path, 'w').write(text)\n"
            "    subprocess.run(['git', 'add', path], check=True)\n"
            "    subprocess.run(['git', 'commit', '--quiet', '-m', 'worker change'], check=True)\n"
            "if os.environ.get('PI_SIGNAL'):\n"
            "    signal.signal(signal.SIGINT, signal.SIG_DFL)\n"
            "    os.kill(os.getpid(), signal.SIGINT)\n"
            "sys.exit(int(os.environ.get('PI_EXIT', '0')))\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        old_path = os.environ.get("PATH", "")
        main_status = self.git("status", "--porcelain")
        os.environ["PATH"] = f"{fake.parent}:{old_path}"
        os.environ["EXPECTED_ROOT"] = str(self.root / ".worktrees" / "task-1")
        try:
            unchanged = self.run_cli("run")
            self.assertEqual(unchanged.stdout, "TASK-1: todo → error\n")
            worktree = self.root / ".worktrees" / "task-1"
            self.assertEqual(
                self.git("-C", str(worktree), "branch", "--show-current").strip(), "task-1"
            )
            self.assertEqual(
                Repo.open(worktree)
                .find(Repo.open(worktree).resolve("TASK-1"))
                .task.frontmatter.status,
                "error",
            )
            self.assertNotEqual(self.git("rev-parse", "main").strip(), main_head)
            self.assertEqual(self.git("status", "--porcelain"), main_status)
            self.assertEqual(self.git("rev-list", "--count", "main..task-1").strip(), "1")
            invalid = self.run_cli("run", "--errors", exit_code=1)
            self.assertIn("repair agent left TASK-1 in invalid status error", invalid.stderr)
            os.environ["PI_EXIT"] = "3"
            failed = self.run_cli("run", "--errors")
            self.assertEqual(failed.stdout, "TASK-1: error → error\n")
            os.environ["PI_EXIT"] = "7"
            failed = self.run_cli("run", "--errors")
            self.assertEqual(failed.stdout, "TASK-1: error → error\n")
            self.assertNotIn("cannot read usage file", failed.stderr)
            self.assertEqual(self.git("rev-list", "--count", "main..task-1").strip(), "1")
            os.environ.pop("PI_EXIT")
            os.environ["PI_SIGNAL"] = "1"
            interrupted = self.run_cli("run", "--errors", exit_code=130)
            self.assertIn("interrupted during agent", interrupted.stderr)
            os.environ.pop("PI_SIGNAL")
            os.environ["CHANGE"] = "1"
            os.environ["TASK_PATH"] = str(
                self.root / ".worktrees" / "task-1" / "chitty/tasks/TASK-1--todo.md"
            )
            changed = self.run_cli("run", "--errors")
            self.assertEqual(changed.stdout, "TASK-1: error → blocked\n")
            log = self.tmp / "data" / "chitty" / "usage" / "repo.jsonl"
            records = [json.loads(line) for line in log.read_text().splitlines()]
            self.assertEqual(records[-1]["status_after"], "blocked")
            self.assertTrue(all("models" not in record for record in records))
            no_next = self.run_cli("run", exit_code=3)
            self.assertEqual(no_next.stdout, "")
            self.assertEqual(no_next.stderr, "no next ticket\n")
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
            "import pathlib, subprocess\n"
            "root = pathlib.Path.cwd()\n"
            "ticket = next((root / 'chitty/tasks').glob('*.md'))\n"
            "ticket.write_text(ticket.read_text().replace('status: doing', 'status: blocked'))\n"
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
            },
        )
        self.assertEqual(records[0]["status_before"], "doing")
        self.assertEqual(records[0]["status_after"], "blocked")
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_run_without_usage_file_is_silent_and_logs_no_models(self):
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
            "import os, pathlib, subprocess\n"
            "report = pathlib.Path(os.environ['REPORT'])\n"
            "report.write_text(str('CHITTY_USAGE_FILE' in os.environ))\n"
            "root = pathlib.Path.cwd()\n"
            "ticket = next((root / 'chitty/tasks').glob('*.md'))\n"
            "ticket.write_text(ticket.read_text().replace('status: doing', 'status: blocked'))\n"
            "subprocess.run(['git', 'add', str(ticket)], check=True)\n"
            "subprocess.run(['git', 'commit', '--quiet', '-m', 'worker change'], check=True)\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        report = self.tmp / "report.txt"
        previous = {key: os.environ.get(key) for key in ("PATH", "REPORT")}
        os.environ["PATH"] = f"{fake.parent}:{previous['PATH'] or ''}"
        os.environ["REPORT"] = str(report)
        try:
            result = self.run_cli("run")
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

        self.assertEqual(result.stdout, "TASK-1: doing → blocked\n")
        self.assertNotIn("cannot read usage file", result.stderr)
        self.assertEqual(report.read_text(), "False")
        log = self.tmp / "data" / "chitty" / "usage" / "repo.jsonl"
        records = [json.loads(line) for line in log.read_text().splitlines()]
        self.assertEqual(len(records), 1)
        self.assertNotIn("models", records[0])

    def test_usage_log_write_failure_warns_without_raising(self):
        stderr = io.StringIO()
        with (
            patch("chitty.run._append_usage", side_effect=OSError("disk full")),
            redirect_stderr(stderr),
        ):
            _record_usage("repo", {})
        self.assertIn("warning: cannot write usage log: disk full", stderr.getvalue())

    def test_run_write_failure_warns_and_keeps_agent_exit_code(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Failure")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text("#!" + sys.executable + "\nimport sys\nsys.exit(7)\n")
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        previous = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake.parent}:{previous}"
        stderr = io.StringIO()
        try:
            with (
                patch("chitty.run._append_usage", side_effect=OSError("disk full")),
                redirect_stderr(stderr),
            ):
                result = self.run_cli("run")
        finally:
            os.environ["PATH"] = previous
        self.assertIn("todo → error", result.stdout)
        self.assertIn("warning: cannot write usage log: disk full", result.stderr)

    def test_run_logs_under_project_added_by_setup_refresh(self):
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
            "import pathlib, subprocess\n"
            "root = pathlib.Path.cwd()\n"
            "ticket = next((root / 'chitty/tasks').glob('*.md'))\n"
            "ticket.write_text(ticket.read_text().replace('status: doing', 'status: blocked'))\n"
            "subprocess.run(['git', 'add', str(ticket)], check=True)\n"
            "subprocess.run(['git', 'commit', '--quiet', '-m', 'worker change'], check=True)\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        previous = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake.parent}:{previous}"
        try:
            self.assertIsNone(Repo.open(self.root).config.project)
            self.assertEqual(self.run_cli("run").stdout, "TASK-1: doing → blocked\n")
        finally:
            os.environ["PATH"] = previous

        self.assertEqual(Repo.open(self.root).config.project, "repo")
        log = self.tmp / "data" / "chitty" / "usage" / "repo.jsonl"
        self.assertEqual(len(log.read_text().splitlines()), 1)

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
            "(root / 'run-actor').write_text(os.environ['CHITTY_ACTOR'])\n"
            "(root / 'pi-session-id').write_text(os.environ.get('CHITTY_PI_SESSION_ID', ''))\n"
            "os.environ['CLAUDE_CODE_SESSION_ID'] = 'agent-session'\n"
            "chitty = str(pathlib.Path(sys.executable).with_name('chitty'))\n"
            "subprocess.run([chitty, 'edit', sys.argv[2], '--status', 'blocked', "
            "'--note', 'fake agent write'], check=True, stdout=subprocess.DEVNULL)\n"
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
            with patch(
                "chitty.run.uuid4",
                side_effect=[
                    UUID("00000000-0000-0000-0000-000000000001"),
                    UUID("00000000-0000-0000-0000-000000000002"),
                ],
            ):
                self.assertEqual(
                    self.run_cli("run", "--", "--from-test").stdout,
                    "TASK-1: doing → blocked\n",
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
                first_actor = (worktree / "run-actor").read_text()
                self.assertEqual(first_actor, next(iter(actors)))
                self.assertEqual((worktree / "pi-session-id").read_text(), "")

                os.environ["CHITTY_ACTOR"] = "test-agent"
                self.add("Second")
                self.git("add", "--all")
                self.git("commit", "--quiet", "-m", "add second ticket")
                os.environ["CHITTY_ACTOR"] = "fixed-actor"
                os.environ["CLAUDE_CODE_SESSION_ID"] = "fixed-session"
                self.assertEqual(self.run_cli("run").stdout, "TASK-2: doing → blocked\n")
                second = self.root / ".worktrees" / "task-2"
                second_history = (
                    Repo.open(second)
                    .find(Repo.open(second).resolve("TASK-2"))
                    .task.section("History")
                )
                assert second_history is not None
                second_actor = second_history.splitlines()[-1].split()[2]
                second_run_actor = (second / "run-actor").read_text()
                self.assertEqual(second_actor, second_run_actor)
                self.assertNotEqual(first_actor, second_run_actor)
                self.assertNotIn("fixed-actor", {second_actor})
                self.assertEqual((second / "pi-session-id").read_text(), "")
        finally:
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

    def test_run_leaves_pending_inbox_suggestions_unpulled(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace('project = "chitty"\n', "")
            .replace("autocommit = false", 'autocommit = true\nproject = "demo"\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Todo")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        pending = suggest("demo", "Pending suggestion", None, True, self.root)
        fake = self.root / "bin" / "pi"
        fake.parent.mkdir()
        fake.write_text("#!" + sys.executable + "\n")
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        previous = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake.parent}:{previous}"
        try:
            self.run_cli("run")
        finally:
            os.environ["PATH"] = previous
        self.assertTrue(pending.exists())
        titles = [item.task.frontmatter.title for item in Repo.open(self.root).all_tasks()]
        self.assertEqual(titles, ["Todo"])

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
        (self.root / ".gitignore").write_text("setup-ran\npi-ran\nagent-arguments-*\ninterpreted\n")
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
            # A continued session appends `-c` after a continuation prompt.
            "if sys.argv[2:] == ['-c']:\n"
            "    assert sys.argv[1].startswith('Continue ')\n"
            "else:\n"
            "    assert sys.argv[2:] == []\n"
            "    assert '\\n' in sys.argv[1]\n"
            "    Path('agent-arguments-' + name).write_text(repr(sys.argv[1:]))\n"
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
            result = self.run_cli("run")
            repeated = self.run_cli("run", exit_code=3)
        finally:
            os.environ["PATH"] = previous
            if previous_root is None:
                os.environ.pop("EXPECTED_ROOT", None)
            else:
                os.environ["EXPECTED_ROOT"] = previous_root
        self.assertEqual(result.stdout, "TASK-1: todo → error\n")
        self.assertEqual(repeated.stderr, "no next ticket\n")
        self.assertTrue((worktree / "pi-ran").exists())
        self.assertEqual(
            (worktree / "agent-arguments-work").read_text(), repr([guide("work", "TASK-1")])
        )
        self.assertEqual((worktree / "setup-ran").read_text(), "1")
        self.assertFalse((worktree / "interpreted").exists())

        self.git("worktree", "remove", "--force", str(worktree))
        self.git("branch", "-D", "task-1")
        self.run_cli("edit", "TASK-1", "--status", "review")
        self.git("worktree", "add", "--quiet", "-b", "task-1", str(worktree))
        os.environ["PATH"] = f"{fake.parent}:{previous}"
        os.environ["EXPECTED_ROOT"] = str(worktree)
        try:
            review = self.run_cli("run")
        finally:
            os.environ["PATH"] = previous
            os.environ.pop("EXPECTED_ROOT", None)
        self.assertEqual(review.stdout, "TASK-1: review → error\n")
        review_prompt = (worktree / "agent-arguments-review").read_text()
        self.assertEqual(review_prompt, repr([guide("review", "TASK-1")]))
        self.assertIn('"', review_prompt)
        self.assertEqual(
            Repo.open(worktree).find(Repo.open(worktree).resolve("TASK-1")).task.frontmatter.status,
            "error",
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

    def test_error_tickets_need_explicit_repair_and_repair_updates_main_state(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.add("Broken", status="error")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        self.assertEqual(self.run_cli("next", exit_code=3).stderr, "no next ticket\n")
        self.run_cli("run", "--ticket", "TASK-1", exit_code=1)

        self.install_fake_pi(
            "from pathlib import Path\n"
            "import subprocess\n"
            "path = next(Path('chitty/tasks').glob('*.md'))\n"
            "path.write_text(path.read_text().replace('status: error', 'status: review'))\n"
            "subprocess.run(['git', 'add', str(path)], check=True)\n"
            "subprocess.run(['git', 'commit', '--quiet', '-m', 'repair'], check=True)\n"
        )
        result = self.run_cli("run", "--errors")
        self.assertEqual(result.stdout, "TASK-1: error → review\n", result.stderr)
        self.assertEqual(self.json("show", "TASK-1")["status"], "review")
