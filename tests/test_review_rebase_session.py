import json
import sys
from pathlib import Path
from unittest import mock

from chitty.git import rebase_in_progress
from chitty.run import RunInterrupted
from chitty.store import Repo
from tests.test_review_merge import ReviewMergeTestCase

# The timeout case (exit code 124) uses a short limit and an agent that sleeps
# far past it. Every other case runs with no limit (`0`), so it cannot time out
# however slowly the machine runs.
TIMEOUT_CASE_SECONDS = 1
NO_LIMIT = 0


class TestReviewRebaseSession(ReviewMergeTestCase):
    def configure_rebase_agent(self, exit_code: int, finish: bool, dirty: bool) -> None:
        timeout = TIMEOUT_CASE_SECONDS if exit_code == 124 else NO_LIMIT
        script = self.tmp / "rebase-agent.py"
        script.write_text(
            "import subprocess, sys, time\n"
            "from pathlib import Path\n"
            "mode = sys.argv[1]\n"
            "print(mode + '-stdout', flush=True)\n"
            "print(mode + '-stderr', file=sys.stderr, flush=True)\n"
            f"exit_code = {exit_code}\n"
            f"finish = {finish!r}\n"
            f"dirty = {dirty!r}\n"
            f"log = Path({str(self.tmp / 'agent.log')!r})\n"
            "if mode == 'rebase':\n"
            "    task = next(Path('chitty/tasks').glob('TASK-1--*.md'))\n"
            f"    Path({str(self.tmp / 'ticket-start')!r}).write_bytes(task.read_bytes())\n"
            f"    Path({str(self.tmp / 'prompt')!r}).write_text(sys.argv[3])\n"
            "    log.open('a').write('rebase ' + repr(sys.argv[4:]) + '\\n')\n"
            "    if finish:\n"
            "        subprocess.run(['git', 'add', 'shared.txt'], check=True)\n"
            "        subprocess.run(\n"
            "            ['git', '-c', 'core.editor=true', 'rebase', '--continue'], check=True\n"
            "        )\n"
            "    if dirty:\n"
            "        Path('leftover.txt').write_text('uncommitted')\n"
            "    if exit_code == 124:\n"
            "        time.sleep(60)\n"
            "    if finish:\n"
            f"        Path({str(self.tmp / 'ticket-end')!r}).write_bytes(task.read_bytes())\n"
            "    raise SystemExit(0 if exit_code == 124 else exit_code)\n"
            "log.open('a').write('review ' + repr(sys.argv[4:]) + '\\n')\n"
            "task = next(Path('chitty/tasks').glob('TASK-1--*.md'))\n"
            "task.write_text(task.read_text().replace('status: review', 'status: done'))\n"
            "subprocess.run(['git', 'add', str(task)], check=True)\n"
            "subprocess.run(['git', 'commit', '-m', 'review'], check=True)\n"
        )
        (self.tmp / "agent.log").write_text("")
        config = self.root / "chitty.toml"
        text = config.read_text()
        start = text.index("agent_command = ")
        end = text.index("\n", start)
        text = (
            text[:start]
            + f'agent_command = "{sys.executable} {script} '
            + '{mode} {id} {prompt}"'
            + text[end:]
        )
        text = text.replace(
            "[contexts.tasks]",
            'rebase_model = "cheap/model"\nreview_model = "review-model"\n'
            f"agent_timeout = {timeout}\n\n[contexts.tasks]",
        )
        config.write_text(text)

    def branch_ticket_before_conflict(self):
        self.git("switch", "--quiet", "-c", "task-1")
        self.run_cli("edit", "1", "-s", "doing")
        self.run_cli("edit", "1", "-s", "review")
        (self.root / "work.txt").write_text("work\\n")
        (self.root / "shared.txt").write_text("branch\\n")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "conflicting code work")
        self.git("switch", "--quiet", "main")

    def run_conflicted_review(self, exit_code: int, finish: bool, dirty: bool):
        self.configure_rebase_agent(exit_code, finish, dirty)
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "configure test agent")
        self.branch_ticket_before_conflict()
        self.move_main(shared="main\n")
        result = self.run_cli("run", "--mode", "review", exit_code=0)
        repo = Repo.open(self.worktree if self.worktree.exists() else self.root)
        return result, repo.find(repo.resolve("1")).task

    def test_successful_rebase_session_precedes_reviewer_and_logs_mode(self):
        result, _ = self.run_conflicted_review(0, True, False)
        logs = [
            line.removeprefix("log: ")
            for line in result.stderr.splitlines()
            if line.startswith("log: ")
        ]
        self.assertEqual(len(logs), 1, result.stderr)
        path = self.root / Path(logs[0])
        self.assertEqual(list((self.root / ".git/chitty/run").glob("*.log")), [path])
        markers = {"rebase-stdout", "rebase-stderr", "review-stdout", "review-stderr"}
        self.assertEqual(
            [line for line in path.read_text().splitlines() if line in markers],
            ["rebase-stdout", "rebase-stderr", "review-stdout", "review-stderr"],
        )
        starts = (self.tmp / "agent.log").read_text().splitlines()
        self.assertEqual(len(starts), 2)
        self.assertTrue(starts[0].startswith("rebase "))
        self.assertTrue(starts[1].startswith("review "))
        self.assertIn("A rebase onto the integration branch", (self.tmp / "prompt").read_text())
        self.assertEqual(
            (self.tmp / "ticket-start").read_bytes(), (self.tmp / "ticket-end").read_bytes()
        )
        self.assertIn("--model", starts[0])
        self.assertIn("cheap/model", starts[0])
        self.assertIn("review-model", starts[1])
        usage = self.tmp / "data" / "chitty" / "usage" / "repo.jsonl"
        records = [json.loads(line) for line in usage.read_text().splitlines()]
        rebase_record = next(record for record in records if record["mode"] == "rebase")
        self.assertEqual(rebase_record["status_before"], "review")
        self.assertEqual(rebase_record["status_after"], "review")
        self.assertGreaterEqual(rebase_record["seconds"], 0)

    def test_rebase_command_requires_prompt(self):
        self.configure_rebase_agent(0, True, False)
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace(" {prompt}", ""))
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "remove agent prompt")
        self.branch_ticket_before_conflict()
        self.move_main(shared="main\n")
        self.run_cli("run", "--mode", "review")
        repo = Repo.open(self.worktree)
        task = repo.find(repo.resolve("1")).task
        self.assertEqual(task.frontmatter.status, "doing")
        self.assertIn("the rebase session needs {prompt}", task.section("Notes") or "")
        self.assertFalse((self.tmp / "agent.log").read_text())

    def test_interrupt_aborts_rebase_without_starting_reviewer(self):
        self.configure_rebase_agent(0, True, False)
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "configure test agent")
        self.branch_ticket_before_conflict()
        self.move_main(shared="main\\n")

        def interrupt(*args, **kwargs):
            raise RunInterrupted("agent")

        with mock.patch("chitty.run._run_session", side_effect=interrupt):
            result = self.run_cli("run", "--mode", "review", exit_code=130)
        self.assertIn("interrupted during rebase", result.stderr)
        self.assertFalse(rebase_in_progress(self.worktree))
        self.assertEqual(self.ticket().frontmatter.status, "review")
        self.assertFalse((self.tmp / "agent.log").read_text())

    def assert_failed_outcome(self, exit_code: int, finish: bool, dirty: bool):
        _, task = self.run_conflicted_review(exit_code, finish, dirty)
        self.assertEqual(task.frontmatter.status, "doing")
        note = task.section("Notes") or ""
        self.assertIn("Review failed (integration)", note)
        self.assertIn("`shared.txt`", note)
        if exit_code == 0 and finish and dirty:
            self.assertIn("`leftover.txt`", note)
        elif exit_code == 0 and not finish:
            self.assertIn("rebase still in progress", note)
        elif exit_code == 1:
            self.assertIn("agent exited with status 1:", note)
        elif exit_code == 124:
            self.assertIn(f"agent timed out after {TIMEOUT_CASE_SECONDS} seconds:", note)
        starts = (self.tmp / "agent.log").read_text().splitlines()
        self.assertFalse([start for start in starts if start.startswith("review ")])
        if exit_code != 124:
            # A timed-out agent may be killed before it logs its start.
            self.assertEqual(len(starts), 1)
        self.assert_no_rebase_in_progress()


def _failure_test(exit_code: int, finish: bool, dirty: bool):
    def test(self):
        self.assert_failed_outcome(exit_code, finish, dirty)

    return test


for _exit, _finished, _dirty in (
    (0, False, False),
    (0, False, True),
    (0, True, True),
    (1, False, False),
    (1, False, True),
    (1, True, False),
    (1, True, True),
    (124, False, False),
    (124, False, True),
    (124, True, False),
    (124, True, True),
):
    _name = f"test_exit_{_exit}_finish_{_finished}_dirty_{_dirty}"
    setattr(TestReviewRebaseSession, _name, _failure_test(_exit, _finished, _dirty))
