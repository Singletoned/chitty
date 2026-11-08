import subprocess
from pathlib import Path
from unittest import mock

from chitty import git
from chitty.errors import ChittyError
from tests.support import RepoTestCase


class TestHistoricalFiles(RepoTestCase):
    def git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args], cwd=self.root, check=True, capture_output=True, text=True
        )
        return result.stdout

    def commit(self, message: str) -> None:
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", message)

    def test_branch_deleted_after_refs_are_listed_surfaces_git_error(self):
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        (self.root / "chitty/tasks/TASK-1.md").parent.mkdir(parents=True)
        (self.root / "chitty/tasks/TASK-1.md").write_text("task")
        self.commit("initial")
        self.git("branch", "worker")

        original = git._git

        def delete_worker_after_refs(root: Path, *args: str) -> str:
            output = original(root, *args)
            if args[:2] == ("for-each-ref", "--format=%(refname)%09%(symref)"):
                self.git("branch", "-D", "worker")
            return output

        with (
            mock.patch.object(git, "_git", side_effect=delete_worker_after_refs),
            self.assertRaises(ChittyError),
        ):
            git.historical_files(self.root, Path("chitty/tasks"))

    def test_file_at_missing_ref_names_git_command(self):
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        (self.root / "file.txt").write_text("content")
        self.commit("initial")

        with self.assertRaisesRegex(
            ChittyError, r"`git rev-parse --verify no-such-ref` failed in .*"
        ) as raised:
            git.file_at(self.root, "no-such-ref", "file.txt")

        self.assertNotIn("autocommit", str(raised.exception))

    def test_non_repository_has_no_history(self):
        directory = self.tmp / "not-a-repository"
        directory.mkdir()
        self.assertEqual(git.historical_files(directory, Path("chitty/tasks")), [])
