import asyncio
import os
import subprocess
from typing import Any

from mcp.server.mcpserver.exceptions import ToolError
from mcp_types import CallToolResult

from chitty.mcp import server
from chitty.store import guide
from tests.test_cli import CliTestCase


def call(name: str, **arguments: Any) -> Any:
    result = asyncio.run(server.call_tool(name, arguments))
    assert isinstance(result, CallToolResult)
    content = result.structured_content
    assert content is not None
    return content.get("result", content)


class TestMcp(CliTestCase):
    def test_tools_mirror_the_cli(self):
        tools = asyncio.run(server.list_tools())
        self.assertEqual(
            sorted(t.name for t in tools),
            sorted(
                [
                    "add",
                    "suggest",
                    "whoami",
                    "inbox",
                    "list",
                    "next",
                    "show",
                    "edit",
                    "note",
                    "fix",
                    "move",
                    "renumber",
                    "archive",
                    "check",
                    "path",
                ]
            ),
        )

    def test_whoami_matches_the_cli(self):
        os.environ["PI_SESSION_ID"] = "session-123"
        self.assertEqual(call("whoami"), self.run_cli("whoami").stdout.strip())

    def test_inbox_without_a_project_name_is_actionable(self):
        self.run_cli("init")
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace(f'project = "{self.root.name}"\n', ""))

        with self.assertRaisesRegex(ToolError, "this repository has no project name"):
            call("inbox")

    def test_check_and_fix_include_problem_severity(self):
        call("add", title="Warning", description="static/photos/*.jpg")

        self.assertEqual(call("check"), self.json("check"))
        self.assertEqual(call("fix"), self.json("fix"))

    def test_same_json_as_cli(self):
        added = call("add", title="Hi", description="x", ac=["One"], label=["cli"])
        self.assertEqual(added, self.json("show", "1"))
        edited = call("edit", id="1", status="doing", check=[1], plan="Do it.", note="Started.")
        self.assertIn("todo → doing", edited["history"])
        self.assertIn("ticked acceptance criteria", edited["history"])
        self.assertEqual(call("show", id="TASK-1"), self.json("show", "1"))
        self.assertEqual(call("note", id="1", text="Started."), self.json("show", "1"))
        self.assertEqual(call("list", status=["doing"]), self.json("list", "-s", "doing"))
        self.assertEqual(call("path", id="1"), self.json("path", "1"))
        self.assertEqual(call("check"), [])
        self.assertEqual(call("move", id="1", context="human")["id"], "HUMAN-1")
        self.assertTrue(call("archive", id="HUMAN-1")["archived"])

    def test_archives_every_done_task_without_an_id(self):
        call("add", title="Done", description="x")
        call("add", title="Human done", description="x", context="human")
        call("edit", id="1", status="review")
        os.environ["CHITTY_ACTOR"] = "reviewer"
        call("edit", id="1", status="done", note="Reviewed: ready.")
        os.environ["CHITTY_ACTOR"] = "test-agent"
        call("edit", id="HUMAN-1", status="review")
        os.environ["CHITTY_ACTOR"] = "reviewer"
        call("edit", id="HUMAN-1", status="done", note="Reviewed: ready.")

        archived = call("archive")

        self.assertEqual([task["id"] for task in archived], ["TASK-1", "HUMAN-1"])

    def test_adds_backlog_without_a_description(self):
        with self.assertRaisesRegex(ToolError, "requires -s review first"):
            call("add", title="Done immediately", description="x", status="done")
        task = call("add", title="Explore sync", status="backlog")

        self.assertEqual(task["status"], "backlog")
        self.assertEqual(task["description"], "This ticket needs refining.")

    def test_review_verdict_is_required_and_complete(self):
        call("add", title="Review", description="x", ac=["One"])
        call("edit", id="1", status="review")
        os.environ["CHITTY_ACTOR"] = "reviewer"
        before = call("show", id="1")
        with self.assertRaisesRegex(ToolError, "missing 1"):
            call("edit", id="1", status="done", note="Reviewed: ready.")
        self.assertEqual(call("show", id="1"), before)
        completed = call("edit", id="1", status="done", note="Reviewed: ready.\n1: pass - complete")
        self.assertEqual(completed["status"], "done")

    def test_errors_reach_the_client(self):
        with self.assertRaisesRegex(ToolError, "no task TASK-9"):
            call("show", id="9")
        with self.assertRaisesRegex(ToolError, "nothing to change"):
            call("edit", id="9")
        call("add", title="Review", description="x")
        call("edit", id="1", status="review")
        with self.assertRaisesRegex(ToolError, "review → doing requires --note"):
            call("edit", id="1", status="doing")

    def test_cross_branch_write_error_matches_the_cli(self):
        def git(*args: str) -> None:
            subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)

        commit_seconds = 0

        def commit(message: str) -> None:
            nonlocal commit_seconds
            commit_seconds += 1
            environment = {
                **os.environ,
                "GIT_AUTHOR_DATE": f"2026-10-23T00:00:{commit_seconds:02}+00:00",
                "GIT_COMMITTER_DATE": f"2026-10-23T00:00:{commit_seconds:02}+00:00",
            }
            git("add", "--all")
            subprocess.run(
                ["git", "commit", "--quiet", "-m", message],
                cwd=self.root,
                check=True,
                capture_output=True,
                env=environment,
            )

        git("init", "--quiet")
        git("config", "user.email", "test@example.com")
        git("config", "user.name", "Test")
        git("branch", "-M", "main")
        call("add", title="Task", description="x")
        commit("main task")
        git("checkout", "--quiet", "-b", "worker")
        path = self.root / "chitty/tasks/TASK-1--task.md"
        path.write_text(path.read_text().replace("status: todo", "status: doing"))
        commit("claim task")
        git("checkout", "--quiet", "main")

        with self.assertRaisesRegex(ToolError, "worker"):
            call("note", id="1", text="Blocked.")

    def test_guide_resource(self):
        contents = asyncio.run(server.read_resource("chitty://guide"))
        self.assertEqual([c.content for c in contents], [guide()])  # type: ignore[union-attr]
        self.assertEqual(server.instructions, guide())
