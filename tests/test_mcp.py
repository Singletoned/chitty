import asyncio
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
                    "pull",
                    "list",
                    "show",
                    "edit",
                    "note",
                    "fix",
                    "move",
                    "archive",
                    "check",
                    "path",
                ]
            ),
        )

    def test_same_json_as_cli(self):
        added = call("add", title="Hi", description="x", ac=["One"], label=["cli"])
        self.assertEqual(added, self.json("show", "1"))
        edited = call("edit", id="1", status="doing", check=[1], plan="Do it.", note="Started.")
        self.assertTrue(edited["history"].endswith("todo → doing"))
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
        call("edit", id="1", status="done")
        call("edit", id="HUMAN-1", status="review")
        call("edit", id="HUMAN-1", status="done")

        archived = call("archive")

        self.assertEqual([task["id"] for task in archived], ["TASK-1", "HUMAN-1"])

    def test_adds_backlog_without_a_description(self):
        with self.assertRaisesRegex(ToolError, "requires -s review first"):
            call("add", title="Done immediately", description="x", status="done")
        task = call("add", title="Explore sync", status="backlog")

        self.assertEqual(task["status"], "backlog")
        self.assertEqual(task["description"], "This ticket needs refining.")

    def test_errors_reach_the_client(self):
        with self.assertRaisesRegex(ToolError, "no task TASK-9"):
            call("show", id="9")
        with self.assertRaisesRegex(ToolError, "nothing to change"):
            call("edit", id="9")
        call("add", title="Review", description="x")
        call("edit", id="1", status="review")
        with self.assertRaisesRegex(ToolError, "review → doing requires --note"):
            call("edit", id="1", status="doing")

    def test_guide_resource(self):
        contents = asyncio.run(server.read_resource("chitty://guide"))
        self.assertEqual([c.content for c in contents], [guide()])  # type: ignore[union-attr]
        self.assertEqual(server.instructions, guide())
