import ast
import os
import stat
import subprocess
import sys

from tests.test_cli import CliTestCase

# argv: `fake-agent {mode} {id} {prompt} [-c ...]`. The fake edits the ticket
# named by argv[2], commits the edit, and logs its argv to the invocation log.
FAKE_AGENT = """#!{python}
import subprocess, sys
from pathlib import Path
with Path({log!r}).open("a") as stream:
    stream.write(repr(sys.argv[1:]) + "\\n")
ticket = sys.argv[2]
continued = "-c" in sys.argv[3:]
path = next(Path("chitty/tasks").glob(f"{{ticket}}--*.md"))
text = path.read_text()
{edit}
path.write_text(text)
subprocess.run(["git", "add", str(path)], check=True)
subprocess.run(["git", "commit", "--quiet", "--allow-empty", "-m", "agent"], check=True)
"""

# Acceptance criterion 1: the first session leaves the ticket in `doing`; a
# continued session moves it to `review`.
FINISH_WHEN_CONTINUED = """
if continued:
    text = text.replace('status: doing', 'status: review')
"""
# Acceptance criterion 3: a continued session sets the ticket to `blocked`.
BLOCK_WHEN_CONTINUED = """
if continued:
    text = text.replace('status: doing', 'status: blocked')
"""
# Acceptance criterion 2: the agent never changes the ticket.
NO_CHANGE = ""


class TestRunContinue(CliTestCase):
    def setUp(self):
        super().setUp()
        self.invocations = self.tmp / "invocations.log"
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace(
                "autocommit = false",
                'autocommit = true\nsetup = "true"',
            )
            .replace(
                'agent_command = "pi --chitty-{mode} {id}"',
                'agent_command = "fake-agent {mode} {id} {prompt}"',
            )
        )
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        self.bindir = self.tmp / "bin"
        self.bindir.mkdir()
        old_path = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{self.bindir}:{old_path}"
        self.addCleanup(os.environ.__setitem__, "PATH", old_path)

    def git(self, *args: str) -> None:
        subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)

    def write_fake(self, edit: str, name: str = "fake-agent") -> None:
        path = self.bindir / name
        path.write_text(
            FAKE_AGENT.format(python=sys.executable, log=str(self.invocations), edit=edit)
        )
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def invocations_seen(self) -> list[list[str]]:
        if not self.invocations.exists():
            return []
        return [ast.literal_eval(line) for line in self.invocations.read_text().splitlines()]

    def ticket(self) -> str:
        return self.json("add", "Continue ticket", "-d", "Description.", "-s", "todo")["id"]

    def test_continued_session_finishes_ticket_left_in_doing(self):
        ticket = self.ticket()
        self.write_fake(FINISH_WHEN_CONTINUED)
        self.run_cli("run", "--ticket", ticket)
        self.assertEqual(self.json("show", ticket)["status"], "review")
        seen = self.invocations_seen()
        self.assertEqual(len(seen), 2, seen)
        self.assertNotIn("-c", seen[0])
        self.assertEqual(seen[1][-1], "-c")
        self.assertIn("Continue working only on Chitty ticket " + ticket, seen[1][2])

    def test_unchanged_ticket_is_continued_five_times_then_fails(self):
        ticket = self.ticket()
        self.write_fake(NO_CHANGE)
        result = self.run_cli("run", "--ticket", ticket)
        self.assertEqual(result.stdout, f"{ticket}: todo → error\n")
        self.assertEqual(len(self.invocations_seen()), 6)

    def test_command_without_prompt_is_not_continued(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace(
                'agent_command = "fake-agent {mode} {id} {prompt}"',
                'agent_command = "fake-agent {mode} {id}"',
            )
        )
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "command without prompt")
        ticket = self.ticket()
        self.write_fake(NO_CHANGE)
        result = self.run_cli("run", "--ticket", ticket)
        self.assertEqual(result.stdout, f"{ticket}: todo → error\n")
        self.assertEqual(len(self.invocations_seen()), 1)

    def test_ticket_blocked_when_continued_ends_run_blocked(self):
        ticket = self.ticket()
        self.write_fake(BLOCK_WHEN_CONTINUED)
        self.run_cli("run", "--ticket", ticket)
        self.assertEqual(self.json("show", ticket)["status"], "blocked")
        self.assertEqual(len(self.invocations_seen()), 2)
