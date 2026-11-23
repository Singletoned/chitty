---
title: Treat `/dev/stdin` and `/dev/fd/0` as stdin when refusing two stdin file options
status: planning
created: 2026-11-23
---

## Description

`_check_stdin_files` (`src/chitty/cli.py:235`) refuses two `-file` options that both read stdin, but it only recognises `-` (click names that stream `<stdin>`). A path that also reads stdin slips through. Seen 2026-11-23: `chitty edit TASK-568 --note-file - --summary-file /dev/stdin -s review <<'EOF'` stored the whole heredoc as the note, left Summary empty, and gave no warning.

Change: an option reads stdin when its value is `-`, `/dev/stdin`, `/dev/fd/0` or `/proc/self/fd/0`. Decide this in a small pure function, `reads_stdin(name: str) -> bool`, in `cli.py`, called by `_check_stdin_files` with each file's `name`. The error message is unchanged: `only one file option can read stdin: <options>`.

Callers today: `add` (`cli.py:319`), `note`/`add` paths at `cli.py:393`, and `edit` (`cli.py:776`). The guard runs before any read or write, so a refused command changes nothing.

Property tool: Hypothesis, with the `examples()` profile helper as in the existing tests in `tests/test_property_text_files.py`.

Out of scope: detecting other aliases of fd 0 (process substitution, other `/dev/fd/N`), and two options naming the same regular file, which reads correctly.

## Acceptance Criteria

- [ ] A Hypothesis property test in `tests/test_property_text_files.py` draws, for each of the five `chitty edit` file options, one of: absent, `-`, `/dev/stdin`, `/dev/fd/0`, or a regular temp file. It asserts that the edit exits 2 naming every stdin-reading option exactly when two or more options read stdin, and that the ticket file is then byte-for-byte unchanged; otherwise the edit succeeds. It fails on `main` today for a draw such as `--note-file -` with `--summary-file /dev/stdin`.
- [ ] `chitty add` with `--description-file /dev/stdin --note-file -` exits 2 and creates no ticket file (example test next to `test_two_stdin_options`).

## Notes

Suggestion origin: chitty

## History

- 2026-11-23T10:24:06Z witty-russet-gannet → backlog
- 2026-11-23T10:24:07Z witty-russet-gannet: changed notes
- 2026-11-23T10:28:51Z witty-russet-gannet: changed title, description, acceptance criteria
- 2026-11-23T10:28:51Z witty-russet-gannet backlog → planning
