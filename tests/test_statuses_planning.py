import asyncio
import unittest
from pathlib import Path
from typing import Any

from mcp_types import CallToolResult

from chitty.mcp import server
from chitty.store import guide
from tests.test_cli import CliTestCase

REPO = Path(__file__).resolve().parents[1]


def call(name: str, **arguments: Any) -> Any:
    result = asyncio.run(server.call_tool(name, arguments))
    assert isinstance(result, CallToolResult)
    content = result.structured_content
    assert content is not None
    return content.get("result", content)


class TestPlanningStatuses(CliTestCase):
    def add_planning_and_cold_read(self):
        self.run_cli("add", "Plan me", "-s", "planning", "-d", "x")
        self.run_cli("add", "Read me", "-d", "x")
        self.run_cli("edit", "TASK-2", "-s", "cold-read")

    def test_cli_add_and_edit_accept_both_statuses(self):
        self.run_cli("add", "Plan me", "-s", "planning", "-d", "x")
        self.assertEqual(self.json("show", "TASK-1")["status"], "planning")
        self.run_cli("edit", "TASK-1", "-s", "cold-read")
        self.assertEqual(self.json("show", "TASK-1")["status"], "cold-read")

    def test_mcp_edit_accepts_both_statuses(self):
        self.run_cli("add", "Plan me", "-d", "x")
        call("edit", id="TASK-1", status="planning")
        self.assertEqual(self.json("show", "TASK-1")["status"], "planning")
        call("edit", id="TASK-1", status="cold-read")
        self.assertEqual(self.json("show", "TASK-1")["status"], "cold-read")

    def test_list_without_status_shows_planning_and_cold_read(self):
        self.add_planning_and_cold_read()
        self.run_cli("add", "Idea", "-c", "tasks", "-s", "backlog")
        self.run_cli("add", "Finished", "-c", "tasks", "-d", "x")
        self.run_cli("edit", "TASK-4", "-s", "review")
        self.run_cli(
            "edit",
            "TASK-4",
            "-s",
            "done",
            "--note",
            "Reviewed: complete",
            "--override-review-independence",
        )
        output = self.run_cli("list").stdout
        self.assertIn("📝 plan", output)
        self.assertIn("🔎 cold", output)
        self.assertNotIn("bklog", output)
        self.assertNotIn("done", output)

    def test_mcp_list_without_status_returns_planning_and_cold_read(self):
        self.add_planning_and_cold_read()
        self.run_cli("add", "Idea", "-s", "backlog")
        self.run_cli("add", "Finished", "-d", "x")
        self.run_cli("edit", "TASK-4", "-s", "review")
        self.run_cli(
            "edit",
            "TASK-4",
            "-s",
            "done",
            "--note",
            "Reviewed: complete",
            "--override-review-independence",
        )
        ids = sorted(task["id"] for task in call("list"))
        self.assertEqual(ids, ["TASK-1", "TASK-2"])

    def test_next_never_picks_planning_or_cold_read(self):
        self.add_planning_and_cold_read()
        result = self.run_cli("next", exit_code=3)
        self.assertIn("no next ticket", result.stderr)

    def test_plan_guide_names_both_statuses(self):
        text = " ".join(guide("plan").split())
        self.assertIn("-s planning", text)
        self.assertIn("-s cold-read", text)

    def test_docs_list_both_statuses(self):
        for name in ("docs/plan/cli.md", "README.md"):
            text = (REPO / name).read_text()
            with self.subTest(document=name):
                self.assertIn("📝 plan", text)
                self.assertIn("🔎 cold", text)


if __name__ == "__main__":
    unittest.main()
