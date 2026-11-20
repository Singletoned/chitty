import subprocess
from contextlib import ExitStack
from unittest.mock import patch

from chitty import store
from chitty.errors import ChittyError
from chitty.ids import TaskId
from chitty.store import Repo
from chitty.ticket_source import WORKING_TREE
from tests import test_source_copy
from tests.test_cli import CliTestCase


class TestSourceCopyCheckouts(CliTestCase):
    git = test_source_copy.TestSourceCopy.git
    init_git = test_source_copy.TestSourceCopy.init_git
    commit = test_source_copy.TestSourceCopy.commit
    wrapped_git = test_source_copy.TestSourceCopy.wrapped_git
    file = test_source_copy.TestSourceCopy.file

    def check_copy(self, root, number, ref, title):
        copy = Repo.open(root).source_copy(TaskId.parse(f"TASK-{number}"))
        assert copy is not None
        self.assertEqual((copy.ref, copy.task.frontmatter.title), (ref, title))

    def checkout_fixture(self):
        self.init_git()
        self.file(5, "main")
        self.file(7, "main")
        self.commit()
        self.git("worktree", "add", ".worktrees/task-5", "-b", "task-5")
        worktree = self.root / ".worktrees/task-5"
        task5 = worktree / "chitty/tasks/TASK-5--example.md"
        task7 = worktree / "chitty/tasks/TASK-7--example.md"
        task5.write_text(task5.read_text().replace("title: main", "title: branch"))
        subprocess.run(["git", "add", str(task5)], cwd=worktree, check=True)
        subprocess.run(["git", "commit", "--quiet", "-m", "branch"], cwd=worktree, check=True)
        task5.write_text(task5.read_text().replace("title: branch", "title: dirty"))
        task7.write_text(task7.read_text().replace("title: main", "title: dirty"))
        self.git("checkout", "-b", "feature")
        self.file(7, "dirty")
        return worktree

    def check_task5(self, worktree):
        self.check_copy(worktree, 5, None, "dirty")

    def check_task7_worktree(self, worktree):
        self.check_copy(worktree, 7, "main", "main")

    def check_task7_feature(self):
        self.check_copy(self.root, 7, "main", "main")

    def check_outside_git(self):
        repo = Repo.open(self.root)
        with ExitStack() as stack:
            calls = self.wrapped_git(stack)
            copy = repo.source_copy(TaskId.parse("TASK-5"))
        assert copy is not None
        self.assertEqual((copy.ref, copy.task.frontmatter.title), (None, "dirty"))
        self.assertEqual([name for name, _, _ in calls], ["is_repository"])

    def test_linked_worktree_and_feature(self):
        worktree = self.checkout_fixture()
        self.check_task5(worktree)
        self.check_task7_worktree(worktree)
        self.check_task7_feature()

    def test_outside_git(self):
        self.file(5, "dirty")
        self.check_outside_git()

    def test_mutant_always_uses_working_tree(self):
        worktree = self.checkout_fixture()
        real = store.ticket_source

        def mutant(*args, **kwargs):
            real(*args, **kwargs)
            return WORKING_TREE

        with patch("chitty.store.ticket_source", mutant):
            with self.assertRaises(AssertionError):
                self.check_task7_worktree(worktree)
            with self.assertRaises(AssertionError):
                self.check_task7_feature()

    def test_mutant_ignores_current_branch(self):
        worktree = self.checkout_fixture()
        real = store.ticket_source

        def mutant(task_id, provisional, current_branch, *args):
            return real(task_id, provisional, None, *args)

        with patch("chitty.store.ticket_source", mutant), self.assertRaises(AssertionError):
            self.check_task5(worktree)

    def test_mutant_treats_non_git_as_repository(self):
        self.file(5, "dirty")
        with (
            patch("chitty.store.git.is_repository", return_value=True),
            self.assertRaisesRegex(ChittyError, "refs/heads/main"),
        ):
            self.check_outside_git()
