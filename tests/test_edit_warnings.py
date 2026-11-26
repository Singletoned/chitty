import functools
import operator

from chitty.model import parse
from tests.test_cli import CliTestCase
from tests.test_mcp import call


class TestEditWarnings(CliTestCase):
    # Fixed examples exercise the status transitions and both front ends.
    def test_warnings_on_checked_moves(self):
        criteria = functools.reduce(
            operator.iadd, (["--ac", f"Criterion {i}"] for i in range(6)), []
        )
        task = self.json("add", "Ticket", "-s", "planning", "-d", "Description", *criteria)
        task_id = task["id"]
        for status in ("cold-read", "planning", "todo"):
            result = self.run_cli("edit", task_id, "-s", status)
            self.assertEqual(
                "warning: 6 acceptance criteria" in result.output, status != "planning"
            )
        self.assertNotIn(
            "warning: 6 acceptance criteria",
            self.run_cli("add", "Other", "-s", "todo", "-d", "Description", *criteria).output,
        )
        self.run_cli("edit", task_id, "-s", "planning")
        result = call("edit", id=task_id, status="todo")
        self.assertTrue(
            any("warning: 6 acceptance criteria" in warning for warning in result["warnings"])
        )
        self.assertNotIn("warnings", call("edit", id=task_id, status="planning"))
        self.assertNotIn("warning:", self.run_cli("edit", task_id, "-s", "todo", "--json").output)

    def test_missing_dependency_refuses_move_without_changing_file(self):
        task = self.json("add", "Ticket", "-s", "planning", "-d", "Description")
        from pathlib import Path

        path = Path(task["path"])
        path.write_text(parse(path.read_text()).with_field("depends_on", ["TASK-999999"]).render())
        result = self.run_cli("edit", task["id"], "-s", "todo", exit_code=1)
        self.assertIn("TASK-999999", result.output)
        self.assertEqual(parse(path.read_text()).frontmatter.status, "planning")
