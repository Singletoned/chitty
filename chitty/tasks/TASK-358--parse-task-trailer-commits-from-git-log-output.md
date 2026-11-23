---
title: Parse `Task:` trailer commits from `git log` output
status: planning
created: 2026-11-16
---

## Description

Part of the `chitty check` warning for tickets whose work is on `main` while they are not `done` (seen 2026-11-16 with `TASK-318`, 2026-11-22 with `TASK-540`). Split 2026-11-22 after three cold reads: `TASK-572` decides which tickets landed unfinished; `TASK-571` adds the warning; `TASK-569` the guide wording. Split again 2026-11-23 after three more: this ticket is the pure parser; `TASK-YJ6VBS` runs `git log` and feeds it here.

Decisions, all in `src/chitty/git.py`:

- New frozen dataclass `TrailerCommit`: `sha: str`, `subject: str`, `task_ids: tuple[TaskId, ...]`, `paths: tuple[PurePosixPath, ...]`.
- New constant `TRAILER_LOG_FORMAT = "%x1e%H%x1f%s%x1f%(trailers:key=Task,valueonly,separator=%x2C)%x1f"`.
- New constant `TRAILER_LOG_OPTIONS = ("--root", "--no-show-signature", "--encoding=UTF-8", "--no-merges", "--no-renames", "--name-only", "-z", f"--format={TRAILER_LOG_FORMAT}")`, the options `TASK-YJ6VBS` passes to `git log`. Nothing runs Git in this ticket.
- New pure `parse_trailer_log(text: str) -> list[TrailerCommit]` for the output of `git log` with those options. That output is, per commit: `\x1e`, the 40-hex SHA, `\x1f`, the subject, `\x1f`, the comma-joined trailer values, `\x1f`, `\x00`; then, only when the commit changed paths, `\n` followed by each path and `\x00`. The last record has no trailing newline. Parse: split on `\x1e` (dropping the empty text before the first); in each record, a record with no `\x00` raises `ChittyError`; otherwise the header is the text up to the first `\x00`, and must split on `\x1f` into exactly four fields, the last empty; the rest, with one leading `\n` removed if present, is split on `\x00`, and its final entry must be empty and is dropped. Any record that does not fit (wrong field count, a SHA that is not 40 lowercase hex characters, an empty path, a non-empty final entry) raises `ChittyError` naming the record's SHA or its first 40 characters. So `\x1e` or `\x1f` in a subject or trailer, or `\x1e` in a path, fails loudly rather than mis-parsing (a `\x1e` mid-path splits the record; the fragment after it fails the four-field header check). A `\x1f`, newline or `\r` in a path is faithful (paths end at `\x00`) and is returned unchanged. Accepted limit: a path holding a complete forged header (`\x1e`, 40 hex, three `\x1f`) would parse as an extra commit; that is out of scope, as are SHA-256 repositories (64-hex SHAs). Trailer values are split on `,` and stripped; a value for which `TaskId.parse` raises `IdError` is dropped (catch `IdError` only).
- Nothing calls `parse_trailer_log` yet.

Tests in a new `tests/test_trailer_commits.py`, with Hypothesis (the repository's property tool). No Git is run.

- Round trip: generate lists of zero to five `TrailerCommit` values: 40-character SHAs from `0123456789abcdef`; subjects of printable text without `\x1e`, `\x1f`, NUL or newline and without leading or trailing whitespace (Git strips it); task IDs `TaskId("TASK", n)` and `TaskId("HUMAN", n)` with `n` from `st.integers(1, 10_000)`; zero to three paths per commit, each one to three parts joined by `/`, each part at least one character of text without `/`, NUL or `\x1e`, never `.` or `..` (which `PurePosixPath` would normalise), including spaces, quotes, `\x1f`, `\r`, newlines and non-ASCII, and some paths starting with `\n` (so removing more than one leading `\n` fails). Per commit, add zero to two junk trailer values from `st.sampled_from(["x", "TASK-", "TASK-1-2", "1"])` (none parses with `TaskId.parse`). Render each in exactly the byte layout above and assert `parse_trailer_log` returns the commits without the junk.
- Malformed input: for a rendered list holding one valid commit, each of these makes `parse_trailer_log` raise `ChittyError`: a `\x1f` inserted into its subject; a `\x1e` inserted into the middle of one of its paths (draw a commit with at least one path of two or more characters); an extra `\x00` after a path, making an empty path; the SHA with its last character dropped; the SHA with its last character replaced by `g`; the trailing `\x00` of the last path removed.
- Without `-z`: a rendered valid list with every `\x00` replaced by `\n` (as `git log` prints without `-z`) raises `ChittyError`, since it has no `\x00`.

## Acceptance Criteria

- [ ] The `parse_trailer_log` round-trip property passes
- [ ] The malformed-input and without-`-z` cases pass, each raising `ChittyError`; each fails when its rule is removed from the parser (no SHA check, empty paths kept, non-empty final entry dropped, field count unchecked). Record those runs in a note
- [ ] `make check` passes

## Plan

Implement the Git log parser and reader, add property and real-Git tests, and run the project checks.

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
- 2026-11-22T14:44:31Z kind-indigo-dormouse: wrote the plan
- 2026-11-22T14:44:41Z kind-indigo-dormouse: changed owner, notes
- 2026-11-22T14:44:41Z kind-indigo-dormouse doing → planning
- 2026-11-23T16:47:28Z witty-yellow-vole: replaced notes; changed owner, description
- 2026-11-23T16:47:39Z witty-yellow-vole planning → cold-read
- 2026-11-23T16:49:16Z witty-yellow-vole: changed description
- 2026-11-23T16:49:16Z witty-yellow-vole cold-read → planning
- 2026-11-23T16:49:51Z witty-yellow-vole planning → cold-read
- 2026-11-23T18:36:33Z witty-yellow-vole: changed description, acceptance criteria
- 2026-11-23T18:36:33Z witty-yellow-vole cold-read → planning
- 2026-11-23T18:36:52Z witty-yellow-vole planning → cold-read
- 2026-11-23T18:39:30Z witty-yellow-vole: changed title, description, acceptance criteria
- 2026-11-23T18:39:30Z witty-yellow-vole cold-read → planning
