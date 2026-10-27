import unittest
from datetime import date

from chitty.import_backlog import ConvertedTask, renumber
from chitty.model import new_task, parse


class TestRenumber(unittest.TestCase):
    def test_subtasks_become_flat_ids_and_rewrite_known_references(self):
        parent = ConvertedTask(
            "TASK-7", new_task("Parent", date(2026, 1, 1), "See TASK-7.3.", [], {}), ()
        )
        child = ConvertedTask(
            "TASK-7.3",
            new_task(
                "Child", date(2026, 1, 1), "Depends on TASK-99.", [], {"depends_on": ["TASK-7"]}
            ),
            (),
        )
        result = renumber([parent, child], "WORK")

        self.assertEqual([task.new_id for task in result], ["WORK-7", "WORK-8"])
        self.assertEqual(result[1].task.frontmatter.parent, "WORK-7")
        self.assertEqual(result[1].task.frontmatter.depends_on, ["WORK-7"])
        self.assertIn("WORK-8", result[0].task.section("Description") or "")
        self.assertIn("Backlog.md ID: TASK-7.3", result[1].task.section("Notes") or "")
        self.assertEqual(result[1].reports[-1], "TASK-7.3: reference to unknown ID TASK-99")
        for task in result:
            parse(task.task.render())
