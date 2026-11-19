"""`scripts/release.sh` releases from a temporary worktree.

Each test builds a repository with a bare `origin`, the real release scripts,
a fixture `Makefile`, a stub `watch_release.py` and a fake `uv` on `PATH`, so
the release runs end to end without the network.
"""

import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

CHECKOUT = Path(__file__).parents[1]

MAKEFILE = """\
install:
\ttrue

check:
\tsh "$(CHECK_SCRIPT)"
"""

WATCH = """\
import os, sys
from pathlib import Path
Path(os.environ["WATCHED"]).write_text(sys.argv[1])
"""

# `uv run python ARGS` becomes `python3 ARGS`, with this checkout's `src`
# importable so `scripts/release_version.py` can read the tickets.
FAKE_UV = """\
#!/bin/sh
shift
shift
exec python3 "$@"
"""


class TestReleaseScript(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.tmp = Path(directory.name).resolve()
        self.origin = self.tmp / "origin.git"
        self.root = self.tmp / "repo"
        self.watched = self.tmp / "watched"
        self.check_script = self.tmp / "check.sh"
        self.check_script.write_text("true\n")
        subprocess.run(["git", "init", "--quiet", "--bare", str(self.origin)], check=True)
        self.root.mkdir()
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        (self.root / "Makefile").write_text(MAKEFILE)
        (self.root / "scripts").mkdir()
        for name in ("release.sh", "release_version.py"):
            shutil.copy(CHECKOUT / "scripts" / name, self.root / "scripts" / name)
        (self.root / "scripts" / "watch_release.py").write_text(WATCH)
        (self.root / "src" / "chitty").mkdir(parents=True)
        (self.root / "src" / "chitty" / "__init__.py").write_text('__version__ = "0.1.0"\n')
        (self.root / "chitty" / "tasks").mkdir(parents=True)
        (self.root / "chitty" / "tasks" / ".gitkeep").write_text("")
        (self.root / "notes.txt").write_text("committed\n")
        (self.root / ".gitignore").write_text(".worktrees/\n")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "base")
        self.git("tag", "v0.1.0")
        self.git("remote", "add", "origin", str(self.origin))
        self.git("push", "--quiet", "origin", "main", "v0.1.0")
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir()
        uv = bin_dir / "uv"
        uv.write_text(FAKE_UV)
        uv.chmod(uv.stat().st_mode | stat.S_IXUSR)
        self.env = {
            **os.environ,
            "PATH": f"{bin_dir}:{os.environ['PATH']}",
            "PYTHONPATH": str(CHECKOUT / "src"),
            "CHECK_SCRIPT": str(self.check_script),
            "WATCHED": str(self.watched),
            "XDG_DATA_HOME": str(self.tmp / "data"),
        }
        self.env.pop("VIRTUAL_ENV", None)
        self.env.pop("UV_PROJECT_ENVIRONMENT", None)

    def git(self, *args: str, cwd: Path | None = None) -> str:
        return subprocess.run(
            ["git", *args], cwd=cwd or self.root, check=True, capture_output=True, text=True
        ).stdout

    def release(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["sh", "scripts/release.sh"],
            cwd=self.root,
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
        )

    def origin_git(self, *args: str) -> str:
        return subprocess.run(
            ["git", "--git-dir", str(self.origin), *args],
            check=True,
            capture_output=True,
            text=True,
        ).stdout

    def test_releases_while_main_moves_and_the_checkout_is_dirty(self):
        # The check commits to the main checkout, as a runner landing a ticket would.
        self.check_script.write_text(
            f'echo moved > "{self.root}/moved.txt"\n'
            f'git -C "{self.root}" add moved.txt\n'
            f'git -C "{self.root}" commit --quiet -m "landed during release"\n'
        )
        (self.root / "notes.txt").write_text("uncommitted edit\n")
        (self.root / "untracked.txt").write_text("untracked\n")

        result = self.release()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            self.origin_git("log", "-1", "--format=%s", "main").strip(), "Release 0.1.1"
        )
        self.assertEqual(
            self.origin_git("rev-parse", "v0.1.1^{commit}"), self.origin_git("rev-parse", "main")
        )
        self.assertIn('__version__ = "0.1.1"', (self.root / "src/chitty/__init__.py").read_text())
        local = self.git("log", "--format=%s", "main").splitlines()
        self.assertIn("Release 0.1.1", local)
        self.assertIn("landed during release", local)
        self.assertEqual((self.root / "notes.txt").read_text(), "uncommitted edit\n")
        self.assertTrue((self.root / "untracked.txt").exists())
        self.assertFalse((self.root / ".worktrees" / "release").exists())
        self.assertEqual(self.watched.read_text(), "0.1.1")
        pending = self.tmp / "data" / "chitty" / "pending-release"
        self.assertEqual(pending.read_text().strip(), "0.1.1")

    def test_failed_check_publishes_nothing_and_removes_the_worktree(self):
        self.check_script.write_text("exit 1\n")
        main_before = self.git("rev-parse", "main")
        origin_before = self.origin_git("rev-parse", "main")

        result = self.release()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("checks failed at 0.1.1", result.stderr)
        self.assertEqual(self.git("rev-parse", "main"), main_before)
        self.assertEqual(self.origin_git("rev-parse", "main"), origin_before)
        self.assertEqual(self.git("tag", "--list", "v0.1.1"), "")
        self.assertFalse((self.root / ".worktrees" / "release").exists())
        self.assertFalse(self.watched.exists())

    def test_main_behind_origin_is_refused(self):
        other = self.tmp / "other"
        subprocess.run(["git", "clone", "--quiet", str(self.origin), str(other)], check=True)
        self.git("config", "user.email", "test@example.com", cwd=other)
        self.git("config", "user.name", "Test", cwd=other)
        (other / "elsewhere.txt").write_text("pushed elsewhere\n")
        self.git("add", "elsewhere.txt", cwd=other)
        self.git("commit", "--quiet", "-m", "elsewhere", cwd=other)
        self.git("push", "--quiet", "origin", "main", cwd=other)

        result = self.release()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("main is behind origin/main", result.stderr)
        self.assertFalse((self.root / ".worktrees" / "release").exists())


if __name__ == "__main__":
    unittest.main()
