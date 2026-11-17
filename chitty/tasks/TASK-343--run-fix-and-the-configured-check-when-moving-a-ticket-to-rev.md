---
title: Run fix and the configured check when moving a ticket to review
status: cold-read
depends_on:
  - TASK-342
created: 2026-11-16
---

## Description

`src/chitty/roles/work.md` tells workers to run `chitty fix`, format and check before `-s review`. `chitty run` already runs the configured check before a review session, so a forgotten check costs a whole session. Make `chitty edit -s review` run the configured check and refuse on failure, then shorten the guide.

Decisions:

- Run the check in `Repo.edit` in `src/chitty/store.py`, under exactly the condition of the existing uncommitted-changes refusal: entering review from another status, in a git checkout, without `skip_current_version`. It runs after that refusal passes, in `Repo.root`. So the CLI and MCP both get it, and the runner's repair path (which sets `review` with `skip_current_version=True` from the main checkout) does not run it.
- No `check` configured: nothing runs and the edit proceeds. `check` is optional outside `chitty run`, which already requires it.
- Add a new module `src/chitty/commands.py` holding `command_environment()` (moved from `_command_environment` in `src/chitty/run.py`, which then imports it) and `run_check(root: Path, command: str) -> str | None`. `run_check` runs `shlex.split(command)` in `root` with stdin closed, stdout and stderr merged, and returns `None` on exit 0, otherwise the failure text: `check exited with status <N>:` and the output in a fenced block, or `check command not found: <command>`. `_run_check` in `src/chitty/run.py` calls it instead of its own `subprocess.run`, keeping its `KeyboardInterrupt` handling.
- On failure `Repo.edit` raises `ChittyError` starting `cannot move <ID> to review; check failed:` followed by the failure text. Nothing is written or committed.
- After a passing check, if the worktree now has uncommitted files (a check that formats or writes files), refuse with the same uncommitted-changes message as before the check.
- Do not run `chitty fix`: every Chitty write already runs it on the ticket it writes, and it repairs only ticket files.
- In `work.md`, replace ``run `chitty fix`, format and check, then commit your changes: `chitty edit -s review` refuses while the worktree has uncommitted files.`` (the text after `TASK-342`) with ``format and commit your changes: `chitty edit -s review` runs the configured check and refuses if it fails or the worktree has uncommitted files.``

Tests go in a new `tests/test_review_check.py`, with classes inheriting `ReviewMergeTestCase` from `tests/test_review_merge.py` (git helpers; config `check = "true"`), following `test_dirty_branch_cannot_enter_review_until_committed`. Set the check to a Python script with `sys.executable`, as `tests/test_next.py` does near line 1281. No property tests: the outcomes are the fixed set listed in the criteria, each tested, and each needs a real subprocess and git repository.

## Acceptance Criteria

- [ ] On branch `task-1` with `TASK-1` in `doing`, a check script that prints `boom` and exits 3 makes `chitty edit 1 -s review` exit 1 with output containing `check failed`, `status 3` and `boom`; `TASK-1` stays `doing` and `git log` gains no commit. Fails on `main`.
- [ ] With `check` naming a command that does not exist, `chitty edit 1 -s review` exits 1 with `check command not found`. With a check script that exits 0 after creating `made.txt`, it exits 1 and lists `made.txt`. Both leave `TASK-1` in `doing`.
- [ ] With `check = "true"`, and with no `check` line in `chitty.toml`, `chitty edit 1 -s review` moves `TASK-1` to `review`. A direct `Repo.edit` with `Edit(status="review", skip_current_version=True)` and a failing check script also moves it to `review`, and the script (which writes a marker file outside the repository) never runs.
- [ ] `_run_check` in `src/chitty/run.py` calls `run_check` from `src/chitty/commands.py`, `run.py` has no `_command_environment` of its own, and the existing runner check tests in `tests/test_next.py` pass unchanged.
- [ ] The `work.md` sentence is replaced as the Description says, and `tests/test_guide_work_commits.py` asserts `runs the configured check and refuses if it fails`. `make check` passes.

## History

- 2026-11-16T09:59:52Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:34Z intrepid-coral-raven backlog → planning
- 2026-11-17T16:34:09Z kind-umber-toad: changed dependencies, description, acceptance criteria
- 2026-11-17T16:34:09Z kind-umber-toad planning → cold-read
