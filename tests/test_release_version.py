import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "release_version.py"


class ReleaseVersionTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.write_version("0.1.9")
        self.commit("initial")
        self.git("tag", "v0.1.9")

    def git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args], cwd=self.root, check=True, capture_output=True, text=True
        )
        return result.stdout

    def write(self, relative: str, content: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def write_version(self, version: str) -> None:
        self.write("src/chitty/__init__.py", f'__version__ = "{version}"\n')

    def commit(self, message: str) -> None:
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", message)

    def ticket(self, path: str, labels: str = "") -> None:
        labels_line = f"labels: [{labels}]\n" if labels else ""
        self.write(
            path,
            "---\n"
            "title: Example\n"
            "status: done\n"
            f"{labels_line}"
            "created: 2026-01-01\n"
            "---\n\n"
            "## Description\n\nExample.\n",
        )

    def run_script(self) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(Path(__file__).parents[1] / "src")
        return subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=self.root,
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )

    def test_patch_bump_without_label(self):
        self.ticket("chitty/tasks/TASK-1--example.md")
        self.commit("ticket")
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "0.1.10")
        self.assertEqual(result.stderr, "")

    def test_minor_bump_for_active_or_archived_labelled_ticket(self):
        self.ticket("chitty/tasks/TASK-1--active.md", "needs-minor")
        self.ticket("chitty/tasks/archive/TASK-2--archived.md", "needs-minor")
        self.commit("labelled tickets")
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "0.2.0")
        self.assertIn("TASK-1", result.stderr)
        self.assertIn("TASK-2", result.stderr)

    def test_label_before_tag_is_ignored(self):
        self.ticket("chitty/tasks/TASK-1--example.md", "needs-minor")
        self.commit("old ticket")
        self.git("tag", "v0.1.10")
        self.write("README.md", "changed\n")
        self.commit("unrelated change")
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "0.1.11")
        self.assertEqual(result.stderr, "")

    def test_current_version_ahead_of_tag_is_bump_base(self):
        self.write_version("0.1.20")
        self.commit("version ahead")
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "0.1.21")

    def test_missing_tag_fails(self):
        self.git("tag", "--delete", "v0.1.9")
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no v* tags", result.stderr)


if __name__ == "__main__":
    unittest.main()
