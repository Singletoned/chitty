import os
import subprocess
from pathlib import Path
from unittest import mock

from tests.test_cli import CliTestCase


class TestProvisionalIds(CliTestCase):
    def setUp(self):
        super().setUp()
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.com")
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "init")
        config = (self.root / "chitty.toml").read_text()
        (self.root / "chitty.toml").write_text(
            config + '\n[contexts.backlog]\nprefix = "BACKLOG"\nrandom_ids = true\n'
        )

    def git(self, *args: str, cwd: Path | None = None):
        return subprocess.run(
            ["git", *args], cwd=cwd or self.root, check=True, capture_output=True, text=True
        ).stdout.strip()

    def test_add_on_main_is_sequential_and_feature_is_provisional(self):
        main = self.json("add", "Main ticket", "-d", "Description.")
        self.assertEqual(main["id"], "TASK-1")
        self.assertIsNone(main["provisional"])
        self.assertNotIn(
            "provisional:", (self.root / "chitty/tasks/TASK-1--main-ticket.md").read_text()
        )
        self.git("switch", "-c", "feature")
        branch = self.json("add", "Branch ticket", "-d", "Description.")
        self.assertRegex(branch["id"], r"^TASK-[A-Z0-9]*[A-Z][A-Z0-9]*$")
        self.assertTrue(branch["provisional"])

    def test_main_checkout_switched_to_feature_and_detached_head_are_provisional(self):
        self.git("switch", "-c", "feature")
        switched = self.json("add", "Switched", "-d", "Description.")
        self.assertRegex(switched["id"], r"^TASK-[A-Z0-9]*[A-Z][A-Z0-9]*$")
        self.assertTrue(switched["provisional"])
        self.git("checkout", "--detach")
        detached = self.json("add", "Detached", "-d", "Description.")
        self.assertRegex(detached["id"], r"^TASK-[A-Z0-9]*[A-Z][A-Z0-9]*$")
        self.assertTrue(detached["provisional"])

    def test_linked_worktree_uses_default_context_with_provisional_id(self):
        worktree = self.tmp / "feature-worktree"
        self.git("worktree", "add", "--quiet", "-b", "feature", str(worktree))
        self.addCleanup(
            subprocess.run,
            ["git", "-C", str(self.root), "worktree", "remove", "--force", str(worktree)],
            check=True,
        )
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        result = subprocess.run(
            ["git", "-C", str(worktree), "status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.stdout, "")
        previous = Path.cwd()
        try:
            os.chdir(worktree)
            ticket = self.json("add", "Linked", "-d", "Description.")
        finally:
            os.chdir(previous)
        self.assertRegex(ticket["id"], r"^TASK-[A-Z0-9]*[A-Z][A-Z0-9]*$")
        self.assertTrue(ticket["provisional"])

    def test_outside_git_keeps_sequential_ids(self):
        outside = self.tmp / "outside"
        outside.mkdir()
        (outside / "chitty.toml").write_text((self.root / "chitty.toml").read_text())
        previous = Path.cwd()
        try:
            os.chdir(outside)
            ticket = self.json("add", "Outside", "-d", "Description.")
        finally:
            os.chdir(previous)
        self.assertEqual(ticket["id"], "TASK-1")
        self.assertIsNone(ticket["provisional"])
        self.assertNotIn("provisional:", (outside / "chitty/tasks/TASK-1--outside.md").read_text())

    def test_move_provisional_off_main_then_promote_on_main(self):
        self.json("add", "Source", "-d", "Description.")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "source")
        worktree = self.tmp / "feature-worktree"
        self.git("worktree", "add", "--quiet", "-b", "feature", str(worktree))
        self.addCleanup(
            subprocess.run,
            ["git", "-C", str(self.root), "worktree", "remove", "--force", str(worktree)],
            check=True,
        )
        previous = Path.cwd()
        try:
            os.chdir(worktree)
            refused = self.run_cli("move", "TASK-1", "human", exit_code=1)
            self.assertIn("latest committed version is on branch main", refused.stderr)
            with mock.patch("chitty.store._provisional_draw", return_value=0):
                created = self.json("add", "Branch", "-d", "Description.")
                self.assertEqual(created["id"], "TASK-AAAAAA")
                moved = self.json("move", "TASK-AAAAAA", "human")
            self.assertEqual(moved["id"], "HUMAN-AAAAAA")
            self.assertTrue(moved["provisional"])
            self.git("add", "--all", cwd=worktree)
            self.git("commit", "--quiet", "-m", "move", cwd=worktree)
        finally:
            os.chdir(previous)
        self.git("merge", "--quiet", "feature")
        promoted = self.json("move", "HUMAN-AAAAAA", "tasks")
        self.assertEqual(promoted["id"], "TASK-2")
        self.assertIsNone(promoted["provisional"])

    def test_renumber_provisional_duplicate_on_main_clears_marker(self):
        self.git("switch", "-c", "feature")
        with mock.patch("chitty.store._provisional_draw", return_value=0):
            provisional = self.json("add", "Provisional", "-d", "Description.")
        self.assertTrue(provisional["provisional"])
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "provisional")
        self.git("switch", "main")
        self.git("merge", "--quiet", "feature")
        original = self.root / "chitty/tasks/TASK-AAAAAA--provisional.md"
        duplicate = self.root / "chitty/tasks/TASK-AAAAAA--duplicate.md"
        duplicate.write_text(original.read_text())
        result = self.run_cli("renumber", "chitty/tasks/TASK-AAAAAA--duplicate.md")
        self.assertIn("TASK-1", result.stdout)
        self.assertNotIn(
            "provisional:", (self.root / "chitty/tasks/TASK-1--duplicate.md").read_text()
        )

    def test_origin_main_ref_allows_provisional_ids_without_local_main(self):
        self.git("switch", "-c", "feature")
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")
        self.git("branch", "-D", "main")
        ticket = self.json("add", "Single branch", "-d", "Description.")
        self.assertTrue(ticket["provisional"])

    def test_random_context_stays_numeric_off_main(self):
        self.git("switch", "-c", "feature")
        ticket = self.json("add", "Backlog ticket", "-c", "backlog")
        self.assertTrue(ticket["id"].startswith("BACKLOG-"))
        self.assertTrue(ticket["id"].split("-")[1].isdigit())
        self.assertIsNone(ticket["provisional"])

    def test_collision_retries_and_exhaustion(self):
        self.git("switch", "-c", "feature")
        with mock.patch("chitty.store._provisional_draw", return_value=0):
            first = self.json("add", "Existing", "-d", "Description.")
        self.assertEqual(first["id"], "TASK-AAAAAA")
        with mock.patch("chitty.store._provisional_draw", side_effect=[0] * 6 + [1] * 6):
            second = self.json("add", "Next", "-d", "Description.")
        self.assertEqual(second["id"], "TASK-BBBBBB")
        with mock.patch("chitty.store._provisional_draw", return_value=0):
            failed = self.run_cli("add", "Exhausted", "-d", "Description.", exit_code=1)
        self.assertIn("no unused provisional ID", failed.stderr)

    def test_missing_main_ref_fails_on_master(self):
        # Deliberately create a master-only repository with no main ref.
        self.git("branch", "-m", "master")
        self.git("update-ref", "refs/heads/other/main", "HEAD")
        result = self.run_cli("add", "No ticket", "-d", "Description.", exit_code=1)
        self.assertIn("main", result.output)
        self.assertIn("main_branch", result.output)
        self.assertEqual(list((self.root / "chitty" / "tasks").glob("*.md")), [])
