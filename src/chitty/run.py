"""Run Pi on Chitty's next action."""

import subprocess
from dataclasses import dataclass

from chitty.errors import ChittyError
from chitty.store import NextAction, Repo, next_action


class RunInterrupted(Exception):
    """The user interrupted Pi; the command must stop a shell loop."""


@dataclass(frozen=True)
class RunResult:
    action: NextAction
    old_status: str
    new_status: str


def run(repo: Repo) -> RunResult:
    """Run Pi with inherited streams and report its committed status change."""
    action = next_action(repo)
    old_status = repo.find(action.id).task.frontmatter.status
    try:
        completed = subprocess.run(
            ["pi", f"--chitty-{action.mode}", str(action.id)], cwd=repo.root, check=False
        )
    except FileNotFoundError:
        raise ChittyError("pi is not on PATH") from None
    except KeyboardInterrupt:
        raise RunInterrupted from None
    if completed.returncode:
        raise ChittyError(f"pi exited with status {completed.returncode}")
    # Pi commonly commits from a ticket worktree. Reopen so Repo's history cache sees it.
    new_status = Repo.open(repo.root).find(action.id).task.frontmatter.status
    if new_status == old_status:
        raise ChittyError(
            f"{action.id} was unchanged; only committed changes are visible to `chitty run`"
        )
    return RunResult(action, old_status, new_status)
