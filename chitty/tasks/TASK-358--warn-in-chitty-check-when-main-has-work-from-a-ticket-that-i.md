---
title: Warn in `chitty check` when `main` has work from a ticket that is not done
status: cold-read
created: 2026-11-16
---

## Description

Seen 2026-11-16: `TASK-318` code reached `main` in `6a9e3ee` before the review that then failed it; and on 2026-11-22 `TASK-540`'s code reached `main` while its ticket said `error` (`TASK-555`). Make `chitty check` on `main` warn about every ticket whose implementation is on `main` while the ticket is not `done`. The managed `AGENTS.md` wording is a separate `untestable` ticket.

Measured on this repository's `main` on 2026-11-22: 345 ticket IDs have a non-`chitty: ` commit with a `Task:` trailer. Counting only commits that also change a path outside every ticket directory, exactly one is not `done` (`TASK-540`, `blocked`). Without the path rule, hand-written ticket-only commits (for example `206d7558`, "Refine TASK-70 into a waiting status") make `TASK-66`, `TASK-70` and `TASK-74` warn too; with neither rule, almost every ticket warns, because `chitty:` bookkeeping commits carry the trailer.

Decisions:

- A commit counts for a ticket when it is reachable from `main` (`--no-merges`), its subject does not start with `chitty: `, its `Task:` trailers name that ticket, and it changes at least one path outside every context directory (`has_work_beyond_tickets` in `src/chitty/run.py`; move it to `src/chitty/git.py`, next to `commits_missing_trailer`, and import it in `run.py`, so `check.py` does not import `run.py`).
- New pure function in `src/chitty/check.py`: `unfinished_landed(commits: Sequence[TrailerCommit], statuses: Mapping[TaskId, str], ticket_directories: Sequence[PurePosixPath]) -> dict[TaskId, str]`, returning for each counted ticket whose status is in `statuses` and is not `done` the SHA of the newest counted commit (`commits` is newest first). Tickets absent from `statuses` (deleted on archive) are ignored. `TrailerCommit` is a frozen dataclass in `src/chitty/git.py`: `sha: str`, `subject: str`, `task_ids: tuple[TaskId, ...]`, `paths: tuple[PurePosixPath, ...]`; trailer values that do not parse as a `TaskId` are dropped.
- New `git.trailer_commits(root: Path, ref: str) -> list[TrailerCommit]`, one `git log <ref> --no-merges --name-only` call with a format giving the SHA, subject and `%(trailers:key=Task,valueonly,separator=%x2C)`.
- `check()` adds, only when `include_worktree_state` is true and `git.current_branch(repo.root)` equals `repo.config.main_branch`, one warning per returned ticket, on the ticket's file path: `commit <first 10 characters of SHA> on <main> has work for <ID>, which is <status>`. Statuses come from the ticket files `check()` already parsed (archived tickets are `done`). Warnings do not change the exit code.
- Out of scope: commits on other branches; `chitty run` behaviour.

Tests in a new `tests/test_check_unfinished_landed.py`.

- Property with Hypothesis (the repository's property tool) on `unfinished_landed`: draw two to five ticket IDs, each with a status from `STATUSES` or absent; one to eight commits, each with a subject (drawn text, prefixed `chitty: ` or not), a subset of the IDs (plus sometimes an ID not among them), and paths drawn from `chitty/tasks/<name>.md`, `chitty/human/archive/<name>.md` and `src/<name>.py`. Ticket directories `chitty/tasks` and `chitty/human`. Expected, computed in the test from the drawn values by the rule above: the IDs with a counted commit and a non-`done` status, each mapped to the SHA of the first counted commit for it in list order.
- CLI examples inheriting `CliTestCase` from `tests/test_cli.py`, real Git on branch `main`: add `TASK-1` (status `todo`); commit `src/x.py` with message `Add x\n\nTask: TASK-1`.

## Acceptance Criteria

- [ ] The `unfinished_landed` property passes, and fails against a version that ignores the `chitty: ` subject rule and against one that ignores the path rule (commit both as mutant tests that assert the property fails)
- [ ] CLI: on `main`, `chitty check` exits 0 and prints the warning naming `TASK-1` and `todo`; with only a commit of `chitty/tasks/` files carrying the trailer, or a `chitty: ` commit of `src/x.py`, no warning; after `TASK-1` is moved to `done` (through `review`, with `--override-review-independence` as other CLI tests do), no warning; in a linked worktree on branch `task-1`, no warning
- [ ] `run.py` imports `has_work_beyond_tickets` from `chitty.git` and the existing runner tests pass; `make check` passes

## History

- 2026-11-16T10:29:29Z intrepid-coral-raven → backlog
- 2026-11-16T10:39:00Z intrepid-coral-raven backlog → planning
- 2026-11-22T09:55:33Z friendly-jade-stoat: changed title, description, acceptance criteria
- 2026-11-22T09:55:33Z friendly-jade-stoat planning → cold-read
