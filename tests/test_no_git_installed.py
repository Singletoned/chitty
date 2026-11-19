import os
import re
import shutil
import subprocess
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from chitty import config, git
from chitty.cli import cli
from chitty.errors import ChittyError
from tests.support import RepoTestCase


class TestGitUnavailableHelpers(RepoTestCase):
    def test_commands_match_with_and_without_git(self):
        self.assertFalse(git.is_repository(self.root))
        added = CliRunner().invoke(
            cli,
            ["add", "Sample", "-d", "Description"],
            env={"CHITTY_ROOT": str(self.root), "CHITTY_ACTOR": "test"},
        )
        self.assertEqual(added.exit_code, 0, added.output)
        empty_path = self.tmp / "empty-path"
        empty_path.mkdir()
        cases = (
            ("list",),
            ("show", "TASK-1"),
            ("path", "TASK-1"),
            ("next",),
            ("edit", "TASK-1", "-s", "planning"),
            ("note", "TASK-1", "x"),
            ("check",),
            ("move", "TASK-1", "human"),
            ("archive",),
        )
        for index, args in enumerate(cases):
            with self.subTest(command=args):
                outputs = []
                snapshots = []
                for label, path in (("git", os.environ["PATH"]), ("no-git", str(empty_path))):
                    root = self.tmp / f"{label}-{index}"
                    shutil.copytree(self.root, root)
                    invocation_env = {
                        "CHITTY_ROOT": str(root),
                        "PATH": path,
                        "CHITTY_ACTOR": "test",
                    }
                    if args[0] == "archive":
                        moved = CliRunner().invoke(
                            cli,
                            ["move", "TASK-1", "human"],
                            env=invocation_env,
                        )
                        self.assertEqual(moved.exit_code, 0, moved.output)
                        moved_id = re.search(r"HUMAN-\d+", moved.output)
                        if moved_id is None:
                            self.fail(f"move output did not include the new ID: {moved.output}")
                        command_args = ["archive", moved_id.group()]
                    else:
                        command_args = list(args)
                    config.git_common_dir.cache_clear()
                    result = CliRunner().invoke(cli, command_args, env=invocation_env)
                    self.assertEqual(result.exit_code, 0, result.output)
                    outputs.append(result.output.replace(str(root), "<ROOT>"))
                    files = {}
                    for file_path in sorted(root.rglob("*")):
                        if file_path.is_file():
                            relative = file_path.relative_to(root).as_posix()
                            contents = file_path.read_text()
                            contents = re.sub(
                                r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z",
                                "<TIMESTAMP>",
                                contents,
                            )
                            files[relative] = contents
                    snapshots.append(files)
                self.assertEqual(outputs[0], outputs[1])
                self.assertEqual(snapshots[0], snapshots[1])

    def test_helpers_return_empty_answers_without_git_outside_repository(self):
        empty_path = self.tmp / "empty-path"
        empty_path.mkdir()
        with patch.dict(os.environ, {"PATH": str(empty_path)}):
            config.git_common_dir.cache_clear()
            self.assertEqual(git.dirty_paths(self.root, Path("chitty")), set())
            self.assertIsNone(git.current_branch(self.root))
            self.assertIsNone(config.git_common_dir(self.root))

    def test_dirty_paths_surfaces_git_failure_inside_repository(self):
        subprocess.run(["git", "init", str(self.root)], check=True, capture_output=True)
        (self.root / ".git" / "index").write_text("garbage")
        with self.assertRaisesRegex(ChittyError, "index file smaller than expected"):
            git.dirty_paths(self.root, Path("chitty"))
