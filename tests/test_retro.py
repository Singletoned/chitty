import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "retro.py"

COLD_READ_PASSED = """---
title: First
status: done
created: 2026-11-02
---

## Notes

Cold read by a fresh agent.

Reviewed: all good.

## History

- 2026-11-02T10:00:00Z a → backlog
- 2026-11-03T10:00:00Z a doing → review
- 2026-11-03T11:00:00Z b review → done
"""

FAILED_THEN_PASSED = """---
title: Second
status: done
created: 2026-11-02
---

## Notes

Review failed (tests): no test fails without the change.

Reviewed: fixed.

## History

- 2026-11-03T10:00:00Z a doing → review
- 2026-11-03T11:00:00Z b review → doing
- 2026-11-10T10:00:00Z a doing → review
- 2026-11-10T11:00:00Z b review → done
"""


class RetroTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name) / "repo"
        self.data = Path(directory.name) / "data"
        tasks = self.root / "chitty" / "tasks"
        tasks.mkdir(parents=True)
        (self.root / "chitty.toml").write_text('project = "demo"\n')
        (tasks / "TASK-1--first.md").write_text(COLD_READ_PASSED)
        (tasks / "TASK-2--second.md").write_text(FAILED_THEN_PASSED)
        usage = self.data / "chitty" / "usage"
        usage.mkdir(parents=True)
        records = [
            {"started": "2026-11-03T09:00:00Z", "seconds": 3600, "status_after": "review"},
            {"started": "2026-11-04T09:00:00Z", "seconds": 1800, "status_after": "error"},
        ]
        (usage / "demo.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.commit("2026-11-03T12:00:00", "chitty: edit TASK-1 First")
        self.commit("2026-11-03T13:00:00", "Implement the first ticket")

    def git(self, *args: str, env: dict[str, str] | None = None) -> None:
        subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True, env=env)

    def commit(self, date: str, subject: str) -> None:
        env = {**os.environ, "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date}
        self.git("commit", "--quiet", "--allow-empty", "-m", subject, env=env)

    def run_retro(self) -> str:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(self.root)],
            env={**os.environ, "XDG_DATA_HOME": str(self.data)},
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout

    def test_reports_reviews_cold_reads_sessions_and_commits_by_week(self):
        output = self.run_retro()
        self.assertIn("## demo", output)
        self.assertIn("| 2026-W45 | 1/1 | 100% of 1 | 0% of 1 | 2 | 1.5 | 1 | 2 | 50% |", output)
        self.assertIn("| 2026-W46 | 1/0 | - of 0 | - of 0 | 0 | 0.0 | 0 | 0 | - |", output)
        self.assertIn("Failed reviews by cause: tests 1", output)
        self.assertIn("- 1 TASK-2", output)

    def test_ticket_without_created_date_fails_loudly(self):
        (self.root / "chitty" / "tasks" / "TASK-3--broken.md").write_text("---\ntitle: x\n---\n")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(self.root)],
            env={**os.environ, "XDG_DATA_HOME": str(self.data)},
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("TASK-3: no `created:` date", result.stderr)


if __name__ == "__main__":
    unittest.main()
