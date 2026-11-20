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
