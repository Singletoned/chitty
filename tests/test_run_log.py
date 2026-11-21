import shlex
import sys
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from hypothesis import given
from hypothesis import strategies as st

from chitty.ids import TaskId
from chitty.run import log_path
from tests.test_cli import CliTestCase
from tests.test_source_copy_errors import SourceCopyErrorChecks


class TestLogPath(TestCase):
    @given(
        st.text(alphabet="abc012", min_size=1, max_size=8),
        st.text(alphabet="ABC", min_size=1, max_size=4),
        st.one_of(st.integers(1, 9999), st.text(alphabet="ABC012", max_size=5).map("A".__add__)),
        st.datetimes(min_value=datetime(2, 1, 1), max_value=datetime(9998, 12, 31)),
        st.integers(-720, 720),
    )
    def test_utc_filename(self, directory, prefix, suffix, instant, offset):
        common = Path("/") / directory
        task_id = TaskId(prefix, suffix)
        utc = instant.replace(tzinfo=UTC)
        aware = utc.astimezone(timezone(timedelta(minutes=offset)))
        stamp = (
            utc.isoformat(timespec="microseconds")
            .split("+")[0]
            .translate(str.maketrans("", "", "-:T."))
        )
        self.assertEqual(
            log_path(common, task_id, aware), common / f"chitty/run/{task_id}-{stamp}Z.log"
        )

    def test_small_year(self):
        self.assertEqual(
            log_path(Path("/git"), TaskId("TASK", 1), datetime(9, 1, 2, tzinfo=UTC)),
            Path("/git/chitty/run/TASK-1-00090102000000000000Z.log"),
        )


class TestRunLog(CliTestCase):
    git = SourceCopyErrorChecks.git
    init_git = SourceCopyErrorChecks.init_git
    commit = SourceCopyErrorChecks.commit

    def fixture(self, body: str, *, setup="true", timeout=0):
        script = self.tmp / "agent.py"
        script.write_text("import subprocess, sys, time\nfrom pathlib import Path\n" + body)
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace(
                "autocommit = false",
                f'autocommit = true\nsetup = "{setup}"\nagent_timeout = {timeout}',
            )
            .replace(
                "pi --chitty-{mode} {id}",
                f"{shlex.quote(sys.executable)} {shlex.quote(str(script))} {{prompt}}",
            )
        )
        self.init_git()
        self.run_cli("init")
        self.commit()
        return self.json("add", "Subject", "-d", "Fixture.", "-s", "todo")

    def one_log(self, result):
        lines = [
            line.removeprefix("log: ")
            for line in result.stderr.splitlines()
            if line.startswith("log: ")
        ]
        self.assertEqual(len(lines), 1, result.stderr)
        path = Path(lines[0])
        directory = self.root / ".git/chitty/run"
        self.assertEqual(list(directory.glob("*.log")), [path])
        self.assertEqual(path.parent, directory)
        return path.read_text()

    def test_continuation(self):
        ticket = self.fixture(
            "continued = '-c' in sys.argv\n"
            "label = 'second' if continued else 'first'\n"
            "print(label + '-out', flush=True)\n"
            "print(label + '-err', file=sys.stderr, flush=True)\n"
            "if continued:\n"
            "    path = next(Path('chitty/tasks').glob('TASK-1--*.md'))\n"
            "    path.write_text(path.read_text().replace('status: doing', 'status: review'))\n"
            "    subprocess.run(['git', 'commit', '-qm', 'review', str(path)], check=True)\n"
        )["id"]
        result = self.run_cli("run", "--ticket", ticket)
        self.assertEqual(result.stdout, f"{ticket}: doing → review\n")
        self.assertEqual(
            self.one_log(result).splitlines(),
            ["first-out", "first-err", "second-out", "second-err"],
        )

    def test_timeout(self):
        ticket = self.fixture("print('timeout-marker', flush=True)\ntime.sleep(60)\n", timeout=2)[
            "id"
        ]
        result = self.run_cli("run", "--ticket", ticket)
        self.assertEqual(result.stdout, f"{ticket}: doing → error\n")
        self.assertIn("timed out", self.json("show", ticket)["notes"])
        self.assertEqual(self.one_log(result), "timeout-marker\n")

    def test_setup_failure(self):
        ticket = self.fixture("print('unexpected')\n", setup="false")["id"]
        result = self.run_cli("run", "--ticket", ticket)
        self.assertEqual(result.stdout, f"{ticket}: todo → error\n")
        self.assertIn("setup", self.json("show", ticket)["notes"])
        self.assertEqual(self.one_log(result), "")

    def check_creation_failure(self, *, collision: bool):
        ticket = self.fixture("print('unexpected')\n")
        folder = self.root / ".git/chitty/run"
        if not collision:
            # Keep the runner's own lock directory usable.
            folder /= "blocked"
        path = folder / "occupied.log"
        if collision:
            folder.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"keep me")
            sentinel = path
        else:
            folder.parent.mkdir(parents=True, exist_ok=True)
            folder.write_bytes(b"keep me")
            sentinel = folder
        head = self.git("rev-parse", "HEAD")
        task = Path(ticket["path"])
        before = task.read_bytes()
        with patch("chitty.run.log_path", return_value=path):
            result = self.run_cli("run", "--ticket", ticket["id"], exit_code=1)
        self.assertIn(str(path), result.stderr)
        self.assertFalse(any(line.startswith("log: ") for line in result.stderr.splitlines()))
        self.assertEqual(sentinel.read_bytes(), b"keep me")
        self.assertEqual(self.git("rev-parse", "HEAD"), head)
        self.assertEqual(task.read_bytes(), before)
        self.assertEqual(self.git("branch", "--list", "task-1"), "")
        self.assertFalse((self.root / ".worktrees/task-1").exists())

    def test_collision(self):
        self.check_creation_failure(collision=True)

    def test_blocked_parent(self):
        self.check_creation_failure(collision=False)
