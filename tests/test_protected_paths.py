from chitty.errors import ChittyError
from chitty.run import _land
from chitty.store import NextAction, Repo
from tests.test_review_merge import ReviewMergeTestCase


class TestProtectedPaths(ReviewMergeTestCase):
    def protect(self, *paths: str) -> None:
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace(
                "autocommit = true", f"protected_paths = {list(paths)!r}\nautocommit = true"
            )
        )
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "configure protected paths")

    def change_branch_file(self, operation: str, path: str) -> None:
        self.git("switch", "--quiet", "task-1")
        target = self.root / path
        if operation == "add":
            target.write_text("branch file\n")
        elif operation == "change":
            target.write_text("changed\n")
        elif operation == "delete":
            target.unlink()
        elif operation == "rename":
            target.rename(target.with_name(target.name + ".renamed"))
        else:
            raise AssertionError(operation)
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", f"{operation} protected file")
        self.git("switch", "--quiet", "main")

    def assert_review_blocked(self, path: str) -> None:
        result = self.run_cli("run", "--mode", "review")
        self.assertFalse((self.logs / "agent").exists())
        self.assertEqual(result.stdout, "TASK-1: review → doing\n")
        self.assertIn(
            f"Review failed (work): the branch changes protected files: `{path}`. "
            "Restore them from `main`.",
            self.ticket().section("Notes") or "",
        )

    def test_protected_file_is_added(self):
        self.protect("new.txt")
        self.branch_for_review()
        self.change_branch_file("add", "new.txt")
        self.assert_review_blocked("new.txt")

    def test_protected_file_is_changed(self):
        self.protect("shared.txt")
        self.branch_for_review()
        self.change_branch_file("change", "shared.txt")
        self.assert_review_blocked("shared.txt")

    def test_protected_file_is_deleted(self):
        self.protect("shared.txt")
        self.branch_for_review()
        self.change_branch_file("delete", "shared.txt")
        self.assert_review_blocked("shared.txt")

    def test_protected_file_is_renamed(self):
        self.protect("shared.txt")
        self.branch_for_review()
        self.change_branch_file("rename", "shared.txt")
        self.assert_review_blocked("shared.txt")

    def test_similarly_named_unprotected_files_reach_reviewer(self):
        self.protect("__init__.py", "a*b.py")
        self.branch_for_review()
        self.git("switch", "--quiet", "task-1")
        (self.root / "__init__.py.bak").write_text("not protected\n")
        (self.root / "ab.py").write_text("literal glob name\n")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "change unprotected neighbors")
        self.git("switch", "--quiet", "main")
        result = self.run_cli("run", "--mode", "review")
        self.assertEqual(result.stdout, "TASK-1: review → done\n")
        self.assertTrue((self.logs / "agent").exists())

    def test_main_change_to_protected_file_merges_and_lands(self):
        self.protect("shared.txt")
        self.branch_for_review()
        self.move_main("main protected update\n")
        result = self.run_cli("run", "--mode", "review")
        self.assertEqual(result.stdout, "TASK-1: review → done\n")
        self.assertTrue((self.logs / "agent").exists())

    def test_absent_protected_paths_reaches_reviewer(self):
        self.branch_for_review()
        result = self.run_cli("run", "--mode", "review")
        self.assertEqual(result.stdout, "TASK-1: review → done\n")
        self.assertTrue((self.logs / "agent").exists())

    def test_landing_refuses_protected_change_without_moving_main(self):
        self.protect("shared.txt")
        self.branch_for_review()
        self.git("switch", "--quiet", "task-1")
        task = next((self.root / "chitty/tasks").glob("TASK-1--*.md"))
        task.write_text(task.read_text().replace("status: review", "status: done"))
        (self.root / "shared.txt").write_text("protected branch version\n")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "finish with protected change")
        self.git("switch", "--quiet", "main")
        self.git("worktree", "add", "--quiet", str(self.worktree), "task-1")
        before = self.git("rev-parse", "main").strip()
        repo = Repo.open(self.root)
        action = NextAction("review", repo.resolve("1"))
        with self.assertRaisesRegex(
            ChittyError, "cannot land TASK-1; the branch changes protected files: `shared.txt`"
        ):
            _land(repo, self.worktree, action, "true", "true")
        self.assertEqual(self.git("rev-parse", "main").strip(), before)
        self.assertTrue(self.worktree.exists())
