---
title: Find active tickets whose `Task:` commits landed work while they are not done
status: doing
depends_on:
  - TASK-358
created: 2026-11-22
---

## Description

`TASK-358` has landed `TrailerCommit` in `src/chitty/git.py` (`trailer_commits`, which runs Git, is `TASK-YJ6VBS`; this ticket does not need it). Using it, add the pure rule that picks the tickets whose work is on `main` while they are not `done`. `TASK-571` then calls it from `chitty check`. Split from `TASK-358` on 2026-11-22.

Measured on `main` on 2026-11-22: about 340 ticket IDs have a non-`chitty: ` commit with a `Task:` trailer. Counting only commits that also change a path outside every ticket directory, and only active tickets, one is not `done` (`TASK-540`). Without the path rule, hand-written ticket-only commits (for example `206d7558`) count too; without the subject rule almost every ticket counts, because `chitty:` bookkeeping commits carry the trailer.

Decisions:

- Move `has_work_beyond_tickets` from `src/chitty/run.py` to `src/chitty/git.py`, next to `commits_missing_trailer`; import it from there in `run.py` and in `tests/test_property_repair_work.py` (no re-export; drop the `Iterable` import from `run.py` if nothing else uses it, and add `Iterable` to the `collections.abc` import in `git.py`). It uses `PurePosixPath.is_relative_to`, so `chitty/tasksX/a.md` is not inside `chitty/tasks`.
- New pure function in `src/chitty/check.py`: `unfinished_landed(commits: Sequence[TrailerCommit], statuses: Mapping[TaskId, str], ticket_directories: Sequence[PurePosixPath]) -> dict[TaskId, str]`. A commit counts for a ticket when its subject does not start with `chitty: `, its `task_ids` include that ticket, and `has_work_beyond_tickets(commit.paths, ticket_directories)` is true. Return, for each ticket in `statuses` whose status is not `done` and that has a counted commit, the SHA of the first counted commit for it in list order. Tickets absent from `statuses` are ignored. Nothing calls it yet.

Tests in a new `tests/test_unfinished_landed.py`, Hypothesis (the repository's property tool). Draw two to five distinct ticket IDs `TaskId("TASK", n)` with `n` from `st.integers(1, 12)`, each with a status from `STATUSES` (in `src/chitty/model.py`) or absent from `statuses`; one to eight commits, each with a distinct 40-hex SHA, a subject (`st.text(alphabet="abc :", max_size=8)`, prefixed `chitty: ` or not), a subset of the IDs plus sometimes one ID `TaskId("TASK", n)` with `n` from `st.integers(100, 103)` (disjoint from the drawn IDs), and zero to three paths, each `<name>` from `st.text(alphabet="abc", min_size=1, max_size=3)`, from `chitty/tasks/<name>.md`, `chitty/human/archive/<name>.md`, `chitty/backlog/<name>.md`, `chitty/tasksX/<name>.md` and `src/<name>.py`; ticket directories `chitty/tasks`, `chitty/human` and `chitty/backlog`. A helper `landed_mismatch(function, commits, statuses) -> str | None` compares a function's result with the expected value computed in the test from the drawn values by the rule above, using `is_relative_to` for the path rule. Mutant tests call `hypothesis.find` (with `settings(max_examples=200, deadline=None, database=None)`) with wrong versions written in the test file (one that also counts `chitty: ` commits, one that ignores the path rule, one that uses `str.startswith` on paths) and assert a mismatching case is found. These mutant tests show the generator can tell the rule apart from plausible wrong versions; they never call `unfinished_landed`, so they need no failure-before evidence. Red first: add `unfinished_landed` raising `NotImplementedError`, run the property and record its failure in a note, then implement it.

## Acceptance Criteria

- [ ] The `unfinished_landed` property passes, and all three mutant tests find a mismatching case
- [ ] `run.py` and `tests/test_property_repair_work.py` import `has_work_beyond_tickets` from `chitty.git`, `chitty.run` no longer defines it, and `tests/test_property_repair_work.py` passes; `make check` passes

## Plan

Move the existing path helper, add the specified property and mutants with a red-first stub, then implement the pure rule and run checks.

## Notes

Planner, 2026-11-23: `TASK-358` landed `TrailerCommit` as this ticket assumes; cold-read against what landed.

Red first: the unfinished landed property failed with NotImplementedError against the stub.

## History

- 2026-11-22T10:03:13Z friendly-jade-stoat → todo
- 2026-11-22T10:03:32Z friendly-jade-stoat: changed description, acceptance criteria
- 2026-11-22T10:03:32Z friendly-jade-stoat todo → planning
- 2026-11-22T10:09:52Z friendly-jade-stoat planning → cold-read
- 2026-11-22T10:11:21Z friendly-jade-stoat: changed description, notes
- 2026-11-22T10:11:21Z friendly-jade-stoat cold-read → planning
- 2026-11-23T19:28:34Z witty-yellow-vole planning → cold-read
- 2026-11-23T19:37:43Z witty-yellow-vole: changed description
- 2026-11-23T19:37:43Z witty-yellow-vole cold-read → planning
- 2026-11-23T19:38:57Z witty-yellow-vole: replaced notes
- 2026-11-23T19:38:57Z witty-yellow-vole planning → cold-read
- 2026-11-23T19:39:44Z witty-yellow-vole cold-read → todo
- 2026-11-23T19:40:20Z witty-yellow-vole: changed description, acceptance criteria
- 2026-11-23T19:40:20Z witty-yellow-vole todo → planning
- 2026-11-23T19:40:23Z witty-yellow-vole planning → todo
- 2026-11-23T19:44:41Z brisk-jade-dormouse todo → doing
- 2026-11-23T19:47:15Z brisk-jade-dormouse: wrote the plan
- 2026-11-23T19:47:54Z brisk-jade-dormouse: changed notes
