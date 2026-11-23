import os
import string
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from chitty.config import CHITTY_VERSION
from chitty.ids import TaskId
from chitty.store import ChittyError, Edit, Repo
from tests import examples
from tests.support import RepoTestCase

SCAN_CONFIG = (
    "format = 1\n"
    'default_context = "tasks"\n'
    f'chitty_version = "{CHITTY_VERSION}"\n'
    "review = false\n"
    "autocommit = false\n"
    'check = "true"\n'
    "[contexts.tasks]\n"
    'prefix = "TASK"\n'
    "[contexts.backlog]\n"
    'prefix = "BACK"\n'
)
# One or two scans of each of the fixture's 4 context directories.
MIN_SCANS = 4
MAX_SCANS = 8
COUNT_SCANS = (
    "import chitty.store as store\n"
    "calls = []\n"
    "original = store.scan\n"
    "def counting(*args, **kwargs):\n"
    "    calls.append(1)\n"
    "    return original(*args, **kwargs)\n"
    "store.scan = counting\n"
)
LIST_SCRIPT = COUNT_SCANS + (
    "from chitty.cli import cli\n"
    "import io, contextlib\n"
    "with contextlib.redirect_stdout(io.StringIO()):\n"
    "    cli(['list'], standalone_mode=False)\n"
    "print(len(calls))\n"
)
LOOKUP_SCRIPT = COUNT_SCANS + (
    "from pathlib import Path\n"
    "from chitty.ids import TaskId\n"
    "repo = store.Repo.open(Path.cwd())\n"
    "for task_id in repo.ticket_ids():\n"
    "    repo.lookup(task_id)\n"
    "found = repo.lookup(TaskId('TASK', 2))\n"
    "print(len(calls))\n"
    "print(found.task.frontmatter.title)\n"
)
DIRECTORIES = ("backlog", "backlog/archive", "tasks", "tasks/archive")
PROPERTY_IDS = [TaskId("TASK", n) for n in range(1, 6)] + [TaskId("BACK", n) for n in range(1, 4)]


def ticket_text(title: str, status: str = "todo") -> str:
    return (
        f"---\ntitle: {title}\nstatus: {status}\npriority: medium\ncreated: 2026-11-23\n---\n"
        "\n## Description\n\nFixture.\n"
    )


def git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )


def write_ticket_dirs(root: Path) -> None:
    (root / "chitty.toml").write_text(SCAN_CONFIG)
    for name in ("tasks", "tasks/archive", "backlog"):
        (root / "chitty" / name).mkdir(parents=True, exist_ok=True)


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


class TestScanCounts(RepoTestCase):
    def test_list_scans_are_constant_in_ticket_count(self):
        counts = [self._scans(n, LIST_SCRIPT)[0] for n in (2, 20)]
        self.assertEqual(counts[0], counts[1])
        self.assertTrue(MIN_SCANS <= counts[0] <= MAX_SCANS, counts)

    def test_lookup_scans_are_constant_in_ticket_count(self):
        results = [self._scans(n, LOOKUP_SCRIPT) for n in (2, 20)]
        self.assertEqual(results[0][0], results[1][0])
        self.assertTrue(MIN_SCANS <= results[0][0] <= MAX_SCANS, results)
        self.assertEqual([title for _, title in results], ["Branch copy", "Branch copy"])

    def test_ref_files_with_unparseable_names_are_skipped(self):
        root, worktree = self._fixture(2)
        (worktree / "chitty/tasks/not-a-ticket.md").write_text("Not a ticket.\n")
        git(worktree, "add", ".")
        git(worktree, "commit", "-m", "stray file")
        repo = Repo.open(root)
        first = repo.lookup(TaskId("TASK", 1))
        second = repo.lookup(TaskId("TASK", 2))
        assert first is not None and second is not None
        self.assertEqual(first.task.frontmatter.title, "Ticket 1")
        self.assertEqual(second.task.frontmatter.title, "Branch copy")

    def _fixture(self, n: int) -> tuple[Path, Path]:
        root = self.tmp / f"scans-{n}"
        root.mkdir()
        write_ticket_dirs(root)
        for number in range(1, n + 1):
            (root / f"chitty/tasks/TASK-{number}--ticket.md").write_text(
                ticket_text(f"Ticket {number}")
            )
        (root / "chitty/tasks/archive/TASK-1000--old.md").write_text(ticket_text("Old", "done"))
        (root / "chitty/backlog/BACK-1--idea.md").write_text(ticket_text("Idea"))
        git(root, "init", "-b", "main")
        git(root, "add", ".")
        git(root, "commit", "-m", "setup")
        worktree = self.tmp / f"wt-task-2-{n}"
        git(root, "worktree", "add", "-b", "task-2", str(worktree), "main")
        path = worktree / "chitty/tasks/TASK-2--ticket.md"
        path.write_text(ticket_text("Branch copy"))
        git(worktree, "add", ".")
        git(worktree, "commit", "-m", "branch copy")
        return root, worktree

    def _scans(self, n: int, script: str) -> tuple[int, str | None]:
        root, _ = self._fixture(n)
        environment = os.environ.copy()
        environment["CHITTY_ACTOR"] = "test-agent"
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=root,
            env=environment,
            capture_output=True,
            text=True,
            check=True,
        )
        lines = result.stdout.splitlines()
        return int(lines[0]), (lines[1] if len(lines) > 1 else None)


