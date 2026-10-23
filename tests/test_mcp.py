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
            sorted(["add", "list", "show", "edit", "move", "archive", "restore", "check", "path"]),
        )

    def test_same_json_as_cli(self):
        added = call("add", title="Hi", description="x", ac=["One"], label=["cli"])
        self.assertEqual(added, self.json("show", "1"))
        call("edit", id="1", status="doing", check=[1], plan="Do it.", note="Started.")
        self.assertEqual(call("show", id="TASK-1"), self.json("show", "1"))
        self.assertEqual(call("list", status=["doing"]), self.json("list", "-s", "doing"))
        self.assertEqual(call("path", id="1"), self.json("path", "1"))
        self.assertEqual(call("check"), [])
        self.assertEqual(call("move", id="1", context="human")["id"], "HUMAN-1")
        self.assertTrue(call("archive", id="HUMAN-1")["archived"])
        self.assertFalse(call("restore", id="HUMAN-1")["archived"])

    def test_errors_reach_the_client(self):
        with self.assertRaisesRegex(ToolError, "no task TASK-9"):
            call("show", id="9")
        with self.assertRaisesRegex(ToolError, "nothing to change"):
            call("edit", id="9")

    def test_guide_resource(self):
        contents = asyncio.run(server.read_resource("chitty://guide"))
        self.assertEqual([c.content for c in contents], [guide()])  # type: ignore[union-attr]
