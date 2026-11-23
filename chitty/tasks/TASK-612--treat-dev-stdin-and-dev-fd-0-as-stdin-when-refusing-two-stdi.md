---
title: Treat `/dev/stdin` and `/dev/fd/0` as stdin when refusing two stdin file options
status: cold-read
created: 2026-11-23
---

## Description

`_check_stdin_files` (`src/chitty/cli.py:235`) refuses two `-file` options that both read stdin, but it only recognises `-` (click names that stream `<stdin>`). A path that also reads stdin slips through. Seen 2026-11-23: `chitty edit TASK-568 --note-file - --summary-file /dev/stdin -s review <<'EOF'` stored the whole heredoc as the note, left Summary empty, and gave no warning.

Change: decide in a small pure function, `reads_stdin(name: str) -> bool`, in `cli.py`, called by `_check_stdin_files` with each opened file's `name`. It receives click's `file.name`: `<stdin>` for `-`, the raw path otherwise (checked with click 8.5.0). It returns True for exactly `<stdin>`, `/dev/stdin`, `/dev/fd/0` and `/proc/self/fd/0`.

Test hazard: click opens path options when it parses them (`File.convert`), so under `CliRunner` a `/dev/stdin` or `/dev/fd/0` option reads the test process's real fd 0, not the runner `input`; with `pytest -s` it can hang. Tests that pass these paths must point fd 0 at a temp file first (`os.dup2`) and restore it afterwards, and must not assert what such an option read. The error message is unchanged: `only one file option can read stdin: <options>`.

Callers today: `suggest` (`cli.py:319`), `add` (`cli.py:393`) and `edit` (`cli.py:776`). The guard runs before any read or write, so a refused command changes nothing.

Property tool: Hypothesis, with the `examples()` profile helper as in the existing tests in `tests/test_property_text_files.py`.

Out of scope: detecting other aliases of fd 0 (process substitution, other `/dev/fd/N`), and two options naming the same regular file, which reads correctly.

## Acceptance Criteria

- [ ] A Hypothesis property test in `tests/test_property_text_files.py` (a `RepoTestCase` with one ticket, `Path.cwd` patched as in `test_two_stdin_options`, fd 0 pointed at a temp file as described) draws, for each of the five `chitty edit` file options, one of: absent, `-`, `/dev/stdin`, `/dev/fd/0`, or a regular temp file. When two or more drawn values read stdin, it asserts exit code 2, an error naming every stdin-reading option, and the ticket file's bytes unchanged; otherwise it asserts exit code 0. It fails on `main` for a draw such as `--note-file -` with `--summary-file /dev/stdin`.
- [ ] `chitty add T --description-file /dev/stdin --note-file -` (fd 0 pointed at a temp file) exits 2, and the set of files under `chitty/tasks/` is unchanged. Example test next to `test_two_stdin_options`; it fails on `main`, where the ticket is created.
- [ ] A Hypothesis test of `reads_stdin` asserts True for each of the four names and False for any other drawn text, including near misses such as `/dev/stdin/`, `/dev/fd/00` and `-`.

## Notes

Suggestion origin: chitty

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
