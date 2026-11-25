import os
import subprocess
from contextlib import ExitStack
from pathlib import Path

from chitty.ids import TaskId
from chitty.store import Repo
from tests import test_ticket_ids
from tests.test_cli import CliTestCase


class TestSourceCopy(CliTestCase):
    git = test_ticket_ids.TestTicketIds.git
    init_git = test_ticket_ids.TestTicketIds.init_git
    commit = test_ticket_ids.TestTicketIds.commit
    wrapped_git = test_ticket_ids.TestTicketIds.wrapped_git

    def file(self, number, title="original"):
        path = self.root / f"chitty/tasks/TASK-{number}--example.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\ntitle: {title}\nstatus: todo\ncreated: 2026-01-01\n---\n"
            "\n## Description\n\nFixture.\n"
        )
        return path

    def commit_at(self, date):
        self.git("add", "--all")
        subprocess.run(
            ["git", "commit", "--quiet", "--allow-empty", "-m", "fixture"],
            cwd=self.root,
            env={**os.environ, "GIT_COMMITTER_DATE": date},
            check=True,
            capture_output=True,
        )

    def source(self, number, repo=None):
        return (repo or Repo.open(self.root)).source_copy(TaskId.parse(f"TASK-{number}"))

    def assert_copy(self, copy, ref, path, title):
        self.assertIsNotNone(copy)
        self.assertEqual(
            (copy.ref, copy.path, copy.task.frontmatter.title), (ref, Path(path), title)
        )

    def base(self):
        self.init_git()
        self.file(1)
        self.commit()

    def branch_edit(self):
        self.git("checkout", "-b", "task-1")
        self.file(1, "branch")
        self.commit_at("2020-01-01T00:00:00Z")

    def test_provisional_in_linked_worktree(self):
        self.init_git()
        worktree = self.root / "linked"
        self.git("worktree", "add", "-b", "task-5", str(worktree))
        previous = Path.cwd()
        try:
            os.chdir(worktree)
            self.run_cli("add", "provisional fixture", "-d", "Fixture.")
        finally:
            os.chdir(previous)
        path = next((worktree / "chitty/tasks").glob("TASK-*--*.md"))
        task_id = TaskId.parse(path.name.split("--")[0])
        repo = Repo.open(worktree)
        for committed in (False, True):
            with self.subTest(committed=committed):
                copy = repo.source_copy(task_id)
                assert copy is not None
                self.assertIsNone(copy.ref)
                self.assertEqual(copy.path, path.relative_to(worktree))
                self.assertEqual(copy.task.frontmatter.title, "provisional fixture")
                self.assertIs(copy.task.frontmatter.provisional, True)
            if not committed:
                subprocess.run(["git", "add", "--all"], cwd=worktree, check=True)
                subprocess.run(["git", "commit", "-qm", "fixture"], cwd=worktree, check=True)
                repo = Repo.open(worktree)

    def test_provisional_is_read_from_the_id(self):
        self.init_git()
        for number in ("K7Q2MA", "K7Q2MC", 4):
            path = self.file(number)
            path.write_text(
                path.read_text().replace("status: todo", "provisional: true\nstatus: todo")
            )
        self.file(2)
        self.commit()
        self.git("checkout", "-b", "feature")
        (self.root / "chitty/tasks/TASK-K7Q2MA--example.md").unlink()
        (self.root / "chitty/tasks/TASK-2--example.md").unlink()
        (self.root / "chitty/tasks/TASK-4--example.md").unlink()
        self.file("K7Q2MC", "working")
        self.assertIsNone(self.source("K7Q2MA"))
        self.assert_copy(self.source(2), "main", "chitty/tasks/TASK-2--example.md", "original")
        self.assert_copy(
            self.source("K7Q2MC"), None, "chitty/tasks/TASK-K7Q2MC--example.md", "working"
        )
        self.assert_copy(self.source(4), "main", "chitty/tasks/TASK-4--example.md", "original")

    def test_malformed_working_tree_on_another_branch_is_not_read(self):
        self.base()
        self.git("checkout", "-b", "feature")
        path = self.root / "chitty/tasks/TASK-1--example.md"
        path.write_text(path.read_text().replace("\n---\n", "\n", 1))
        self.assert_copy(self.source(1), "main", "chitty/tasks/TASK-1--example.md", "original")

    def test_malformed_working_tree_does_not_stop_a_branch_copy(self):
        self.base()
        self.git("checkout", "-b", "task-1")
        self.file(1, "branch")
        self.commit()
        self.git("checkout", "main")
        (self.root / "chitty/tasks/TASK-1--example.md").write_text("not frontmatter\n")
        self.assert_copy(self.source(1), "task-1", "chitty/tasks/TASK-1--example.md", "branch")

    def test_provisional_on_main_with_its_own_branch_ahead_is_read_from_it(self):
        self.init_git()
        path = self.file("K7Q2MY")
        path.write_text(path.read_text().replace("status: todo", "provisional: true\nstatus: todo"))
        self.commit()
        self.git("checkout", "-b", "task-k7q2my")
        path = self.file("K7Q2MY", "branch")
        path.write_text(path.read_text().replace("status: todo", "provisional: true\nstatus: todo"))
        self.commit()
        self.git("checkout", "main")
        self.assert_copy(
            self.source("K7Q2MY"), "task-k7q2my", "chitty/tasks/TASK-K7Q2MY--example.md", "branch"
        )
        self.git("merge", "--ff-only", "task-k7q2my")
        self.assert_copy(
            self.source("K7Q2MY"), None, "chitty/tasks/TASK-K7Q2MY--example.md", "branch"
        )

    def test_provisional_only_on_its_branch_is_read_from_it(self):
        self.init_git()
        self.git("checkout", "-b", "task-k7q2mx")
        path = self.file("K7Q2MX")
        path.write_text(path.read_text().replace("status: todo", "provisional: true\nstatus: todo"))
        self.commit()
        self.git("checkout", "main")
        self.assert_copy(
            self.source("K7Q2MX"), "task-k7q2mx", "chitty/tasks/TASK-K7Q2MX--example.md", "original"
        )

    def test_branch_ahead_despite_later_main_date(self):
        self.base()
        self.branch_edit()
        self.git("checkout", "main")
        self.file(2)
        self.commit_at("2030-01-01T00:00:00Z")
        self.assert_copy(self.source(1), "task-1", "chitty/tasks/TASK-1--example.md", "branch")

    def test_renamed(self):
        self.base()
        self.git("checkout", "-b", "task-1")
        self.file(1, "renamed").rename(self.root / "chitty/tasks/TASK-1--renamed.md")
        self.commit()
        self.git("checkout", "main")
        self.assert_copy(self.source(1), "task-1", "chitty/tasks/TASK-1--renamed.md", "renamed")

    def test_remote_only(self):
        self.base()
        self.branch_edit()
        self.git("update-ref", "refs/remotes/origin/task-1", self.git("rev-parse", "HEAD"))
        self.git("checkout", "main")
        self.git("branch", "-D", "task-1")
        self.assert_copy(
            self.source(1), "origin/task-1", "chitty/tasks/TASK-1--example.md", "branch"
        )

    def test_remote_ahead_of_local(self):
        self.base()
        self.branch_edit()
        self.file(1, "remote")
        self.commit()
        self.git("update-ref", "refs/remotes/origin/task-1", self.git("rev-parse", "HEAD"))
        self.git("reset", "--hard", "HEAD~1")
        self.git("checkout", "main")
        self.assert_copy(
            self.source(1), "origin/task-1", "chitty/tasks/TASK-1--example.md", "remote"
        )

    def test_uncommitted_edit(self):
        self.base()
        self.file(1, "dirty")
        self.assert_copy(self.source(1), None, "chitty/tasks/TASK-1--example.md", "dirty")

    def test_archived(self):
        self.base()
        self.git("checkout", "-b", "task-1")
        archive = self.root / "chitty/tasks/archive/TASK-1--example.md"
        archive.parent.mkdir()
        self.file(1, "archived").rename(archive)
        self.commit()
        self.git("checkout", "main")
        self.assert_copy(
            self.source(1), "task-1", "chitty/tasks/archive/TASK-1--example.md", "archived"
        )

    def test_branch_deletes(self):
        self.base()
        self.git("checkout", "-b", "task-1")
        self.file(1).unlink()
        self.commit()
        self.git("checkout", "main")
        self.assertIsNone(self.source(1))

    def test_merged_then_main_changed(self):
        self.base()
        self.branch_edit()
        self.git("checkout", "main")
        self.git("merge", "--ff-only", "task-1")
        self.file(1, "main")
        self.commit()
        self.assert_copy(self.source(1), None, "chitty/tasks/TASK-1--example.md", "main")

    def test_no_further_ref_reads(self):
        self.init_git()
        for number in (1, 2):
            self.file(number)
        self.commit()
        for number in (1, 2):
            self.git("checkout", "-b", f"task-{number}", "main")
            self.file(number, f"branch{number}")
            self.commit()
        self.git("checkout", "main")
        repo = Repo.open(self.root)
        repo.ticket_ids()
        with ExitStack() as stack:
            calls = self.wrapped_git(stack)
            for number in (1, 2):
                self.assert_copy(
                    self.source(number, repo),
                    f"task-{number}",
                    f"chitty/tasks/TASK-{number}--example.md",
                    f"branch{number}",
                )
        self.assertFalse(any(name in {"files_at", "file_at"} for name, _, _ in calls))

    def test_invalidation(self):
        self.base()
        self.branch_edit()
        self.git("checkout", "main")
        repo = Repo.open(self.root)
        first = self.source(1, repo)
        self.assertEqual(first, self.source(1, repo))
        self.git("checkout", "task-1")
        self.file(1, "new")
        self.commit()
        self.git("checkout", "main")
        repo._invalidate()
        self.assert_copy(self.source(1, repo), "task-1", "chitty/tasks/TASK-1--example.md", "new")

    def test_uncommitted_deletion(self):
        self.base()
        self.file(1).unlink()
        self.assertIsNone(self.source(1))
