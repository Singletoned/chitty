import json
import subprocess
from contextlib import chdir
from pathlib import Path
from unittest.mock import patch

from chitty import locks, mcp
from chitty.ids import TaskId
from chitty.store import Repo
from tests.test_cli import CliTestCase


class TestPlanningWorktrees(CliTestCase):
    def git(self, *args: str, cwd: Path | None = None) -> str:
        return subprocess.run(
            ["git", *args], cwd=cwd or self.root, capture_output=True, text=True, check=True
        ).stdout.strip()

    def setUp(self):
        super().setUp()
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace("autocommit = false", "autocommit = true"))
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.com")
        self.run_cli("init")
        self.commit()
        self.path = Path(self.json("add", "First", "-d", "Initial body.")["path"])
        self.other = Path(self.json("add", "Second", "-d", "Other body.")["path"])
        self.plan = self.tmp / "plan"
        self.git("worktree", "add", "-b", "plan/one", str(self.plan))
        self.addCleanup(self.git, "worktree", "remove", "--force", str(self.plan))

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "-qm", "fixture")

    def test_isolated_edit_and_show(self):
        head = self.git("rev-parse", "HEAD")
        before = self.path.read_bytes()
        with chdir(self.plan):
            self.run_cli("edit", "TASK-1", "--title", "Draft title")
            self.assertIn("title: Draft title", self.run_cli("show", "TASK-1").stdout)
            draft = self.json("show", "TASK-1")
            self.assertEqual(draft["title"], "Draft title")
            self.assertEqual(Path(draft["path"]), self.plan / "chitty/tasks/TASK-1--draft-title.md")
        self.assertEqual(self.git("rev-parse", "HEAD^", cwd=self.plan), head)
        self.assertEqual(self.git("rev-parse", "HEAD"), head)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(self.json("show", "TASK-1")["title"], "First")
        stored = Repo.open(self.root).lookup(TaskId.parse("TASK-1"))
        assert stored is not None
        self.assertEqual(stored.path, self.path)
        self.assertEqual(stored.task.frontmatter.title, "First")

    def test_cli_one_ticket_commands_on_branches(self):
        for branch in ("plan/one", "hotfix/x"):
            with self.subTest(branch=branch):
                worktree = self.plan if branch == "plan/one" else self.tmp / "hotfix"
                if branch != "plan/one":
                    self.git("worktree", "add", "-b", branch, str(worktree), "main")
                    self.addCleanup(self.git, "worktree", "remove", "--force", str(worktree))
                head = self.git("rev-parse", "main")
                before = self.path.read_bytes()
                with chdir(worktree):
                    self.run_cli("note", "TASK-1", "Branch note")
                    self.run_cli("edit", "TASK-1", "--title", "Branch title")
                    self.run_cli("archive", "TASK-1")
                self.assertEqual(self.git("rev-list", "--count", "main..HEAD", cwd=worktree), "3")
                self.assertEqual(self.git("rev-parse", "main"), head)
                self.assertEqual(self.path.read_bytes(), before)
                self.assertTrue(
                    (worktree / "chitty/tasks/archive/TASK-1--branch-title.md").exists()
                )
                if branch == "plan/one":
                    self.git("reset", "--hard", "main", cwd=worktree)

    def test_mcp_one_ticket_commands_on_hotfix(self):
        worktree = self.tmp / "hotfix"
        self.git("worktree", "add", "-b", "hotfix/x", str(worktree), "main")
        self.addCleanup(self.git, "worktree", "remove", "--force", str(worktree))
        head = self.git("rev-parse", "main")
        before = self.path.read_bytes()
        with chdir(worktree):
            mcp.edit("TASK-1", title="Branch title")
            self.assertEqual(mcp.show("TASK-1")["title"], "Branch title")
            mcp.note("TASK-1", "Branch note")
            mcp.archive("TASK-1")
        self.assertEqual(self.git("rev-list", "--count", "main..HEAD", cwd=worktree), "3")
        self.assertEqual(self.git("rev-parse", "main"), head)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertTrue((worktree / "chitty/tasks/archive/TASK-1--branch-title.md").exists())

    def test_branch_selection(self):
        repo = Repo.open(self.root)
        for branch, expected in (("main", None), ("task-1", None), ("hotfix/x", "hotfix/x")):
            with (
                self.subTest(branch=branch),
                patch.object(repo, "_current_branch", return_value=branch),
            ):
                self.assertEqual(repo.planning_branch(), expected)

    def test_archive_requires_local_copy_and_move(self):
        with chdir(self.plan):
            local = self.plan / self.path.relative_to(self.root)
            local.unlink()
            result = self.run_cli("archive", "TASK-1", exit_code=1)
            self.assertIn("no local draft", result.stderr)
            self.git("restore", str(local), cwd=self.plan)
            config = self.plan / "chitty.toml"
            config.write_text(config.read_text().replace('archive = "move"', 'archive = "delete"'))
            result = self.run_cli("archive", "TASK-1", exit_code=1)
            self.assertIn('archiving on a branch needs archive = "move"', result.stderr)
            self.assertTrue(local.exists())

    def snapshot(self):
        git_dir = Path(self.git("rev-parse", "--absolute-git-dir", cwd=self.plan))
        return (
            self.git("rev-parse", "HEAD", cwd=self.plan),
            (git_dir / "index").read_bytes(),
            {path: path.read_bytes() for path in (self.plan / "chitty").rglob("*.md")},
        )

    def assert_conflict(self, ref: str):
        before = self.snapshot()
        with chdir(self.plan):
            result = self.run_cli("edit", "TASK-1", "--note", "Draft", exit_code=1)
        self.assertIn(f"planning edit for TASK-1 conflicts with {ref}", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_main_conflict(self):
        self.path.write_text(self.path.read_text().replace("Initial body.", "Main changed."))
        self.commit()
        self.assert_conflict("refs/heads/main")

    def test_sibling_rename_conflict(self):
        self.git("switch", "-c", "plan/two")
        renamed = self.path.with_name("TASK-1--renamed.md")
        renamed.write_text(self.path.read_text().replace("title: First", "title: Renamed"))
        self.path.unlink()
        self.commit()
        self.git("switch", "main")
        self.assert_conflict("refs/heads/plan/two")

    def test_ticket_deletion_conflict(self):
        self.git("switch", "-c", "task-1")
        self.path.unlink()
        self.commit()
        self.git("switch", "main")
        self.assert_conflict("refs/heads/task-1")

    def test_remote_only_conflict_and_negative_control(self):
        self.git("switch", "-c", "feature")
        self.path.write_text(self.path.read_text().replace("Initial body.", "Remote changed."))
        self.commit()
        self.git("update-ref", "refs/remotes/origin/feature", "HEAD")
        self.git("switch", "main")
        self.git("branch", "-D", "feature")
        ref = "refs/remotes/origin/feature"
        self.assert_conflict(ref)
        with (
            patch.object(Repo, "_reject_planning_conflicts", return_value=None),
            self.assertRaisesRegex(AssertionError, "0 != 1"),
        ):
            self.assert_conflict(ref)

    def test_no_local_copy_refuses_edit_but_show_falls_back(self):
        (self.plan / self.path.relative_to(self.root)).unlink()
        before = self.snapshot()
        with chdir(self.plan):
            failed = self.run_cli("edit", "TASK-1", "--note", "Not local", exit_code=1)
            self.assertIn(f"no local draft for TASK-1 in {self.plan / 'chitty'}", failed.stderr)
            self.assertEqual(self.json("show", "TASK-1")["title"], "First")
        self.assertEqual(self.snapshot(), before)

    def test_idle_branch_and_live_runner_lock(self):
        self.git("branch", "task-1")
        self.git("switch", "-c", "plan/two")
        self.other.write_text(self.other.read_text().replace("Other body.", "Sibling changed."))
        self.commit()
        self.git("switch", "main")
        with chdir(self.plan):
            idle = self.run_cli("edit", "TASK-1", "--note", "Before lock")
            with locks.run_lock(self.root, "TASK-1", actor="other-worker", mode="work"):
                held = self.run_cli("edit", "TASK-1", "--note", "During lock", "--json")
            released = self.run_cli("edit", "TASK-1", "--note", "After lock")
            self.assertEqual(json.loads(held.stdout)["id"], "TASK-1")
        self.assertNotIn("coordinate", idle.stderr)
        self.assertIn("coordinate", held.stderr)
        self.assertIn("TASK-1", held.stderr)
        self.assertNotIn("coordinate", released.stderr)
        self.assertEqual(self.git("rev-list", "--count", "main..HEAD", cwd=self.plan), "3")
