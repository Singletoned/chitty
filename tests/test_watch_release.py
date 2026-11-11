import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "watch_release.py"

FAKES = {
    "gh": """#!/bin/sh
echo "gh $*" >> "$CALLS"
if [ "$2" = list ]; then echo '[{"databaseId": 7, "url": "https://example.invalid/7"}]'; fi
if [ "$2" = watch ]; then exit "$WATCH_STATUS"; fi
""",
    "uv": """#!/bin/sh
echo "uv $*" >> "$CALLS"
if [ "$2" = list ]; then printf 'chitty v1.2.3\\n- chitty\\n'; fi
""",
    "sump": """#!/bin/sh
echo "sump $*" >> "$CALLS"
""",
}


class TestWatchRelease(unittest.TestCase):
    def run_script(self, watch_status: int) -> tuple[subprocess.CompletedProcess[str], str]:
        with tempfile.TemporaryDirectory() as directory:
            bin_dir = Path(directory)
            for name, body in FAKES.items():
                path = bin_dir / name
                path.write_text(body)
                path.chmod(0o755)
            calls = bin_dir / "calls"
            calls.touch()
            environment = {
                **os.environ,
                "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
                "CALLS": str(calls),
                "WATCH_STATUS": str(watch_status),
            }
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "1.2.3"],
                check=False,
                env=environment,
                capture_output=True,
                text=True,
            )
            return completed, calls.read_text()

    def test_success_upgrades_global_chitty(self) -> None:
        completed, calls = self.run_script(0)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("gh run list --workflow release.yml --branch v1.2.3", calls)
        self.assertIn("gh run watch 7 --exit-status", calls)
        self.assertIn("uv tool upgrade chitty", calls)
        self.assertNotIn("sump", calls)

    def test_failure_captures_in_sump_and_exits_non_zero(self) -> None:
        completed, calls = self.run_script(1)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("publish workflow failed for v1.2.3", completed.stderr)
        self.assertIn(
            "sump capture chitty --message release v1.2.3: publish workflow failed", calls
        )
        self.assertIn("https://example.invalid/7", calls)
        self.assertNotIn("uv tool upgrade", calls)


if __name__ == "__main__":
    unittest.main()