class TestWorkingTreeIndex(RepoTestCase):
    def _root(self) -> Path:
        root = self.tmp / "plain"
        root.mkdir()
        write_ticket_dirs(root)
        (root / "chitty/tasks/TASK-1--one.md").write_text(ticket_text("One"))
        return root

    def test_invalid_active_entry_raises_for_any_lookup(self):
        root = self._root()
        (root / "chitty/tasks/not-a-ticket.md").write_text("x\n")
        with self.assertRaises(ChittyError) as raised:
            Repo.open(root).lookup(TaskId("TASK", 1))
        self.assertEqual(
            str(raised.exception),
            f"{root / 'chitty/tasks/not-a-ticket.md'}: invalid task ID 'not-a-ticket': "
            "expected PREFIX-N or PREFIX-SUFFIX, e.g. TASK-13",
        )

    def test_invalid_archived_entry_raises_for_any_lookup(self):
        root = self._root()
        (root / "chitty/backlog/archive").mkdir()
        (root / "chitty/backlog/archive/not-a-ticket.md").write_text("x\n")
        with self.assertRaises(ChittyError) as raised:
            Repo.open(root).lookup(TaskId("TASK", 1))
        self.assertEqual(
            str(raised.exception),
            f"{root / 'chitty/backlog/archive/not-a-ticket.md'}: invalid task ID "
            "'not-a-ticket': expected PREFIX-N or PREFIX-SUFFIX, e.g. TASK-13",
        )

    def test_duplicate_lists_active_then_archived(self):
        root = self._root()
        (root / "chitty/tasks/TASK-3--a.md").write_text(ticket_text("A"))
        (root / "chitty/tasks/archive/TASK-3--b.md").write_text(ticket_text("B"))
        with self.assertRaises(ChittyError) as raised:
            Repo.open(root).lookup(TaskId("TASK", 3))
        self.assertEqual(
            str(raised.exception),
            f"TASK-3 is used by more than one file: {root / 'chitty/tasks/TASK-3--a.md'}, "
            f"{root / 'chitty/tasks/archive/TASK-3--b.md'}",
        )

    def test_writes_clear_the_index(self):
        os.environ["CHITTY_ACTOR"] = "test-agent"
        root = self.tmp / "invalidate"
        root.mkdir()
        write_ticket_dirs(root)
        (root / "chitty/tasks/TASK-1--one.md").write_text(ticket_text("One", "done"))
        repo = Repo.open(root)
        task_id = TaskId("TASK", 1)
        self.assertIsNotNone(repo.lookup(task_id))
        repo.archive(task_id)
        archived = repo.lookup(task_id)
        assert archived is not None
        self.assertTrue(archived.archived)
        change = repo.add(repo.context("tasks"), "New", "Description.", [], {}, date(2026, 11, 23))
        self.assertIsNotNone(repo.lookup(change.task.id))

    @settings(max_examples=examples(100))
    @given(
        st.sets(
            st.tuples(
                st.sampled_from(PROPERTY_IDS),
                st.text(string.ascii_lowercase, min_size=1),
                st.sampled_from(DIRECTORIES),
            )
        )
    )
    def test_lookup_matches_the_files_on_disk(self, drawn):
        root = Path(tempfile.mkdtemp(dir=self.tmp))
        write_ticket_dirs(root)
        paths: dict[TaskId, set[Path]] = {}
        for task_id, slug, directory in drawn:
            name = f"{task_id}--{slug}"
            path = root / "chitty" / directory / f"{name}.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(ticket_text(name))
            paths.setdefault(task_id, set()).add(path)
        repo = Repo.open(root)
        for task_id in PROPERTY_IDS:
            found = sorted(
                paths.get(task_id, ()),
                key=lambda path: (
                    DIRECTORIES.index(str(path.parent.relative_to(root / "chitty"))),
                    path.name,
                ),
            )
            if not found:
                self.assertIsNone(repo.lookup(task_id))
            elif len(found) == 1:
                stored = repo.lookup(task_id)
                assert stored is not None
                self.assertEqual(stored.task.frontmatter.title, found[0].stem)
                expected_context = str(found[0].parent.relative_to(root / "chitty").parts[0])
                self.assertEqual(stored.context, expected_context)
            else:
                with self.assertRaises(ChittyError) as raised:
                    repo.lookup(task_id)
                self.assertEqual(
                    str(raised.exception),
                    f"{task_id} is used by more than one file: "
                    + ", ".join(str(path) for path in found),
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
