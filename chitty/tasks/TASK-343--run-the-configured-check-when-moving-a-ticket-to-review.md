---
title: Run the configured check when moving a ticket to review
status: todo
labels:
  - needs-minor
depends_on:
  - TASK-342
created: 2026-11-16
---

## Description

`src/chitty/roles/work.md` tells workers to run `chitty fix`, format and check before `-s review`. `chitty run` already runs the configured check before a review session, so a forgotten check costs a whole session. Make `chitty edit -s review` run the configured check and refuse on failure, then shorten the guide.

Decisions:

- Run the check in `Repo.edit` in `src/chitty/store.py` only when entering review (`edit.status == "review"` and the previous status is not `review`), in a git checkout, and without `skip_current_version`. Not on `review` to `done`, although the existing uncommitted-changes refusal also covers that. It runs after that refusal passes, in `Repo.root`. So the CLI and MCP both get it, and the runner's repair path (which sets `review` with `skip_current_version=True` from the main checkout) does not run it. A ticket with no branch entering review from the main checkout runs it there, like the existing refusal.
- After a passing check, refuse with the same uncommitted-changes message if the worktree now has uncommitted files (a check that formats or writes files), then call `self._require_current_version(stored)` again, because the check may take minutes.
- No `check` configured: nothing runs and the edit proceeds. `check` is optional outside `chitty run`, which already requires it.
- In a work session the runner runs the check before the agent, and the agent's `-s review` runs it again. That double cost is accepted.
- Add a new module `src/chitty/commands.py`, which must not import `run.py` or `store.py`. Move into it, unchanged apart from the names: `_command_environment` from `src/chitty/run.py` as `command_environment()`, and `_code_block` as `code_block()`. `run.py` imports both and keeps no function of either old name; `_setup`, `_landing_check` and the other callers use the import.
- Add to `commands.py` a frozen dataclass `CheckFailure(detail: str, exited: bool)` and `run_check(root: Path, command: str) -> CheckFailure | None`. It runs `shlex.split(command)` in `root` with stdin closed, stdout and stderr merged, and `command_environment()`. Exit 0 gives `None`. Another exit status gives `exited=True` and the detail `check exited with status <N>:` followed by `code_block` of the output, or of `(no output)` when it is empty. A missing command gives `exited=False` and `check command not found: <command>`. `KeyboardInterrupt` propagates.
- `_run_check` in `src/chitty/run.py` keeps its signature (`tests/test_run_environment.py` calls it with a `Mock`) and its `Running check in ...` line on stderr. It calls `run_check`, maps `KeyboardInterrupt` to `RunInterrupted("check")` as now, and passes `detail` and `exited` to `_handle_check_failure`.
- On failure `Repo.edit` raises `ChittyError` starting `cannot move <ID> to review; check failed:` followed by the detail. Nothing is written or committed. Ctrl-C during the check writes nothing either.
- Do not run `chitty fix`: every Chitty write already runs it on the ticket it writes, and it repairs only ticket files.
- In `work.md`, replace ``run `chitty fix`, format and check, then commit your changes: `chitty edit -s review` refuses while the worktree has uncommitted files.`` (the text after `TASK-342`) with ``format and commit your changes: `chitty edit -s review` runs the configured check and refuses if it fails or the worktree has uncommitted files.``

`needs-minor`: `chitty edit -s review` now refuses in any repository whose configured check fails.

Tests go in a new `tests/test_review_check.py`, with classes inheriting `ReviewMergeTestCase` from `tests/test_review_merge.py` for its git helpers. Its `setUp` replaces `check` with a landing-check script, so each new test writes its own `check` line into `chitty.toml` (and commits it on `main` before branching). Use a Python script run with `sys.executable`, as `tests/test_next.py` does near line 1281. No property tests: the outcomes are the fixed set listed in the criteria, each tested, and each needs a real subprocess and git repository; `code_block` moves unchanged.

## Acceptance Criteria

- [ ] On branch `task-1` with `TASK-1` in `doing`, a check script that prints `boom` and exits 3 makes `chitty edit 1 -s review` exit 1 with output containing `check failed`, `status 3` and `boom`; `TASK-1` stays `doing` and `git log` gains no commit. Fails before the change.
- [ ] With `check` naming a command that does not exist, `chitty edit 1 -s review` exits 1 with `check command not found`. With a check script that exits 0 after creating `made.txt`, it exits 1 and lists `made.txt`. Both leave `TASK-1` in `doing`.
- [ ] Guards, which pass before the change too: with `check = "true"`, and with no `check` line in `chitty.toml`, `chitty edit 1 -s review` moves `TASK-1` to `review`. With a failing check script that writes a marker file outside the repository, a direct `Repo.edit` with `Edit(status="review", skip_current_version=True)` moves `TASK-1` to `review`, and `review` to `done` (with a `Reviewed:` note and verdict lines, as `tests/test_review_merge.py` does) succeeds; the marker is never written.
- [ ] `_run_check` in `src/chitty/run.py` calls `run_check` from `src/chitty/commands.py`; `run.py` defines neither `_command_environment` nor `_code_block`; `commands.py` imports neither `chitty.run` nor `chitty.store`; and the existing runner check tests in `tests/test_next.py` and `tests/test_run_environment.py` pass unchanged.
- [ ] The `work.md` sentence is replaced as the Description says, and `tests/test_guide_work_commits.py` asserts `runs the configured check and refuses if it fails` in place of `then commit your changes` and `refuses while the worktree has uncommitted files`. `make check` passes.

## History

- 2026-11-16T09:59:52Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:34Z intrepid-coral-raven backlog → planning
- 2026-11-17T16:34:09Z kind-umber-toad: changed dependencies, description, acceptance criteria
- 2026-11-17T16:34:09Z kind-umber-toad planning → cold-read
- 2026-11-17T17:06:38Z kind-umber-toad: changed title, labels, description, acceptance criteria
- 2026-11-17T17:06:38Z kind-umber-toad cold-read → planning
- 2026-11-17T17:07:45Z kind-umber-toad planning → todo
