from unittest.mock import patch

from chitty.ids import TaskId
from chitty.store import Repo
from tests.test_source_copy_errors import SourceCopyErrorChecks


class TestAuthoritativeListing(SourceCopyErrorChecks):
    def test_standalone_does_not_read_history(self):
        self.file(1)
        repo = Repo.open(self.root)
        with patch("chitty.git.historical_files", side_effect=AssertionError("history")):
            tasks = repo.tasks(repo.default_context, "active")
        self.assertEqual([str(task.id) for task in tasks], ["TASK-1"])

    def test_branch_placement(self):
        self.init_git()
        first = self.file(1)
        self.file(2)
        self.commit()
        self.git("checkout", "-b", "task-1")
        archive = first.parent / "archive"
        archive.mkdir()
        first.rename(archive / first.name)
        (archive / first.name).write_text(
            (archive / first.name).read_text().replace("original", "archived branch")
        )
        self.commit()
        self.git("checkout", "main")
        self.git("checkout", "-b", "task-2")
        self.file(2, "branch two")
        self.commit()
        self.git("checkout", "main")
        self.git("checkout", "-b", "task-3")
        self.file(3, "branch three")
        self.commit()
        self.git("checkout", "main")
        self.file(2).write_text("not frontmatter")
        repo = Repo.open(self.root)
        for number, title in [(1, "archived branch"), (2, "branch two"), (3, "branch three")]:
            found = repo.lookup(TaskId.parse(f"TASK-{number}"))
            assert found is not None
            self.assertEqual(found.task.frontmatter.title, title)
        self.assertEqual(
            {t.task.frontmatter.title for t in repo.tasks(repo.default_context, "active")},
            {"branch two", "branch three"},
        )
        self.assertEqual(
            [t.task.frontmatter.title for t in repo.tasks(repo.default_context, "archived")],
            ["archived branch"],
        )
