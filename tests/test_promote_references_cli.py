import json

from tests.test_cli import CliTestCase


class TestPromoteReferencesCli(CliTestCase):
    def setUp(self):
        super().setUp()
        self.run_cli(
            "add",
            "First task",
            "-s",
            "planning",
            "-d",
            "Mentions TASK-2.",
            "--ac",
            "Mentions TASK-1, TASK-9 and TASK-2.",
        )
        self.run_cli("add", "Second task", "-s", "doing", "-d", "Work in progress.")

    def test_promotion_lists_referenced_tasks_once_after_result(self):
        output = self.run_cli("edit", "TASK-1", "-s", "todo").stdout.splitlines()
        self.assertEqual(len(output), 3)
        self.assertTrue(output[0].startswith("updated TASK-1 "))
        self.assertEqual(output[1:], ["TASK-2 doing Second task", "TASK-9 no such task"])

    def test_references_are_silent_except_for_first_textual_promotion(self):
        self.run_cli("edit", "TASK-1", "-s", "todo")
        self.assertEqual(self.run_cli("edit", "TASK-1", "-s", "todo").stdout, "unchanged TASK-1\n")
        output = self.run_cli("edit", "TASK-1", "--title", "Renamed").stdout
        self.assertEqual(
            output, f"updated TASK-1 {self.root}/chitty/tasks/TASK-1--renamed.md actor test-agent\n"
        )

        # A fresh task in planning exercises transitions that do not promote to todo.
        self.run_cli("add", "Third task", "-s", "planning", "-d", "See TASK-2.")
        output = self.run_cli("edit", "TASK-3", "-s", "doing").stdout
        self.assertEqual(
            output,
            f"updated TASK-3 {self.root}/chitty/tasks/TASK-3--third-task.md actor test-agent\n",
        )
        self.run_cli("add", "Fourth task", "-s", "planning", "-d", "See TASK-2.")
        output = self.run_cli("edit", "TASK-4", "-s", "todo", "--json").stdout
        self.assertEqual(json.loads(output)["status"], "todo")
        self.assertNotIn("TASK-2 doing", output)
        self.assertNotIn("TASK-9 no such task", output)

    def test_duplicate_reference_is_reported_without_failing_promotion(self):
        original = self.root / "chitty/tasks/TASK-2--second-task.md"
        (self.root / "chitty/tasks/TASK-2--duplicate.md").write_text(original.read_text())
        result = self.run_cli("edit", "TASK-1", "-s", "todo")
        self.assertIn("TASK-2 unreadable: TASK-2 is used by more than one file", result.output)
        self.assertIn("TASK-9 no such task", result.output)
        self.assertIn("status: todo", self.run_cli("show", "TASK-1").stdout)
