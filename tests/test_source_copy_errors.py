from unittest.mock import patch

from chitty.errors import ChittyError
from chitty.ids import TaskId
from chitty.store import Repo
from chitty.ticket_source import ticket_source
from tests import test_ticket_ids
from tests.test_cli import CliTestCase


class SourceCopyErrorChecks(CliTestCase):
    git = test_ticket_ids.TestTicketIds.git
    init_git = test_ticket_ids.TestTicketIds.init_git
    commit = test_ticket_ids.TestTicketIds.commit

    def file(self, number, title="original"):
        path = self.root / f"chitty/tasks/TASK-{number}--example.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\ntitle: {title}\nstatus: todo\ncreated: 2026-01-01\n---\n"
            "\n## Description\n\nFixture.\n"
        )
        return path

    def setup_base(self):
        self.init_git()
        self.file(1)
        self.file(2)
        self.file(3)
        self.commit()

    def branch(self):
        self.git("checkout", "-b", "task-1")
        self.file(1, "branch")
        self.commit()

    def setup_diverged(self):
        self.setup_base()
        self.branch()
        self.git("update-ref", "refs/remotes/origin/task-1", self.git("rev-parse", "HEAD"))
        self.git("reset", "--hard", "main")
        self.file(1, "local")
        self.commit()
        self.git("checkout", "main")

    def setup_changed_both(self):
        self.setup_base()
        self.branch()
        self.git("checkout", "main")
        self.file(1, "main")
        self.commit()

    def setup_orphan(self):
        self.setup_base()
        self.git("checkout", "--orphan", "task-1")
        self.file(1, "orphan")
        self.commit()
        self.git("checkout", "main")

    def setup_malformed_branch(self):
        self.setup_base()
        self.git("checkout", "-b", "task-1")
        path = self.file(1)
        path.write_text(path.read_text().replace("\n---\n", "\n", 1))
        self.commit()
        self.git("checkout", "main")

    def check_unaffected(self, repo):
        self.assertIn(TaskId.parse("TASK-2"), repo.ticket_ids())
        try:
            copy = repo.source_copy(TaskId.parse("TASK-2"))
        except ChittyError as error:
            self.fail(f"unrelated ticket failed: {error}")
        self.assertIsNotNone(copy)
        self.assertEqual(copy.task.frontmatter.title, "original")

    def check_error(self, repo, number, *parts):
        with self.assertRaises(ChittyError) as raised:
            repo.source_copy(TaskId.parse(f"TASK-{number}"))
        for part in parts:
            self.assertIn(str(part), str(raised.exception))
        return str(raised.exception)

    def check_branch_error(self, repo, *parts):
        self.check_error(repo, 1, *parts)
        self.check_unaffected(repo)

    def check_malformed_branch(self, repo):
        message = self.check_error(repo, 1, "frontmatter is not closed")
        self.assertTrue(message.startswith("task-1:chitty/tasks/TASK-1--"))
        self.check_unaffected(repo)

    def check_malformed_working(self, repo):
        path = repo.root / "chitty/tasks/TASK-3--example.md"
        message = self.check_error(repo, 3, "frontmatter is not closed")
        self.assertTrue(message.startswith(f"{path}: "))


class TestSourceCopyErrors(SourceCopyErrorChecks):
    def test_diverged(self):
        self.setup_diverged()
        self.check_branch_error(
            Repo.open(self.root), "has diverged refs", "origin/task-1", "task-1"
        )

    def test_changed_both(self):
        self.setup_changed_both()
        self.check_branch_error(Repo.open(self.root), "changed on both", "task-1", "main")

    def test_orphan(self):
        self.setup_orphan()
        self.check_branch_error(Repo.open(self.root), "unrelated histories")

    def test_malformed_branch(self):
        self.setup_malformed_branch()
        self.check_malformed_branch(Repo.open(self.root))

    def test_duplicate_working(self):
        self.setup_base()
        other = self.root / "chitty/tasks/TASK-2--duplicate.md"
        other.write_text(self.file(2).read_text())
        repo = Repo.open(self.root)
        self.check_error(
            repo,
            2,
            "TASK-2 is used by more than one file:",
            repo.root / "chitty/tasks/TASK-2--example.md",
            repo.root / "chitty/tasks/TASK-2--duplicate.md",
        )

    def test_malformed_working(self):
        self.setup_base()
        path = self.file(3)
        path.write_text(path.read_text().replace("\n---\n", "\n", 1))
        self.check_malformed_working(Repo.open(self.root))


class TestSourceCopyErrorMutants(SourceCopyErrorChecks):
    def test_eager_selection(self):
        self.setup_diverged()
        repo = Repo.open(self.root)
        original = Repo.source_copy

        def mutant(instance, task_id):
            for other in instance.ticket_ids():
                instance._choose_source(other)
            return original(instance, task_id)

        with patch.object(Repo, "source_copy", mutant), self.assertRaises(AssertionError):
            self.check_unaffected(repo)

    def test_swallowed_errors(self):
        self.setup_malformed_branch()
        repo = Repo.open(self.root)
        original = Repo.source_copy

        def mutant(instance, task_id):
            try:
                return original(instance, task_id)
            except ChittyError:
                return None

        with patch.object(Repo, "source_copy", mutant), self.assertRaises(AssertionError):
            self.check_malformed_branch(repo)
        path = self.file(3)
        path.write_text(path.read_text().replace("\n---\n", "\n", 1))
        with patch.object(Repo, "source_copy", mutant), self.assertRaises(AssertionError):
            self.check_malformed_working(Repo.open(self.root))

    def test_ignore_changed_both(self):
        self.setup_changed_both()
        repo = Repo.open(self.root)
        original = ticket_source

        def mutant(task_id, provisional, current, main, tip, local, remote, contains, changed):
            return original(
                task_id,
                provisional,
                current,
                main,
                tip,
                local,
                remote,
                contains,
                lambda name: False,
            )

        with patch("chitty.store.ticket_source", mutant), self.assertRaises(AssertionError):
            self.check_branch_error(repo, "changed on both", "task-1", "main")
