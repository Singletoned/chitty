import asyncio
import os
from pathlib import Path

from mcp_types import CallToolResult

from chitty.mcp import create_server
from tests.test_cli import CliTestCase


class TestRenumber(CliTestCase):
    def setUp(self):
        super().setUp()
        tasks = self.root / "chitty/tasks"
        for title in ("First", "Second"):
            self.run_cli("add", title, "-d", "Description.")
        self.run_cli("add", "Dependent", "-d", "Description.", "--depends-on", "1")
        self.run_cli("add", "Child", "-d", "Description.", "--parent", "1")
        # A merge left two files with `TASK-24`, and two tickets naming it.
        (tasks / "TASK-1--first.md").rename(tasks / "TASK-24--first.md")
        (tasks / "TASK-2--second.md").rename(tasks / "TASK-24--second.md")
        for name, old, new in (
            ("TASK-3--dependent.md", "- TASK-1\n", "- TASK-24\n"),
            ("TASK-4--child.md", "parent: TASK-1\n", "parent: TASK-24\n"),
        ):
            path = tasks / name
            text = path.read_text()
            self.assertIn(old, text)
            path.write_text(text.replace(old, new))
        self.tasks = tasks

    def snapshot(self) -> dict[Path, bytes]:
        return {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}

    def test_renumbers_only_that_file_and_lists_references(self):
        self.assertIn("used by more than one file", self.run_cli("check", exit_code=1).stdout)
        before = self.snapshot()

        result = self.run_cli("renumber", "chitty/tasks/TASK-24--second.md")

        renumbered = self.tasks / "TASK-25--second.md"
        self.assertFalse((self.tasks / "TASK-24--second.md").exists())
        self.assertIn("moved_from: TASK-24\n", renumbered.read_text())
        self.assertIn(f"renumbered TASK-25 {renumbered}", result.stdout)
        for name in ("TASK-24--first.md", "TASK-3--dependent.md", "TASK-4--child.md"):
            path = self.tasks / name
            self.assertEqual(path.read_bytes(), before[path], name)
        references = [line for line in result.stdout.splitlines() if line.startswith("check")]
        self.assertEqual(
            references,
            [
                f"check reference to TASK-24 in TASK-3 {self.tasks / 'TASK-3--dependent.md'}",
                f"check reference to TASK-24 in TASK-4 {self.tasks / 'TASK-4--child.md'}",
            ],
        )
        self.run_cli("check")
        self.assertEqual(self.json("show", "25")["moved_from"], "TASK-24")

    def test_refuses_without_changing_anything(self):
        before = self.snapshot()
        cases = (
            ("chitty.toml", "not a task file in a context"),
            ("chitty/tasks/TASK-99--missing.md", "not a task file in a context"),
        )
        for path, message in cases:
            with self.subTest(path):
                self.assertIn(message, self.run_cli("renumber", path, exit_code=1).stderr)
                self.assertEqual(self.snapshot(), before)

    def test_accepts_an_archived_path_relative_to_the_working_directory(self):
        archive = self.tasks / "archive"
        archive.mkdir()
        (self.tasks / "TASK-24--second.md").rename(archive / "TASK-24--second.md")
        os.chdir(archive)

        self.run_cli("renumber", "TASK-24--second.md")

        self.assertIn("moved_from: TASK-24\n", (archive / "TASK-25--second.md").read_text())
        self.assertTrue((self.tasks / "TASK-24--first.md").exists())
        self.run_cli("check")

    def test_mcp_tool_matches_the_cli_json(self):
        result = asyncio.run(
            create_server(Path.cwd()).call_tool(
                "renumber", {"path": str(self.tasks / "TASK-24--second.md")}
            )
        )
        assert isinstance(result, CallToolResult)
        content = result.structured_content
        assert content is not None
        shown = self.json("show", "25")
        shown.pop("running")
        self.assertEqual(content["task"], shown)
        self.assertEqual(
            [reference["id"] for reference in content["references"]], ["TASK-3", "TASK-4"]
        )

    def test_json_lists_references(self):
        data = self.json("renumber", str(self.tasks / "TASK-24--first.md"))
        self.assertEqual(data["task"]["id"], "TASK-25")
        self.assertEqual(
            data["references"],
            [
                {"id": "TASK-3", "path": str(self.tasks / "TASK-3--dependent.md")},
                {"id": "TASK-4", "path": str(self.tasks / "TASK-4--child.md")},
            ],
        )

    def test_help(self):
        help_text = self.run_cli("renumber", "--help").stdout
        self.assertIn("A unique ID is renumbered", help_text)
        self.assertIn("its references are rewritten", help_text)


class TestRenumberUnique(CliTestCase):
    def test_rewrites_references_for_numbered_and_provisional_tickets(self):
        for provisional in (False, True):
            with self.subTest(provisional=provisional):
                target = self.json("add", f"Target {provisional}", "-d", "Description.")
                old = target["id"]
                self.run_cli("add", f"Uses {provisional}", "-d", f"See {old}.", "--depends-on", old)
                path = Path(target["path"])
                if provisional:
                    path.write_text(
                        path.read_text().replace(
                            "status: todo\n", "status: todo\nprovisional: true\n"
                        )
                    )
                result = self.json("renumber", str(path))
                new = result["task"]["id"]
                self.assertEqual(new, f"TASK-{int(old.split('-')[1]) + 2}")
                self.assertEqual(result["task"]["moved_from"], old)
                self.assertFalse(result["task"].get("provisional"))
                self.assertEqual(result["references"], [])
                uses = self.json("show", f"TASK-{int(old.split('-')[1]) + 1}")
                self.assertEqual(uses["depends_on"], [new])
                self.assertIn(new, uses["description"])
                self.assertNotIn(old, uses["description"])
                self.run_cli("check")

    def test_refuses_unique_ticket_in_random_id_context(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("[contexts.tasks]", "[contexts.tasks]\nrandom_ids = true")
        )
        target = self.json("add", "Target", "-d", "Description.")
        path = Path(target["path"])
        before = path.read_bytes()
        result = self.run_cli("renumber", str(path), exit_code=1)
        self.assertIn("random-ID context", result.stderr)
        self.assertEqual(path.read_bytes(), before)


class TestMoveReportsTheMovedTask(CliTestCase):
    def test_move_reports_the_moved_task_not_the_last_one_rewritten(self):
        self.run_cli("add", "Moved one", "-c", "human", "-d", "Description.")
        self.run_cli("add", "Zzz other", "-c", "human", "-d", "Description.")
        moved = self.json("move", "HUMAN-1", "tasks")
        self.assertEqual((moved["id"], moved["title"]), ("TASK-1", "Moved one"))
