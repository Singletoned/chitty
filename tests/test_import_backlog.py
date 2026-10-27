import tempfile
import textwrap
import unittest
from pathlib import Path

from chitty.import_backlog import convert
from chitty.model import parse

SAMPLE = (Path(__file__).parent / "fixtures/backlog/task-7.3.md").read_text()


class TestImportBacklog(unittest.TestCase):
    def test_maps_legacy_file_to_valid_task_and_reports_loss(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "task-7.3.md"
            path.write_text(textwrap.dedent(SAMPLE))
            converted = convert(path)

        task = converted.task
        self.assertEqual(converted.old_id, "TASK-7.3")
        self.assertEqual(task.frontmatter.status, "backlog")
        self.assertEqual(task.section("History"), "- 2026-10-20 → backlog")
        self.assertEqual(task.frontmatter.owner, "ed")
        self.assertEqual(task.frontmatter.depends_on, ["TASK-1"])
        self.assertEqual(
            task.section("Plan"), "Plan.\n\n### Unexpected heading\n\nPreserved content."
        )
        self.assertEqual(task.section("Summary"), "Finished.")
        self.assertEqual([criterion.checked for criterion in task.criteria], [True])
        self.assertEqual(
            converted.reports,
            (
                "TASK-7.3: unknown status 'Backburner'",
                "TASK-7.3: demoted heading 'Unexpected heading'",
            ),
        )
        parse(task.render())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "draft.md"
            path.write_text(textwrap.dedent(SAMPLE).replace("status: Backburner", "status: Done"))
            self.assertEqual(convert(path, draft=True).task.frontmatter.status, "backlog")
