from datetime import date

from chitty.errors import ChittyError
from chitty.ids import TaskId
from chitty.store import Edit, Repo
from tests.support import RepoTestCase

TODAY = date(2026, 10, 23)


class StoreTestCase(RepoTestCase):
    def setUp(self):
        super().setUp()
        self.repo = Repo.open(self.root)
        self.tasks = self.repo.context("tasks")
        self.human = self.repo.context("human")

    def add(self, title, context=None, **fields):
        context = context or self.tasks
        return self.repo.add(context, title, "Describe.", [], fields, TODAY).task


class TestStore(StoreTestCase):
    def test_missing_directory_is_empty(self):
        self.assertEqual(self.repo.tasks(self.human, "all"), [])
        self.assertFalse(self.human.directory.exists())

    def test_add_numbers_sequentially_and_names_files(self):
        first = self.add("Add search!")
        second = self.add("日本語")
        self.assertEqual(first.id, TaskId("TASK", 1))
        self.assertEqual(first.path, self.root / "chitty/tasks/TASK-1--add-search.md")
        self.assertEqual(second.path.name, "TASK-2.md")
        self.assertEqual([t.id.number for t in self.repo.tasks(self.tasks, "active")], [1, 2])

    def test_delete_mode_requires_git_history_for_new_ids(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("[contexts.tasks]", 'archive = "delete"\n\n[contexts.tasks]')
        )
        repo = Repo.open(self.root)

        with self.assertRaisesRegex(ChittyError, "git history is unavailable"):
            repo.add(repo.context("tasks"), "One", "Describe.", [], {}, TODAY)

    def test_numbers_count_archived_tasks(self):
        self.add("One")
        self.repo.archive(TaskId("TASK", 1))
        self.assertEqual(self.add("Two").id.number, 2)

    def test_add_checks_dependencies(self):
        with self.assertRaisesRegex(ChittyError, "no task HUMAN-1"):
            self.add("Blocked", depends_on=["HUMAN-1"])
        self.add("Password", context=self.human)
        self.assertEqual(
            self.add("Blocked", depends_on=["HUMAN-1"]).task.frontmatter.depends_on, ["HUMAN-1"]
        )

    def test_find_and_resolve(self):
        self.add("One")
        self.assertEqual(self.repo.find(self.repo.resolve("1")).task.frontmatter.title, "One")
        with self.assertRaisesRegex(ChittyError, "no task TASK-9"):
            self.repo.find(TaskId("TASK", 9))
        with self.assertRaisesRegex(ChittyError, "prefix 'NOPE'"):
            self.repo.find(TaskId("NOPE", 1))

    def test_save_skips_unchanged(self):
        stored = self.add("One")
        mtime = stored.path.stat().st_mtime_ns
        change = self.repo.edit(stored.id, Edit(status="todo"))
        self.assertEqual(change.paths, ())
        self.assertEqual(stored.path.stat().st_mtime_ns, mtime)
        change = self.repo.edit(stored.id, Edit(status="doing"))
        self.assertEqual(change.paths, (stored.path,))
        with self.assertRaisesRegex(ChittyError, "nothing to change"):
            self.repo.edit(stored.id, Edit(add_labels=[]))

    def test_archive_and_restore(self):
        stored = self.add("One")
        archived = self.repo.archive(stored.id).task
        self.assertEqual(archived.path, self.root / "chitty/tasks/archive/TASK-1--one.md")
        self.assertEqual(self.repo.tasks(self.tasks, "active"), [])
        self.assertEqual(len(self.repo.tasks(self.tasks, "archived")), 1)
        with self.assertRaisesRegex(ChittyError, "already archived"):
            self.repo.archive(stored.id)
        self.assertEqual(self.repo.restore(stored.id).task.path, stored.path)

    def test_move_rewrites_references(self):
        self.add("First")
        self.add("Second")
        blocker = self.add("Needs a person")
        dependent = self.add("Blocked", depends_on=[str(blocker.id)])
        self.add("Human thing", context=self.human)
        change = self.repo.move(blocker.id, self.human)
        moved = change.task
        self.assertEqual(moved.id, TaskId("HUMAN", 2))
        self.assertEqual(moved.path.name, "HUMAN-2--needs-a-person.md")
        self.assertEqual(moved.task.frontmatter.moved_from, "TASK-3")
        self.assertFalse(blocker.path.exists())
        rewritten = self.repo.find(dependent.id)
        self.assertEqual(rewritten.task.frontmatter.depends_on, ["HUMAN-2"])
        self.assertEqual(set(change.paths), {blocker.path, moved.path, dependent.path})

    def test_unexpected_files_are_errors(self):
        self.add("One")
        (self.tasks.directory / "notes.txt").write_text("hi")
        with self.assertRaisesRegex(ChittyError, "notes.txt"):
            self.repo.tasks(self.tasks, "active")

    def test_wrong_prefix_is_an_error(self):
        self.tasks.directory.mkdir(parents=True)
        (self.tasks.directory / "HUMAN-1.md").write_text("x")
        with self.assertRaisesRegex(ChittyError, "does not belong"):
            self.repo.tasks(self.tasks, "active")

    def test_malformed_file_error_names_path(self):
        stored = self.add("One")
        stored.path.write_text("nope\n")
        with self.assertRaisesRegex(ChittyError, "TASK-1--one.md: file must start"):
            self.repo.find(stored.id)
