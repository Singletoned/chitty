import shlex
import subprocess
import sys

from tests.test_cli import CliTestCase


class TestAutocommit(CliTestCase):
    def setUp(self):
        super().setUp()
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace("autocommit = false", "autocommit = true"))
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "init")

    def git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args], cwd=self.root, capture_output=True, text=True, check=True
        )
        return result.stdout

    def last_commit(self) -> tuple[str, list[str]]:
        subject = self.git("log", "-1", "--format=%s").strip()
        files = self.git("show", "--no-renames", "--name-status", "--format=", "HEAD").splitlines()
        return subject, files

    def test_each_write_is_one_commit_of_its_own_paths(self):
        (self.root / "unrelated.txt").write_text("staged by the user\n")
        self.git("add", "unrelated.txt")
        self.run_cli("add", "Blocker", "-d", "x")
        self.assertEqual(
            self.last_commit(),
            ("chitty: add TASK-1 Blocker", ["A\tchitty/tasks/TASK-1--blocker.md"]),
        )
        self.run_cli("add", "Blocked", "-d", "x", "--depends-on", "1")
        self.run_cli("edit", "1", "-s", "doing")
        self.assertEqual(self.last_commit()[0], "chitty: edit TASK-1 Blocker")
        commits = int(self.git("rev-list", "--count", "HEAD"))
        self.run_cli("edit", "1", "-s", "doing")
        self.assertEqual(int(self.git("rev-list", "--count", "HEAD")), commits)
        self.run_cli("move", "1", "human")
        subject, files = self.last_commit()
        self.assertEqual(subject, "chitty: move HUMAN-1 Blocker")
        self.assertEqual(
            sorted(files),
            [
                "A\tchitty/human/HUMAN-1--blocker.md",
                "D\tchitty/tasks/TASK-1--blocker.md",
                "M\tchitty/tasks/TASK-2--blocked.md",
            ],
        )
        self.run_cli("archive", "2")
        self.assertEqual(self.last_commit()[0], "chitty: archive TASK-2 Blocked")
        self.assertIn("A  unrelated.txt", self.git("status", "--porcelain"))
        self.assertEqual(self.git("status", "--porcelain", "chitty"), "")

    def test_delete_mode_preserves_ids_from_git_history(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("[contexts.tasks]", 'archive = "delete"\n\n[contexts.tasks]')
        )
        self.run_cli("add", "First done", "-d", "x")
        self.run_cli("add", "Second done", "-d", "x")
        self.run_cli("edit", "1", "-s", "review")
        self.run_cli("edit", "1", "-s", "done")
        self.run_cli("edit", "2", "-s", "review")
        self.run_cli("edit", "2", "-s", "done")

        self.run_cli("archive")
        self.assertEqual(self.run_cli("add", "Third", "-d", "x").stdout.split()[1], "TASK-3")
        (self.root / "chitty/tasks/TASK-3--third.md").unlink()
        self.assertEqual(self.run_cli("add", "Fourth", "-d", "x").stdout.split()[1], "TASK-4")

    def test_archive_done_tasks_makes_one_commit(self):
        self.run_cli("add", "Task done", "-d", "x")
        self.run_cli("add", "Human done", "-c", "human", "-d", "x")
        self.run_cli("edit", "1", "-s", "review")
        self.run_cli("edit", "1", "-s", "done")
        self.run_cli("edit", "HUMAN-1", "-s", "review")
        self.run_cli("edit", "HUMAN-1", "-s", "done")
        commits = int(self.git("rev-list", "--count", "HEAD"))

        self.run_cli("archive")

        self.assertEqual(int(self.git("rev-list", "--count", "HEAD")), commits + 1)
        self.assertEqual(len(self.last_commit()[1]), 4)

    def test_autoformat_runs_before_autocommit(self):
        formatter = self.tmp / "formatter.py"
        formatter.write_text(
            "import pathlib, sys\n"
            "path = pathlib.Path(sys.argv[1])\n"
            "path.write_text(path.read_text().replace('Describe.', 'Formatted.'))\n"
        )
        config = self.root / "chitty.toml"
        command = f"{shlex.quote(sys.executable)} {shlex.quote(str(formatter))}"
        config.write_text(
            config.read_text().replace(
                "[contexts.tasks]", f'autoformat = "{command}"\n\n[contexts.tasks]'
            )
        )

        self.run_cli("add", "Formatted", "-d", "Describe.")

        self.assertIn("Formatted.", self.git("show", "HEAD:chitty/tasks/TASK-1--formatted.md"))

    def test_fix_runs_before_autocommit(self):
        self.run_cli("add", "Blocker", "-d", "x")
        self.run_cli("add", "Dependent", "-d", "x", "--depends-on", "1")
        path = self.root / "chitty/tasks/TASK-2--dependent.md"
        path.write_text(path.read_text().replace("TASK-1", "task-1"))

        self.run_cli("note", "2", "Trigger autocommit.")

        self.assertIn("- TASK-1", self.git("show", "HEAD:chitty/tasks/TASK-2--dependent.md"))

    def test_failure_is_loud(self):
        self.git("config", "core.hooksPath", str(self.tmp / "hooks"))
        hook = self.tmp / "hooks" / "pre-commit"
        hook.parent.mkdir()
        hook.write_text("#!/bin/sh\necho nope >&2\nexit 1\n")
        hook.chmod(0o755)
        result = self.run_cli("add", "X", "-d", "x", exit_code=1)
        self.assertIn("autocommit failed", result.stderr)
        self.assertIn("nope", result.stderr)
