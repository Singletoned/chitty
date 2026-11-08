---
title: Add `--note-file` and stdin input for task text
status: review
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

A multi-paragraph file is one note, paragraphs kept. An empty or whitespace-only file fails as `--note ""` already does (`note must not be empty`, from `with_note` in `model.py`); keep that.

Also add `[--note-file F]` to the `chitty add` and `chitty edit` synopses in `PLAN.md` (around line 421), and mention it beside `--note TEXT` at line 305. No `__version__` bump: this is CLI-only, and `chitty init` writes nothing new.

## Acceptance Criteria

- [x] Tests show `chitty edit` and `chitty add` each storing a note read with `--note-file -` from standard input whose text contains backticks, unchanged
- [x] A test shows `--note a --note-file f` giving two notes in that order

## Plan

1. Add non-repeatable `--note-file` click options to `add` and `edit`, reading `click.File()` and appending the file content after repeated `--note` values before passing notes to the existing store/model path.
2. Add CLI regression tests covering stdin backticks for both commands and ordering of inline plus file notes.
3. Update the corresponding `PLAN.md` CLI synopsis and option documentation.
4. Run the focused tests, then `make format && make check`.

## Notes

Suggestion origin: circuitry

Cold read by a fresh Haiku subagent, 2026-11-07, kept as `refs/cold-read/TASK-67/1`. It built the ticket from the description alone: all three tests failed first (`No such option '--note-file'`), then passed, and `make check` passed. Outcomes:

- Fixed: the ticket did not say what an empty file does. It now keeps the existing `note must not be empty` error, as for `--note ""`.
- Fixed: a multi-paragraph file was unspecified. It is one note with paragraphs kept, which the reader confirmed; the description says so.
- Fixed: `PLAN.md`'s `chitty add` and `chitty edit` synopses list `--note` and needed `--note-file`; added to the description.
- Fixed: no `__version__` bump is needed, now stated.
- Rejected: a criterion for multi-paragraph files, because it goes through the same `with_note` path as `--note`, which already handles them.
- Rejected: naming the flag in the empty-file error, because the store-level message already matches `--note ""` and changing it is out of scope.
- No wrong claims found; none of these findings changes the design, so no second read.

Verified both stdin paths preserve backticks; inline notes precede file notes. `chitty fix` completed with unrelated existing Markdown delimiter warnings in other tasks.

## Summary

Implemented `--note-file` for `chitty add` and `chitty edit`, including stdin support and ordering after repeated `--note` values. Updated `PLAN.md` and added CLI regression tests. Verified focused tests and full `make format && make check`; no follow-ups.

## History

- 2026-11-01 → backlog
- 2026-11-07T09:16:07Z vivid-dormouse: changed description, acceptance criteria
- 2026-11-07T09:19:32Z vivid-dormouse: changed description, notes
- 2026-11-07T09:19:32Z vivid-dormouse backlog → todo
- 2026-11-08T10:12:22Z friendly-dormouse todo → doing
- 2026-11-08T10:12:44Z friendly-dormouse: wrote the plan
- 2026-11-08T10:15:54Z friendly-dormouse: changed notes, summary; ticked acceptance criteria
- 2026-11-08T10:15:54Z friendly-dormouse doing → review
