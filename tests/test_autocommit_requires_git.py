import shutil
import subprocess
from pathlib import Path

from click.testing import CliRunner

from chitty import git
from chitty.cli import cli
from chitty.config import CHITTY_VERSION
from tests.support import CONFIG, RepoTestCase


class TestAutocommitRequiresGit(RepoTestCase):
    def invoke(self, root, path, *args):
        return CliRunner().invoke(
            cli,
            list(args),
            env={"CHITTY_ROOT": str(root), "PATH": str(path), "CHITTY_ACTOR": "test-agent"},
        )

    def files(self, root):
        return {
            str(path.relative_to(root)): path.read_bytes()
            for path in root.rglob("*")
            if path.is_file() and ".git" not in path.relative_to(root).parts
        }

    def test_non_mutating_commands_and_other_writes(self):
        git_path = shutil.which("git")
        if git_path is None:
            raise AssertionError("git executable is required for this test")
        root = self.tmp / "other-writes"
        root.mkdir()
        (root / "chitty.toml").write_text(CONFIG.replace("autocommit = false", "autocommit = true"))
        path = Path(git_path).parent
        added = self.invoke(root, path, "add", "Seed", "-d", "x")
        self.assertNotEqual(added.exit_code, 0)
        (root / "chitty.toml").write_text(CONFIG)
        self.assertEqual(self.invoke(root, path, "add", "Seed", "-d", "x").exit_code, 0)
        (root / "chitty.toml").write_text(
            (root / "chitty.toml").read_text().replace("autocommit = false", "autocommit = true")
        )
        before = self.files(root)
        for args in (("move", "TASK-1", "human"), ("fix",)):
            result = self.invoke(root, path, *args)
            self.assertNotEqual(result.exit_code, 0, result.output)
            self.assertIn("git init", result.output)
            self.assertEqual(self.files(root), before)
        for args in (("show", "TASK-1"), ("list",)):
            result = self.invoke(root, path, *args)
            self.assertEqual(result.exit_code, 0, result.output)
        stale = (root / "chitty.toml").read_text().replace(CHITTY_VERSION, "0.0.1")
        (root / "chitty.toml").write_text(stale)
        before = self.files(root)
        result = self.invoke(root, path, "add", "Other", "-d", "x")
        self.assertNotEqual(result.exit_code, 0, result.output)
        self.assertIn("git init", result.output)
        self.assertEqual(self.files(root), before)

    def test_write_prerequisite_grid(self):
        git_path = shutil.which("git")
        if git_path is None:
            raise AssertionError("git executable is required for this test")
        path = Path(git_path).parent
        cases = (
            ("add", ("add", "Example", "-d", "Description")),
            ("edit", ("edit", "TASK-1", "-s", "planning")),
            ("note", ("note", "TASK-1", "x")),
        )
        for command, args in cases:
            for autocommit in (False, True):
                for has_git in (False, True):
                    for initialized in (False, True):
                        with self.subTest(
                            command=command,
                            autocommit=autocommit,
                            has_git=has_git,
                            initialized=initialized,
                        ):
                            root = self.tmp / f"{command}-{autocommit}-{has_git}-{initialized}"
                            root.mkdir()
                            (root / "chitty.toml").write_text(CONFIG)
                            baseline = self.invoke(root, path, "add", "Seed", "-d", "x")
                            self.assertEqual(baseline.exit_code, 0, baseline.output)
                            if initialized:
                                subprocess.run([git_path, "init", "--quiet", str(root)], check=True)
                                subprocess.run(
                                    [
                                        git_path,
                                        "-C",
                                        str(root),
                                        "config",
                                        "user.email",
                                        "test@example.com",
                                    ],
                                    check=True,
                                )
                                subprocess.run(
                                    [git_path, "-C", str(root), "config", "user.name", "Test"],
                                    check=True,
                                )
                            else:
                                self.assertFalse(git.is_repository(root))
                            config = root / "chitty.toml"
                            config.write_text(
                                config.read_text().replace(
                                    "autocommit = false", f"autocommit = {str(autocommit).lower()}"
                                )
                            )
                            before = self.files(root)
                            command_path = path if has_git else self.tmp / "empty-path"
                            command_path.mkdir(exist_ok=True)
                            result = self.invoke(root, command_path, *args)
                            should_succeed = (not autocommit and (not initialized or has_git)) or (
                                autocommit and initialized and has_git
                            )
                            if should_succeed:
                                self.assertEqual(result.exit_code, 0, result.output)
                                if autocommit:
                                    subject = subprocess.run(
                                        [git_path, "-C", str(root), "log", "-1", "--format=%s"],
                                        check=True,
                                        capture_output=True,
                                        text=True,
                                    ).stdout
                                    self.assertTrue(subject.startswith("chitty:"), subject)
                            else:
                                self.assertNotEqual(result.exit_code, 0, result.output)
                                self.assertNotIn("Traceback", result.output)
                                if autocommit and not has_git:
                                    self.assertIn("PATH", result.output)
                                elif autocommit:
                                    self.assertIn("git init", result.output)
                                else:
                                    self.assertIn("PATH", result.output)
                                self.assertEqual(self.files(root), before)
