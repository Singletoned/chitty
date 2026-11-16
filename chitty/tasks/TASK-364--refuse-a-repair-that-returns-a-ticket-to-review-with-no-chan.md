---
title: Refuse a repair that returns a ticket to review with no change beyond its ticket files
status: cold-read
owner: open-russet-eel
created: 2026-11-16
---

## Description

A repair agent can end an `error` ticket in `review` with nothing to review. Every `chitty edit` autocommits, so "the branch has commits beyond `main`" is satisfied by the agent's own status change; and for a ticket whose branch was missing (`TASK-326`), `_worktree` creates a fresh branch from `main`. Seen by the `TASK-326` cold read: a repair that only ran `chitty edit 1 -s review` printed `TASK-1: error → review`.

Refuse that. When a repair session ends with the ticket in `review`, and the branch changes no file outside the configured context directories compared with its merge base with `main` (committed changes only), raise `RepairError` with the text `repair agent returned <ID> to review with no change beyond its ticket files` before the final `main_repo.edit` in `_run_session` (around the `if repairing:` block in `src/chitty/run.py`), so the ticket stays `error`. A repair ending in `blocked` is unaffected.

Put the decision in a pure function in `src/chitty/run.py`:

`has_work_beyond_tickets(changed_paths: Iterable[PurePosixPath], ticket_directories: Iterable[PurePosixPath]) -> bool`

true when some changed path is outside every ticket directory. Add a git helper in `src/chitty/git.py` returning the paths a branch changes since its merge base with another (`git diff --name-only <base>...<branch>`).

Existing repair tests that end in `review` with a ticket-only commit must give the branch a real change, for example by committing a code file in the fake agent: `test_run_check_failure_on_error_ticket_starts_repair_agent` in `tests/test_next.py` and the repair test near line 2374 of the same file.

Files: `src/chitty/run.py`, `src/chitty/git.py`, `tests/test_next.py`, new `tests/test_property_repair_work.py` and `tests/test_repair_requires_work.py`.

## Acceptance Criteria

- [ ] Hypothesis property in `tests/test_property_repair_work.py`: for any generated sets of relative POSIX paths and ticket directories, `has_work_beyond_tickets` is true exactly when some path is not inside any ticket directory (a path equal to a directory, or under it, counts as inside). Generate paths that are inside, outside, prefix-alike (`chitty/tasksX/a.md` against `chitty/tasks`) and empty sets. Fails before the change (the function does not exist yet: first add it raising `NotImplementedError`, so the test fails by assertion).
- [ ] Fake-agent tests in `tests/test_repair_requires_work.py`, one subtest per case, on an `error` ticket whose branch has no change beyond `main` at the start: the agent sets `review` through `chitty edit` only; writes `status: review` to the ticket file without committing; commits a code file then sets `review`; sets `blocked`. Only the code-file case ends in `review`; the first two make `chitty run --errors` exit non-zero with the `RepairError` text and leave the ticket `error`; `blocked` ends in `blocked`. The first case fails before the change. Updated `tests/test_next.py` repair tests pass. `make check` passes.

## History

- 2026-11-16T17:08:51Z open-russet-eel → planning
- 2026-11-16T17:09:05Z open-russet-eel: changed owner
- 2026-11-16T17:09:05Z open-russet-eel planning → cold-read
