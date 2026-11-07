---
title: Add `--note-file` and stdin input for task text
status: backlog
created: 2026-11-01
---

## Description

Text passed on the command line in double quotes loses anything in backticks, because the shell runs it as a command. In `circuitry` (commit `90a902f`, `CIRCUIT-67`, 2026-10-29) a reviewer's `--note "... `chitty list --all` reports ..."` pasted the full output of `chitty list --all`, 75 lines, into the note, and other backticked words vanished. Chitty's own guidance asks for backticks around code, so agents hit this often. `TASK-68` adds a guidance line about single quotes. This ticket gives agents a way to pass a note with no shell quoting at all.

Add `--note-file` to `chitty edit` and `chitty add` in `src/chitty/cli.py`, like `--description-file` and `--plan-file` on `edit`:

- `type=click.File()`, so `--note-file -` reads standard input, as `--description-file -` already does.
- Not repeatable. Its text is appended as one more note after any `--note` values, so `--note a --note-file f` gives two notes, `a` first.
- Help text: `Read a note from a file ('-' for stdin).`

This stays in `cli.py`: it only turns a file into one more entry in the existing `notes` tuple passed to `Edit` and to `add`. Nothing changes in `store.py`, `model.py` or `mcp.py`.

Out of scope: `--summary-file`, `--ac-file`, `chitty note`, the MCP server (it takes strings, so has no shell quoting problem), and guidance changes (`TASK-68`).

## Acceptance Criteria

- [ ] Tests show `chitty edit` and `chitty add` each storing a note read with `--note-file -` from standard input whose text contains backticks, unchanged
- [ ] A test shows `--note a --note-file f` giving two notes in that order

## Notes

Suggestion origin: circuitry

## History

- 2026-11-01 → backlog
- 2026-11-07T09:16:07Z vivid-dormouse: changed description, acceptance criteria
