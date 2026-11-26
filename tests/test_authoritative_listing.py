from unittest.mock import patch

from chitty.ids import TaskId
from chitty.store import Repo
from tests.test_source_copy_errors import SourceCopyErrorChecks


class TestAuthoritativeListing(SourceCopyErrorChecks):
    def test_standalone_does_not_read_history(self):
        self.file(1)
        repo = Repo.open(self.root)
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
        self.check_placement()

    def check_placement(self):
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

        expected = {"archived branch", "branch two", "branch three"}
        self.assertEqual(len(repo.all_tasks()), 3)
        self.assertEqual({t.task.frontmatter.title for t in repo.all_tasks()}, expected)
        self.assertEqual({t["title"] for t in self.json("list")}, {"branch two", "branch three"})

    def test_duplicate_across_locations(self):
        first = self.file(1)
        archive = first.parent / "archive"
        archive.mkdir()
        other = archive / first.name
        other.write_text(first.read_text())
        result = self.run_cli("list", "--json", exit_code=1)
        self.assertIn("more than one file", result.output)
        self.assertIn(str(first), result.output)
        self.assertIn(str(other), result.output)

    def test_identical_edits_on_both_branches(self):
        self.setup_base()
        self.git("checkout", "-b", "task-1")
        self.file(1, "same edit")
        self.commit()
        self.git("checkout", "main")
        self.file(1, "same edit")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "main edit")
        self.assertNotEqual(self.git("rev-parse", "main"), self.git("rev-parse", "task-1"))

        listed = self.json("list")
        ticket = next(t for t in listed if t["id"] == "TASK-1")
        self.assertEqual(ticket["title"], "same edit")
        self.assertNotIn("conflict", ticket)
        shown = self.run_cli("show", "TASK-1")
        self.assertIn("same edit", shown.output)

    def test_conflict_and_isolated_allocation(self):
        self.setup_changed_both()
        listed = self.json("list")
        self.assertIn("changed on both", next(t for t in listed if t["id"] == "TASK-1")["conflict"])
        for args in [("archive",)]:
            before = {p: p.read_bytes() for p in (self.root / "chitty").rglob("*.md")}
            head = self.git("rev-parse", "HEAD")
            index = self.git("ls-files", "--stage")
            result = self.run_cli(*args, exit_code=1)
            self.assertIn("TASK-1", result.output)
            self.assertIn("changed on both", result.output)
            self.assertEqual(
                before, {p: p.read_bytes() for p in (self.root / "chitty").rglob("*.md")}
            )
            self.assertEqual(head, self.git("rev-parse", "HEAD"))
            self.assertEqual(index, self.git("ls-files", "--stage"))
        occupied = self.file("AAAAAA")
        self.commit()
        original = occupied.read_bytes()
        self.git("checkout", "-b", "feature")
        self.file(4).write_text("not frontmatter")
        with patch("chitty.store._provisional_draw", side_effect=[0] * 6 + [1] + [0] * 5):
            added = self.json("add", "new ticket", "-d", "description")
        self.assertEqual(added["id"], "TASK-BAAAAA")
        self.assertEqual(occupied.read_bytes(), original)
