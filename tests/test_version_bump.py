import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "check_version_bump.py"


class VersionBumpTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.tmp = Path(directory.name)
        self.root = self.tmp / "repo"
        self.root.mkdir()
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.write_version("0.1.9")
        self.write("src/chitty/guide.md", "guide\n")
        self.write("src/chitty/integrations/pi/chitty.ts", "extension\n")
        self.write("src/chitty/roles/agent.md", "role\n")
        self.write("src/chitty/config.py", 'INITIAL_CONFIG = """initial"""\n')
        self.write("scripts/check_version_bump.py", SCRIPT.read_text())
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

    def run_check(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=self.root,
            check=False,
            capture_output=True,
            text=True,
        )

    def start_branch(self) -> None:
        self.git("switch", "--quiet", "-c", "worker")

    def test_watched_changes_require_higher_version(self):
        for path in (
            "src/chitty/guide.md",
            "src/chitty/integrations/pi/chitty.ts",
            "src/chitty/roles/agent.md",
            "src/chitty/config.py",
        ):
            with self.subTest(path=path):
                self.git("switch", "--quiet", "main")
                self.git("reset", "--quiet", "--hard", "main")
                self.git("branch", "--force", "worker", "main")
                self.git("switch", "--quiet", "worker")
                if path == "src/chitty/config.py":
                    self.write(path, 'INITIAL_CONFIG = """changed"""\n')
                else:
                    self.write(path, "changed\n")
                result = self.run_check()
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(path, result.stderr)
                self.write_version("0.1.10")
                result = self.run_check()
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_same_version_fails_and_numeric_version_comparison_passes(self):
        self.start_branch()
        self.write("src/chitty/guide.md", "changed\n")
        result = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.write_version("0.1.10")
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_unrelated_config_change_passes(self):
        self.start_branch()
        self.write("src/chitty/config.py", 'OTHER = "changed"\nINITIAL_CONFIG = """initial"""\n')
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_branch_behind_main_with_no_changes_passes(self):
        self.start_branch()
        self.write_version("0.1.10")
        self.commit("worker version")
        self.git("switch", "--quiet", "main")
        self.write_version("0.1.11")
        self.commit("main version")
        self.git("switch", "--quiet", "worker")
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_main_passes(self):
        self.write("src/chitty/guide.md", "changed\n")
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_main_passes_with_notice(self):
        self.git("switch", "--detach", "--quiet")
        self.git("branch", "-D", "main")
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("no refs/heads/main", result.stderr)

    def test_shallow_tag_clone_without_main_passes(self):
        clone = self.root.parent / "clone"
        clone_result = subprocess.run(
            [
                "git",
                "clone",
                "--quiet",
                "--depth",
                "1",
                "--branch",
                "v0.1.9",
                f"file://{self.root}",
                str(clone),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(clone_result.returncode, 0, clone_result.stderr)
        result = subprocess.run(
            [sys.executable, str(clone / "scripts/check_version_bump.py")],
            cwd=clone,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("no refs/heads/main", result.stderr)


if __name__ == "__main__":
    unittest.main()
