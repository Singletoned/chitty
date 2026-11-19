import subprocess

from tests.test_cli import CliTestCase


class TestCommitEmptyPaths(CliTestCase):
    def setUp(self):
        super().setUp()
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace("autocommit = false", "autocommit = true")
            .replace("[contexts.tasks]", 'archive = "delete"\n\n[contexts.tasks]')
        )
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "init")

    def git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args], cwd=self.root, capture_output=True, text=True, check=True
        )
        return result.stdout

    def test_deleting_archive_does_not_repair_unrelated_ticket(self):
        self.run_cli("add", "Archived", "-d", "x")
        self.run_cli("add", "Dependent", "-d", "x")
        archived = self.root / "chitty/tasks/TASK-1--archived.md"
        other = self.root / "chitty/tasks/TASK-2--dependent.md"
        self.run_cli("edit", "1", "-s", "review")
        self.run_cli(
            "edit",
            "1",
            "-s",
            "done",
            "--note",
            "Reviewed: ready.",
            "--override-review-independence",
        )
        content = other.read_text().replace("created:", "depends_on: [task-1]\ncreated:")
        other.write_text(content)
        self.git("add", str(other.relative_to(self.root)))
        self.git("commit", "--quiet", "-m", "write lower-case dependency")
        original = other.read_bytes()

        self.run_cli("archive", "1")

        self.assertFalse(archived.exists())
        self.assertEqual(other.read_bytes(), original)
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_fix_without_paths_still_repairs_lowercase_reference(self):
        self.run_cli("add", "First", "-d", "x")
        self.run_cli("add", "Second", "-d", "x")
        path = self.root / "chitty/tasks/TASK-2--second.md"
        path.write_text(path.read_text().replace("created:", "depends_on: [task-1]\ncreated:"))
        self.run_cli("fix")
        self.assertIn("TASK-1", path.read_text())
        self.assertNotIn("task-1", path.read_text())
