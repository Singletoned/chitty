---
title: Treat `/dev/stdin` and `/dev/fd/0` as stdin when refusing two stdin file options
status: review
created: 2026-11-23
---

## Description

`_check_stdin_files` (`src/chitty/cli.py:235`) refuses two `-file` options that both read stdin, but it only recognises `-` (click names that stream `<stdin>`). A path that also reads stdin slips through. Seen 2026-11-23: `chitty edit TASK-568 --note-file - --summary-file /dev/stdin -s review <<'EOF'` stored the whole heredoc as the note, left Summary empty, and gave no warning.

Change: decide in a small pure function, `reads_stdin(name: str) -> bool`, in `cli.py`, called by `_check_stdin_files` with each opened file's `name`. It receives click's `file.name`: `<stdin>` for `-`, the raw path otherwise (checked with click 8.5.0). It returns True for exactly `<stdin>`, `/dev/stdin`, `/dev/fd/0` and `/proc/self/fd/0`.

Test setup: `RepoTestCase` clears `CHITTY_ACTOR`, so set it (as `TestTextFiles.setUp` does) before `add`. A property draw with every option absent is excluded (`edit` refuses it with `nothing to change`): draw at least one present option.

Test hazard: click opens path options when it parses them (`File.convert`), so under `CliRunner` a `/dev/stdin` or `/dev/fd/0` option reads the test process's real fd 0, not the runner `input`; with `pytest -s` it can hang. Tests that pass these paths must point fd 0 at a temp file first (`os.dup2`) and restore it afterwards, and must not assert what such an option read. The error message is unchanged: `only one file option can read stdin: <options>`.

Callers today: `suggest` (`cli.py:319`), `add` (`cli.py:393`) and `edit` (`cli.py:776`). The guard runs before any read or write, so a refused command changes nothing.

Property tool: Hypothesis, with the `examples()` profile helper as in the existing tests in `tests/test_property_text_files.py`.

Out of scope: detecting other aliases of fd 0 (process substitution, other `/dev/fd/N`), and two options naming the same regular file, which reads correctly.

## Acceptance Criteria

- [ ] A Hypothesis property test in `tests/test_property_text_files.py` (a `RepoTestCase` with one ticket, `Path.cwd` patched as in `test_two_stdin_options`; inside each example, fd 0 is pointed at a temp file with `os.dup2` and restored in `finally`) draws, for each `chitty edit` file option except `--set-notes-file` (which `check_edit` refuses alongside `--note-file`), one of: absent, `-`, `/dev/stdin`, `/dev/fd/0`, or a regular temp file holding `text`. When two or more drawn values read stdin, it asserts exit code 2, an error naming every stdin-reading option, and the ticket file's bytes unchanged; otherwise exit code 0. It fails on `main` for a draw such as `--note-file -` with `--summary-file /dev/stdin`.
- [ ] `chitty add T --description-file /dev/stdin --note-file -` (fd 0 pointed at a temp file) exits 2, and the set of files under `chitty/tasks/` is unchanged. Example test next to `test_two_stdin_options`; it fails on `main`, where the ticket is created.
- [ ] A Hypothesis test of `reads_stdin` asserts True for each of the four names, and False for `st.text()` filtered to exclude them and for each of these near misses: `/dev/stdin/`, `/dev/fd/00`, `/dev/fd/0/`, `-`, `<stdin>x`, the empty string.

## Plan

Correct the add regression fixture, demonstrate baseline ticket creation, then run checks and return for review.

## Notes

Suggestion origin: chitty

Both regression tests failed before the fix: add created a ticket and edit accepted note stdin plus summary /dev/stdin.

Review failed (tests): Newly discovered: the add regression uses an empty fd 0, so it does not demonstrate the specified pre-fix ticket creation. Put valid description text in the temporary file and verify the baseline creates a ticket.
1: pass - make check: 1148 passed; baseline test_edit_stdin_aliases: 0 != 2 for [None, None, '-', '/dev/stdin'].
2: fail - Baseline test_add_stdin_alias printed exit 1, not 2: Description text changed section boundaries; use ### for headings and close code fences. The required pre-fix creation is not exercised.
3: pass - make check passed; baseline test_reads_stdin with an old-behaviour shim failed on /dev/stdin. The shim is necessary because main has no reads_stdin function.
Baseline tests ran with the branch test file in a temporary merge-base worktree, PYTHONPATH pointing at its src, and the old-behaviour shim; the worktree was removed.

With valid description in fd 0, the add regression fails against the old stdin predicate with exit 0 and output confirming TASK-1 was added. With the fix, make check passes: 1148 tests.

## Summary

Corrected the add regression fixture and confirmed baseline ticket creation; make check passes.

## History

- 2026-11-23T10:24:06Z witty-russet-gannet → backlog
- 2026-11-23T10:24:07Z witty-russet-gannet: changed notes
- 2026-11-23T10:28:51Z witty-russet-gannet: changed title, description, acceptance criteria
- 2026-11-23T10:28:51Z witty-russet-gannet backlog → planning
- 2026-11-23T10:29:05Z witty-russet-gannet: changed description
- 2026-11-23T10:29:05Z witty-russet-gannet planning → cold-read
- 2026-11-23T10:32:40Z witty-russet-gannet: changed description, acceptance criteria
- 2026-11-23T10:32:40Z witty-russet-gannet cold-read → planning
- 2026-11-23T10:32:42Z witty-russet-gannet planning → cold-read
- 2026-11-23T10:33:47Z witty-russet-gannet: changed acceptance criteria
- 2026-11-23T10:33:47Z witty-russet-gannet cold-read → planning
- 2026-11-23T10:33:50Z witty-russet-gannet planning → cold-read
- 2026-11-23T10:35:00Z witty-russet-gannet: changed description
- 2026-11-23T10:35:00Z witty-russet-gannet cold-read → planning
- 2026-11-23T10:35:02Z witty-russet-gannet planning → todo
- 2026-11-23T11:14:38Z lively-navy-ibis todo → doing
- 2026-11-23T11:17:10Z lively-navy-ibis: wrote the plan
- 2026-11-23T11:17:36Z lively-navy-ibis: changed notes
- 2026-11-23T11:24:50Z lively-navy-ibis: changed summary
- 2026-11-23T11:24:50Z lively-navy-ibis doing → review
- 2026-11-23T11:30:29Z friendly-hazel-wren: changed acceptance criteria, notes
- 2026-11-23T11:30:29Z friendly-hazel-wren review → doing
- 2026-11-23T11:38:14Z jolly-fawn-raven: wrote the plan
- 2026-11-23T11:42:01Z jolly-fawn-raven: changed notes, summary
- 2026-11-23T11:42:01Z jolly-fawn-raven doing → review
