import json
import os
import subprocess
import sys
from pathlib import Path, PurePosixPath
from unittest import mock

from chitty import git
from chitty.errors import ChittyError
from tests.support import RepoTestCase


class TestHistoricalFiles(RepoTestCase):
    def test_read_blobs_handles_output_larger_than_pipe_buffers(self):
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        contents = {}
        for index in range(5000):
            path = Path(f"files/{index:04}.txt")
            content = f"{index:04}" + "x" * 1019
            (self.root / path).parent.mkdir(exist_ok=True)
            (self.root / path).write_text(content)
            contents[str(path)] = content
        self.commit("large blob set")

        script = f"""
import json
from pathlib import Path
import chitty.git
from chitty.git import _read_blobs

source = Path(chitty.git.__file__).resolve()
assert source.is_relative_to(Path({str(Path(git.__file__).resolve().parent.parent)!r}))
objects = []
for line in __import__("subprocess").run(
    ["git", "ls-tree", "-r", "--full-tree", "HEAD"],
    check=True, capture_output=True, text=True,
).stdout.splitlines():
    metadata, filename = line.split("\\t", 1)
    object_id = metadata.split()[2]
    if filename.startswith("files/"):
        objects.append((object_id, Path(filename)))
result = _read_blobs(Path.cwd(), objects)
print(json.dumps({{str(path): content for (_, path), (_, content) in result.items()}}))
"""
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
            timeout=20,
            env={
                **os.environ,
                "PYTHONPATH": str(Path(git.__file__).resolve().parent.parent),
            },
        )
        self.assertEqual(json.loads(result.stdout), contents)

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

    def test_changed_paths_disables_rename_detection_and_preserves_unicode(self):
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        (self.root / "src").mkdir()
        (self.root / "src/a.py").write_text("code\n")
        self.commit("initial")
        self.git("branch", "main")
        self.git("checkout", "-b", "worker")
        (self.root / "src/a.py").rename(self.root / "src/a.tmp")
        (self.root / "chitty/tasks").mkdir(parents=True)
        (self.root / "src/a.tmp").rename(self.root / "chitty/tasks/a.md")
        self.commit("move")
        self.assertEqual(
            git.changed_paths(self.root, "main", "worker"),
            [PurePosixPath("chitty/tasks/a.md"), PurePosixPath("src/a.py")],
        )
        (self.root / "chitty/tasks/é.md").write_text("task\n")
        self.commit("unicode")
        self.assertIn(
            PurePosixPath("chitty/tasks/é.md"), git.changed_paths(self.root, "main", "worker")
        )

    def test_non_repository_has_no_history(self):
        directory = self.tmp / "not-a-repository"
        directory.mkdir()
        self.assertEqual(git.historical_files(directory, Path("chitty/tasks")), [])
