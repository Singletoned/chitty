import inspect
import subprocess
from contextlib import ExitStack
from functools import wraps
from unittest.mock import patch

from chitty import git
from chitty.errors import ChittyError
from chitty.ids import TaskId
from chitty.store import Repo
from tests.test_cli import CliTestCase


class TestTicketIds(CliTestCase):
    def setUp(self):
        super().setUp()
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace("autocommit = false", "autocommit = true"))

    def git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.root, check=True, capture_output=True, text=True
        ).stdout.strip()

    def init_git(self):
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.git("branch", "-M", "main")
        self.commit()

    def commit(self):
        self.git("add", "--all")
        self.git("commit", "--quiet", "--allow-empty", "-m", "fixture")

    def file(self, number):
        path = self.root / f"chitty/tasks/TASK-{number}--example.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("not parsed\n")
        return path

    def ids(self):
        return Repo.open(self.root).ticket_ids()

    def expected(self, *numbers):
        return {TaskId.parse(f"TASK-{number}") for number in numbers}

    def test_locations(self):
        self.init_git()
        self.file(1)
        old = self.file(6)
        self.file(7)
        self.commit()
        self.git("checkout", "-b", "task-5")
        self.file(5)
        self.file(9)
        self.commit()
        self.git("checkout", "main")
        self.git("checkout", "-b", "task-6")
        old.rename(old.with_name("TASK-6--renamed.md"))
        self.commit()
        self.git("checkout", "main")
        self.git("checkout", "-b", "task-7")
        self.file(7).unlink()
        self.commit()
        self.git("checkout", "main")
        self.git("checkout", "-b", "remote-fixture")
        self.file(4)
        self.commit()
        self.git("update-ref", "refs/remotes/origin/task-4", self.git("rev-parse", "HEAD"))
        self.git("checkout", "main")
        self.git("branch", "-D", "remote-fixture")
        self.git("checkout", "-b", "feature")
        self.file(8)
        self.commit()
        self.git("checkout", "main")
        self.file(2)
        self.assertEqual(self.ids(), self.expected(1, 2, 4, 5, 6, 7))

    def test_invalid_main_file(self):
        self.init_git()
        path = self.root / "chitty/tasks/notes.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("notes")
        self.commit()
        path.unlink()
        with self.assertRaisesRegex(ChittyError, r"main:chitty/tasks/notes\.md: "):
            self.ids()

    def test_invalid_working_file(self):
        path = self.root / "chitty/tasks/notes.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("notes")
        with self.assertRaises(ChittyError) as raised:
            self.ids()
        self.assertTrue(str(raised.exception).startswith(f"{path}: "))

    def test_invalid_other_branch_file_ignored(self):
        self.init_git()
        self.git("checkout", "-b", "task-5")
        self.file(5)
        (self.root / "chitty/tasks/notes.md").write_text("notes")
        self.commit()
        self.git("checkout", "main")
        self.assertEqual(self.ids(), self.expected(5))

    def test_missing_main(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace('main_branch = "main"', 'main_branch = "trunk"')
        )
        self.init_git()
        self.git("checkout", "-b", "task-5")
        self.file(5)
        self.commit()
        self.git("checkout", "main")
        self.file(2)
        self.assertEqual(self.ids(), self.expected(2, 5))

    def wrapped_git(self, stack):
        calls = []
        depth = 0

        def wrap(name, function):
            @wraps(function)
            def record(*args, **kwargs):
                nonlocal depth
                if depth == 0:
                    calls.append((name, args, kwargs))
                depth += 1
                try:
                    return function(*args, **kwargs)
                finally:
                    depth -= 1

            return record

        for name, value in inspect.getmembers(git, inspect.isfunction):
            if value.__module__ == git.__name__:
                stack.enter_context(patch.object(git, name, wrap(name, value)))
        return calls

    def test_no_git_repository(self):
        self.file(1)
        repo = Repo.open(self.root)
        with ExitStack() as stack:
            calls = self.wrapped_git(stack)
            self.assertEqual(repo.ticket_ids(), self.expected(1))
        self.assertEqual([name for name, _, _ in calls], ["is_repository"])

    def test_ref_reads_once_and_cached(self):
        self.init_git()
        for number in (1, 2):
            self.git("checkout", "-b", f"task-{number}", "main")
            self.file(number)
            self.commit()
        self.git("checkout", "main")
        repo = Repo.open(self.root)
        with ExitStack() as stack:
            calls = self.wrapped_git(stack)
            self.assertEqual(repo.ticket_ids(), self.expected(1, 2))
            self.assertEqual(repo.ticket_ids(), self.expected(1, 2))
            self.assertCountEqual(
                [args[1] for name, args, _ in calls if name == "files_at"],
                [self.git("rev-parse", ref) for ref in ("main", "task-1", "task-2")],
            )
            self.assertFalse(any(name == "file_at" for name, _, _ in calls))
