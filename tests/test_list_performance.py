import os
import subprocess
import sys
import unittest
from datetime import date

from chitty.config import CHITTY_VERSION
from chitty.store import Edit, Repo
from tests.support import RepoTestCase


class TestListPerformance(RepoTestCase):
    def test_list_git_trace_is_constant_in_task_count(self):
        counts = [self._list_git_calls(task_count) for task_count in (2, 10)]
        self.assertEqual(counts[0], counts[1])

    def test_lookup_git_trace_is_constant_in_task_count(self):
        counts = [self._lookup_git_calls(count) for count in (2, 10)]
        self.assertEqual(counts[0], counts[1])

    def _lookup_git_calls(self, task_count: int) -> int:
        root = self.tmp / f"lookup-{task_count}"
        root.mkdir()
        (root / "chitty.toml").write_text((self.root / "chitty.toml").read_text())
        tasks = root / "chitty" / "tasks"
        tasks.mkdir(parents=True)
        for number in range(1, task_count + 1):
            (tasks / f"TASK-{number}--task.md").write_text(self._task("Task", "todo", []))
        self._git(root, "init", "-b", "main")
        self._git(root, "add", ".")
        self._git(
            root,
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            "commit",
            "-m",
            "setup",
        )
        trace = root / "git-trace.log"
        environment = os.environ.copy()
        environment["GIT_TRACE"] = str(trace)
        script = (
            "from pathlib import Path; from chitty.store import Repo; "
            "repo = Repo.open(Path.cwd()); ids = repo.ticket_ids(); "
            "found = [repo.lookup(task_id) for task_id in ids]; "
            "print(len(ids), sum(item is not None for item in found))"
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=root,
            env=environment,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(result.stdout.strip(), f"{task_count} {task_count}")
        return sum("trace: built-in: git" in line for line in trace.read_text().splitlines())

    def _list_git_calls(self, task_count: int) -> int:
        root = self.tmp / f"repo-{task_count}"
        root.mkdir()
        (root / "chitty.toml").write_text(
            "format = 1\n"
            'default_context = "tasks"\n'
            f'chitty_version = "{CHITTY_VERSION}"\n'
            "review = false\n"
            "autocommit = false\n"
            'check = "true"\n'
            "[contexts.tasks]\n"
            'prefix = "TASK"\n'
        )
        tasks = root / "chitty" / "tasks"
        tasks.mkdir(parents=True)
        (tasks / "TASK-1--done.md").write_text(self._task("Done", "done", []))
        for number in range(2, task_count + 2):
            status = "planning" if number % 2 == 0 else "todo"
            (tasks / f"TASK-{number}--{status}.md").write_text(
                self._task(f"Dependent {number}", status, ["TASK-1", "TASK-1000"])
            )
        (tasks / "TASK-1000--planning.md").write_text(self._task("Blocker", "planning", []))
        self._git(root, "init", "-b", "main")
        self._git(root, "add", ".")
        self._git(
            root,
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            "commit",
            "-m",
            "setup",
        )
        trace = root / "git-trace.log"
        environment = os.environ.copy()
        environment.update(CHITTY_ACTOR="test-agent", GIT_TRACE=str(trace))
        result = subprocess.run(
            [sys.executable, "-c", "from chitty.cli import main; main()", "list"],
            cwd=root,
            env=environment,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(result.stderr, "")
        self.assertIn(
            "🚧", next(line for line in result.stdout.splitlines() if "TASK-1000" in line)
        )
        return sum("trace: built-in: git" in line for line in trace.read_text().splitlines())

    @staticmethod
    def _git(root, *args: str) -> None:
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)

    @staticmethod
    def _task(title: str, status: str, dependencies: list[str]) -> str:
        depends = f"depends_on: [{', '.join(dependencies)}]\n" if dependencies else ""
        return (
            f"---\ntitle: {title}\nstatus: {status}\n{depends}created: 2026-11-08\n---\n"
            "\n## Description\n\nDescription.\n"
        )


class TestRepoCacheInvalidation(RepoTestCase):
    def test_source_metadata_is_refreshed_after_git_changes(self):
        def git(*args):
            return TestListPerformance._git(self.root, *args)

        tasks = self.root / "chitty" / "tasks"
        tasks.mkdir(parents=True)
        path = tasks / "TASK-1--task.md"
        path.write_text(TestListPerformance._task("Baseline", "todo", []))
        git("init", "-b", "main")
        git("add", ".")
        git("-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-m", "base")
        repo = Repo.open(self.root)
        task_id = repo.resolve("TASK-1")
        baseline = repo.lookup(task_id)
        assert baseline is not None
        self.assertEqual((baseline.task.frontmatter.title, baseline.branch), ("Baseline", None))

        git("switch", "-c", "task-1")
        path.write_text(TestListPerformance._task("Branch title", "todo", []))
        git("add", ".")
        git("-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-m", "edit")
        git("switch", "main")
        repo._invalidate()
        branch = repo.lookup(task_id)
        assert branch is not None
        self.assertEqual((branch.task.frontmatter.title, branch.branch), ("Branch title", "task-1"))

        git("merge", "--ff-only", "task-1")
        repo._invalidate()
        merged = repo.lookup(task_id)
        assert merged is not None
        self.assertEqual((merged.task.frontmatter.title, merged.branch), ("Branch title", None))

    def test_tasks_and_find_see_an_edit_on_the_same_repo(self):
        os.environ["CHITTY_ACTOR"] = "test-agent"
        repo = Repo.open(self.root)
        context = repo.context("tasks")
        change = repo.add(context, "A task", "Description.", [], {}, date(2026, 11, 8))
        task_id = change.task.id
        self.assertEqual(repo.find(task_id).task.frontmatter.status, "todo")

        repo.edit(task_id, Edit(status="doing"))

        self.assertEqual(repo.find(task_id).task.frontmatter.status, "doing")
        self.assertEqual(repo.tasks(context, "active")[0].task.frontmatter.status, "doing")


if __name__ == "__main__":
    unittest.main()
