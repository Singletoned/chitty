import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from click.testing import CliRunner

from chitty.cli import cli
from chitty.errors import ChittyError
from chitty.store import guide


class TestGuideRebase(unittest.TestCase):
    def git(self, root: Path, *args: str) -> None:
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)

    def repository(self, backend: str) -> Path:
        root = Path(tempfile.mkdtemp())
        self.git(root, "init", "--quiet", "-b", "main")
        self.git(root, "config", "user.email", "test@example.com")
        self.git(root, "config", "user.name", "Test")
        (root / "conflict.txt").write_text("base\n")
        self.git(root, "add", ".")
        self.git(root, "commit", "--quiet", "-m", "base")
        self.git(root, "checkout", "--quiet", "-b", "topic")
        (root / "conflict.txt").write_text("topic\n")
        self.git(root, "commit", "--quiet", "-am", "topic")
        self.git(root, "checkout", "--quiet", "main")
        (root / "conflict.txt").write_text("main\n")
        self.git(root, "commit", "--quiet", "-am", "main")
        self.git(root, "checkout", "--quiet", "topic")
        args = ["rebase"] + (["--apply"] if backend == "rebase-apply" else []) + ["main"]
        result = subprocess.run(["git", *args], check=False, cwd=root, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        return root

    def test_help_names_the_rebase_guide(self):
        help_result = CliRunner().invoke(cli, ["guide", "--help"], catch_exceptions=False)
        self.assertIn("chitty guide rebase TASK-12", help_result.output)
        self.assertIn("rebase accept an optional ticket ID", help_result.output)

    def test_stopped_rebase_injects_text_for_both_guides_and_backends(self):
        insertion = (Path(__file__).parents[1] / "src/chitty/roles/rebase.md").read_text().rstrip()
        for backend in ("rebase-merge", "rebase-apply"):
            with self.subTest(backend=backend):
                root = self.repository(backend)
                for directory in (root, root / "nested"):
                    directory.mkdir(exist_ok=True)
                    for role in ("work", "repair"):
                        output = guide(role, "TASK-1", directory=directory, workflow="runner")
                        self.assertIn(
                            f"Work only on Chitty ticket TASK-1.\n\n{insertion}\n\n", output
                        )
                        expected = guide(
                            role, "TASK-1", directory=Path(tempfile.mkdtemp()), workflow="runner"
                        )
                        self.assertEqual(output.replace(insertion + "\n\n", "", 1), expected)
                        previous = Path.cwd()
                        try:
                            os.chdir(directory)
                            cli_output = (
                                CliRunner()
                                .invoke(cli, ["guide", role, "TASK-1"], catch_exceptions=False)
                                .output
                            )
                        finally:
                            os.chdir(previous)
                        self.assertEqual(cli_output, output)
                unrelated = Path(tempfile.mkdtemp())
                for role in ("review", "plan", "cold-read"):
                    ticket_id = "TASK-1" if role == "review" else None
                    self.assertEqual(
                        guide(role, ticket_id, directory=root, workflow="runner"),
                        guide(role, ticket_id, directory=unrelated, workflow="runner"),
                    )
                self.git(root, "rebase", "--abort")
                for role in ("work", "repair"):
                    self.assertEqual(
                        guide(role, "TASK-1", directory=root, workflow="runner"),
                        guide(role, "TASK-1", directory=unrelated, workflow="runner"),
                    )

    def test_outside_repository_and_missing_directory(self):
        outside = Path(tempfile.mkdtemp())
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=outside,
            check=False,
            capture_output=True,
        )
        self.assertNotEqual(result.returncode, 0)
        for role in ("work", "repair"):
            with self.assertRaises(ChittyError):
                guide(role, "TASK-1", directory=outside / "missing", workflow="runner")
            self.assertEqual(
                guide(role, "TASK-1", directory=outside, workflow="runner"),
                guide(role, "TASK-1", directory=Path(tempfile.mkdtemp()), workflow="runner"),
            )

    def test_linked_worktree_detects_its_stopped_rebase(self):
        root = self.repository("rebase-merge")
        self.git(root, "rebase", "--abort")
        linked = Path(tempfile.mkdtemp())
        linked.rmdir()
        self.git(root, "worktree", "add", "--quiet", "--detach", str(linked), "main")
        self.git(linked, "checkout", "--quiet", "-b", "linked-topic")
        (linked / "conflict.txt").write_text("linked\n")
        self.git(linked, "commit", "--quiet", "-am", "linked")
        result = subprocess.run(
            ["git", "rebase", "topic"], check=False, cwd=linked, capture_output=True
        )
        self.assertNotEqual(result.returncode, 0)
        insertion = (Path(__file__).parents[1] / "src/chitty/roles/rebase.md").read_text().rstrip()
        outside = Path(tempfile.mkdtemp())
        for role in ("work", "repair"):
            output = guide(role, "TASK-1", directory=linked, workflow="runner")
            self.assertIn(f"Work only on Chitty ticket TASK-1.\n\n{insertion}\n\n", output)
            self.assertEqual(
                output.replace(insertion + "\n\n", "", 1),
                guide(role, "TASK-1", directory=outside, workflow="runner"),
            )
