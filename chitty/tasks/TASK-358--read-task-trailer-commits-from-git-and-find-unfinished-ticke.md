---
title: Read `Task:` trailer commits from Git and find unfinished tickets they landed
status: planning
created: 2026-11-16
---

## Description

Seen 2026-11-16: `TASK-318` code reached `main` in `6a9e3ee` before the review that then failed it; and on 2026-11-22 `TASK-540`'s code reached `main` while its ticket said `error` (`TASK-555`). The goal is a `chitty check` warning on `main` for every active ticket whose implementation is on `main` while the ticket is not `done`. Split 2026-11-22 after two cold reads: this ticket adds the pure pieces and the Git reader; `TASK-571` wires the warning into `check()`; the managed guide wording is `TASK-569`.

Measured on `main` on 2026-11-22: about 340 ticket IDs have a non-`chitty: ` commit with a `Task:` trailer. Counting only commits that also change a path outside every ticket directory, and only active (not archived) tickets, one is not `done` (`TASK-540`). Without the path rule, hand-written ticket-only commits (for example `206d7558`, "Refine TASK-70 into a waiting status") count too; without the subject rule almost every ticket counts, because `chitty:` bookkeeping commits carry the trailer.

Decisions:

- A commit counts for a ticket when its subject does not start with `chitty: `, its `Task:` trailers name that ticket, and it changes at least one path outside every ticket directory. Move `has_work_beyond_tickets` from `src/chitty/run.py` to `src/chitty/git.py`, next to `commits_missing_trailer`; import it from there in `run.py` and in `tests/test_property_repair_work.py` (no re-export).
- New frozen dataclass `TrailerCommit` in `src/chitty/git.py`: `sha: str`, `subject: str`, `task_ids: tuple[TaskId, ...]`, `paths: tuple[PurePosixPath, ...]`.
- New constant `TRAILER_LOG_FORMAT = "%x1e%H%x1f%s%x1f%(trailers:key=Task,valueonly,separator=%x2C)%x1f"` and pure `parse_trailer_log(text: str) -> list[TrailerCommit]` in `git.py`, parsing the output of `git log --no-merges --name-only -z --format=<TRAILER_LOG_FORMAT>`: records start at `\x1e`; the header's fields are split on `\x1f`; the names follow as NUL-separated entries, with the newline Git puts after the header stripped and empty entries dropped. Trailer values that do not parse with `TaskId.parse` are dropped. `-z` matters: without it Git quotes names with special characters (`"chitty/tasks/TASK-1 \303\274.md"`).
- New `trailer_commits(root: Path, ref: str) -> list[TrailerCommit]` in `git.py`: one `git log <ref>` call with those options, parsed by `parse_trailer_log`; newest first, as Git prints.
- New pure function in `src/chitty/check.py`: `unfinished_landed(commits: Sequence[TrailerCommit], statuses: Mapping[TaskId, str], ticket_directories: Sequence[PurePosixPath]) -> dict[TaskId, str]`, returning, for each ticket in `statuses` whose status is not `done` and that has a counted commit, the SHA of the first counted commit for it in list order. Tickets absent from `statuses` are ignored. Nothing calls it yet.

Tests in a new `tests/test_trailer_commits.py`, with Hypothesis (the repository's property tool).

- Round trip: generate a list of `TrailerCommit` values (40-hex SHAs, subjects without `\x1e`, `\x1f`, NUL or newline, task IDs from `TaskId("TASK", n)` and `TaskId("HUMAN", n)`, paths of one to three parts drawn from text without `/`, NUL or `\x1e`, including spaces, quotes and non-ASCII) plus, per commit, zero to two junk trailer values that are not task IDs. Render each in exactly the shape Git prints (header, `\0\n`, then each name followed by `\0`; a commit with no paths has none) and assert `parse_trailer_log` gives the commits back without the junk.
- One real-Git example: a repository with three commits (one with two `Task:` trailers, one whose only path is `chitty/tasks/TASK-1 ü "q".md`, one `chitty: ` commit), compared field by field with `trailer_commits(root, "main")`.
- `unfinished_landed` property: draw two to five ticket IDs, each with a status from `STATUSES` or absent; one to eight commits, each with a subject (drawn text, prefixed `chitty: ` or not), a subset of the IDs plus sometimes one not among them, and paths from `chitty/tasks/<name>.md`, `chitty/human/archive/<name>.md`, `chitty/backlog/<name>.md` and `src/<name>.py`; ticket directories `chitty/tasks`, `chitty/human` and `chitty/backlog`. A helper `landed_mismatch(function, commits, statuses) -> str | None` compares a function's result with the expected value computed in the test by the rule above. Mutant tests call `hypothesis.find` with wrong versions written in the test file (one that also counts `chitty: ` commits, one that ignores the path rule) and assert a mismatching case is found.

## Acceptance Criteria

- [ ] The `parse_trailer_log` round-trip property and the real-Git `trailer_commits` example pass; the example fails if `-z` is dropped from the `git log` call (commit that variant as a mutant test asserting the comparison fails)
- [ ] The `unfinished_landed` property passes, and both mutant tests find a mismatching case
- [ ] `run.py` and `tests/test_property_repair_work.py` import `has_work_beyond_tickets` from `chitty.git`, and the existing runner tests pass; `make check` passes

## History

- 2026-11-16T10:29:29Z intrepid-coral-raven → backlog
- 2026-11-16T10:39:00Z intrepid-coral-raven backlog → planning
- 2026-11-22T09:55:33Z friendly-jade-stoat: changed title, description, acceptance criteria
- 2026-11-22T09:55:33Z friendly-jade-stoat planning → cold-read
- 2026-11-22T09:58:39Z friendly-jade-stoat: changed description, acceptance criteria
- 2026-11-22T09:58:39Z friendly-jade-stoat cold-read → planning
- 2026-11-22T09:58:40Z friendly-jade-stoat planning → cold-read
- 2026-11-22T10:01:13Z friendly-jade-stoat: changed title, description, acceptance criteria
- 2026-11-22T10:01:13Z friendly-jade-stoat cold-read → planning
