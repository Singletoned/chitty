---
title: Read `Task:` trailer commits from Git
status: doing
created: 2026-11-16
---

## Description

Part of the `chitty check` warning for tickets whose work is on `main` while they are not `done` (seen 2026-11-16 with `TASK-318`, 2026-11-22 with `TASK-540`). Split 2026-11-22 after three cold reads: this ticket reads `Task:` trailer commits from Git; `TASK-572` decides which tickets they landed unfinished; `TASK-571` adds the warning; `TASK-569` the guide wording.

Decisions, all in `src/chitty/git.py`:

- New frozen dataclass `TrailerCommit`: `sha: str`, `subject: str`, `task_ids: tuple[TaskId, ...]`, `paths: tuple[PurePosixPath, ...]`.
- New constant `TRAILER_LOG_FORMAT = "%x1e%H%x1f%s%x1f%(trailers:key=Task,valueonly,separator=%x2C)%x1f"`.
- New pure `parse_trailer_log(text: str) -> list[TrailerCommit]` for the output of `git log --no-merges --no-renames --name-only -z --format=<TRAILER_LOG_FORMAT>`. That output is, per commit: `\x1e`, the 40-hex SHA, `\x1f`, the subject, `\x1f`, the comma-joined trailer values, `\x1f`, `\x00`; then, only when the commit changed paths, `\n` followed by each path and `\x00`. The last record has no trailing newline. Parse: split on `\x1e` (dropping the empty text before the first); in each record, a record with no `\x00` raises `ChittyError`; otherwise the header is the text up to the first `\x00`, and must split on `\x1f` into exactly four fields, the last empty; the rest, with one leading `\n` removed if present, is split on `\x00`, dropping only the final empty entry. Any record that does not fit (wrong field count, a SHA that is not 40 lowercase hex characters, an empty path) raises `ChittyError` naming the record's SHA or its first 40 characters: real history with `\x1e` or `\x1f` in a subject, trailer or path fails loudly rather than mis-parsing. Trailer values are split on `,` and stripped; a value for which `TaskId.parse` raises `IdError` is dropped (catch `IdError` only).
- New `trailer_commits(root: Path, ref: str) -> list[TrailerCommit]`: one `git log <ref>` call with those options (`--no-renames`, so a file moved from `src/` into `chitty/tasks/` lists both paths), parsed by `parse_trailer_log`; newest first, as Git prints.
- Nothing calls `trailer_commits` yet.

Tests in a new `tests/test_trailer_commits.py`, with Hypothesis (the repository's property tool).

- Round trip: generate lists of zero to five `TrailerCommit` values: 40-hex SHAs; subjects of printable text without `\x1e`, `\x1f`, NUL or newline and without leading or trailing whitespace (Git strips it); task IDs `TaskId("TASK", n)` and `TaskId("HUMAN", n)` with `n` from `st.integers(1, 10_000)`; zero to three paths per commit, each one to three parts, each part at least one character of text without `/`, NUL, newline, `\x1e` or `\x1f`, including spaces, quotes and non-ASCII. Per commit, add zero to two junk trailer values from `st.sampled_from(["x", "TASK-", "TASK-1-2", "1"])` (none parses with `TaskId.parse`). Render each in exactly the byte layout above and assert `parse_trailer_log` returns the commits without the junk.
- Malformed input: for a rendered valid commit, inserting a `\x1f` into its subject, or a `\x1e` into one of its paths, makes `parse_trailer_log` raise `ChittyError`. SHA-256 repositories (64-hex SHAs) are out of scope.
- Real Git: a repository with three commits on `main` (one with two `Task:` trailers changing `src/a.py`, one whose only path is `chitty/tasks/TASK-1 ü "q".md`, one with subject `chitty: edit TASK-1` and no change, via `--allow-empty`). Assert the exact text `git log` prints with the options above (bytes compared with the expected layout) and that `trailer_commits(root, "main")` returns the expected three commits field by field. Mutant check: the test runs the same `git log` command without `-z` itself, feeds the output to `parse_trailer_log`, and asserts `parse_trailer_log` raises `ChittyError` (it does: without `-z` there is no `\x00` and the fourth header field is not empty).

## Acceptance Criteria

- [ ] The `parse_trailer_log` round-trip and malformed-input properties pass
- [ ] The real-Git example passes: the exact `git log` bytes match the layout, `trailer_commits` returns the three commits, and the same command without `-z` makes `parse_trailer_log` raise `ChittyError`
- [ ] `make check` passes

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
- 2026-11-22T10:01:28Z friendly-jade-stoat planning → cold-read
- 2026-11-22T10:03:33Z friendly-jade-stoat: changed title, description, acceptance criteria
- 2026-11-22T10:03:33Z friendly-jade-stoat cold-read → planning
- 2026-11-22T10:03:37Z friendly-jade-stoat planning → cold-read
- 2026-11-22T10:09:43Z friendly-jade-stoat: changed description, acceptance criteria
- 2026-11-22T10:09:43Z friendly-jade-stoat cold-read → planning
- 2026-11-22T10:09:44Z friendly-jade-stoat planning → todo
- 2026-11-22T14:41:19Z kind-indigo-dormouse todo → doing
