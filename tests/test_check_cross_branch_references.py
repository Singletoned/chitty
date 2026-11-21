import subprocess

from tests.test_cli import CliTestCase


class TestCrossBranchReferences(CliTestCase):
    def setUp(self):
        super().setUp()
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace("autocommit = false", "autocommit = true"))
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.git("branch", "-M", "main")
        self.run_cli("add", "One", "-d", "Describe.")
        self.commit("initial")
        self.initial_commit = self.git("rev-parse", "HEAD")

    def git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args], cwd=self.root, check=True, capture_output=True, text=True
        )
        return result.stdout.strip()

    def commit(self, message: str) -> None:
        self.git("add", "--all")
        self.git("commit", "--quiet", "--allow-empty", "-m", message)

    def add_second(self) -> None:
        self.run_cli("add", "Two", "-d", "Describe.")
        self.commit("second task")

    def check_reference(self, field: str, location: str, missing: bool) -> None:
        with self.subTest(field=field, location=location):
            self.git("checkout", "main")
            subprocess.run(
                ["git", "branch", "-D", "other"],
                cwd=self.root,
                capture_output=True,
                check=False,
            )
            self.git("reset", "--hard", self.initial_commit)
            self.git("clean", "-fd")
            if location == "active":
                self.add_second()
            elif location == "archived":
                self.add_second()
                self.run_cli("archive", "2")
                self.commit("archive second")
            elif location == "other branch":
                self.git("checkout", "-B", "other", "main")
                source = self.root / "chitty/tasks/TASK-1--one.md"
                target = self.root / "chitty/tasks/TASK-2--two.md"
                target.write_text(source.read_text().replace("title: One", "title: Two"))
                self.commit("second task")
                self.git("checkout", "main")
            path = self.root / "chitty/tasks/TASK-1--one.md"
            reference = "depends_on:\n  - TASK-2" if field == "depends_on" else "parent: TASK-2"
            text = path.read_text()
            text = text.replace("status: todo\n", f"status: todo\n{reference}\n")
            path.write_text(text)
            self.commit("add reference")
            show = self.run_cli(
                "show", "2", exit_code=1 if location in {"nowhere", "other branch"} else 0
            )
            check = self.run_cli("check", exit_code=1 if missing else 0)
            self.assertEqual("no such task" in check.stdout, show.exit_code != 0)
            if missing:
                self.assertIn(f"{field} TASK-2: no such task", check.stdout)

    def test_reference_existence_matches_show(self):
        for field in ("depends_on", "parent"):
            for location, missing in (
                ("active", False),
                ("archived", False),
                ("other branch", True),
                ("nowhere", True),
            ):
                self.check_reference(field, location, missing)

    def test_malformed_task_on_another_branch_is_not_read(self):
        self.git("checkout", "-b", "broken")
        malformed = self.root / "chitty/tasks/TASK-3--broken.md"
        malformed.write_text("not task frontmatter\n")
        self.commit("malformed task")
        self.git("checkout", "main")
        task = self.root / "chitty/tasks/TASK-1--one.md"
        task.write_text(
            task.read_text().replace("status: todo\n", "status: todo\ndepends_on:\n  - TASK-3\n")
        )
        self.commit("reference malformed task")

        result = self.run_cli("check", exit_code=1)

        self.assertIn("depends_on TASK-3: no such task", result.stdout)
        self.assertNotIn("file must start with '---' frontmatter", result.stderr)

    def test_edit_on_another_branch_is_refused(self):
        self.git("checkout", "-B", "b", "main")
        self.git("checkout", "main")
        self.add_second()
        self.git("checkout", "b")

        result = self.run_cli("edit", "1", "--depends-on", "2", exit_code=1)

        self.assertIn("latest committed version is on branch main", result.stderr)
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertNotIn("TASK-2", (self.root / "chitty/tasks/TASK-1--one.md").read_text())
