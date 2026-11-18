import os
import stat
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path
from unittest.mock import patch

from tests.test_cli import CliTestCase


class TestRunClaimsOnMain(CliTestCase):
    def setUp(self):
        super().setUp()
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.run_cli("init")
        self.run_cli("add", "Claim me", "-d", "Description.")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "initial")
        self.logs = self.root / "logs"
        self.logs.mkdir()
        self.agent(self.logs / "agent")
        config.write_text(
            config.read_text().replace(
                'agent_command = "pi --chitty-{mode} {id}"',
                f'agent_command = "fake {{mode}} {{id}} {self.logs / "agent"}"',
            )
        )
        fake = self.root / "bin" / "fake"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\n"
            "from pathlib import Path\n"
            "import sys\n"
            "ticket = next(Path('chitty/tasks').glob('TASK-1--*.md'))\n"
            "Path(sys.argv[3]).write_text(ticket.read_text())\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "configure runner")
        self.path_patch = patch.dict(os.environ, {"PATH": f"{fake.parent}:{os.environ['PATH']}"})
        self.path_patch.start()
        self.addCleanup(self.path_patch.stop)

    def agent(self, path: Path) -> None:
        path.parent.mkdir(exist_ok=True)

    def git(
        self,
        *args: str,
        cwd: Path | None = None,
        env: Mapping[str, str] | None = None,
    ) -> str:
        return subprocess.run(
            ["git", *args],
            cwd=cwd or self.root,
            env={**os.environ, **(env or {})},
            capture_output=True,
            text=True,
            check=True,
        ).stdout

    def test_todo_claim_is_committed_on_main_and_inherited_by_new_branch(self):
        result = self.run_cli("run")

        self.assertIn("doing → error", result.stdout)
        claim = self.git("rev-parse", "task-1").strip()
        self.assertEqual(self.git("merge-base", "--is-ancestor", claim, "main", cwd=self.root), "")
        self.assertIn("status: doing", (self.logs / "agent").read_text())

    def test_claim_succeeds_when_main_has_a_newer_ticket_commit(self):
        self.git("switch", "--quiet", "-c", "task-1")
        task = next((self.root / "chitty/tasks").glob("TASK-1--*.md"))
        task.write_text(task.read_text().replace("Description.", "Branch edit."))
        self.git("add", str(task))
        self.git(
            "commit",
            "--quiet",
            "-m",
            "branch ticket edit",
            env={"GIT_COMMITTER_DATE": "2026-11-18T10:00:00+00:00"},
        )
        self.git("switch", "--quiet", "main")
        task = next((self.root / "chitty/tasks").glob("TASK-1--*.md"))
        task.write_text(task.read_text().replace("Description.", "Main edit."))
        self.git("add", str(task))
        self.git(
            "commit",
            "--quiet",
            "-m",
            "newer main ticket edit",
            env={"GIT_COMMITTER_DATE": "2026-11-18T10:01:00+00:00"},
        )
        self.git("switch", "--quiet", "task-1")
        self.git("switch", "--quiet", "main")

        result = self.run_cli("run")

        self.assertIn("doing → error", result.stdout)
        self.assertTrue((self.logs / "agent").exists())
        self.assertNotIn("latest committed version", result.stderr)
