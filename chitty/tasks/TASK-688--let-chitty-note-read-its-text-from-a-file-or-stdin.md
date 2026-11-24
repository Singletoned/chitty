---
title: Let `chitty note` read its text from a file or stdin
status: doing
created: 2026-11-24
---

## Description

### Why

The managed `AGENTS.md` block tells agents to pass text containing backticks or apostrophes through a `-file` option, using `-` and a quoted heredoc. `chitty note ID TEXT` has no such option, so on 2026-11-23 an agent ran `chitty note TASK-557 --file -`, got `No such option '--file'`, and had to find `chitty edit ID --note-file -` instead.

### Change

In `src/chitty/cli.py`, `note` (around line 883):

- Make the `text` argument optional (`required=False`, default `None`).
- Add `--file`, `type=click.File(encoding="utf-8")`, help `Read TEXT from a file ('-' for stdin).`, like `--note-file` on `edit`.
- Exactly one of TEXT and `--file` must be given; otherwise raise `click.UsageError("give TEXT or --file, not both")` when both are given, or `click.UsageError("give TEXT or --file")` when neither is. Check this before writing anything. An empty or whitespace-only file keeps today's `note must not be empty` error.
- Then call `repo.edit(..., Edit(note=text))` as today, with the text read from the file when `--file` is given.

Decided: do not reuse `_text` (`cli.py`, around line 252). Its message names `--<name>` and `--<name>-file`, which does not fit a positional TEXT; write the check inline in `note`.

Decided: the option is `--file`, the name the agent tried and the name the `AGENTS.md` advice suggests, not `--text-file`. A TEXT of `-` stays literal text, as today, so no existing call changes meaning.

The MCP `note` tool already takes its text as a value; it does not change. Behaviour stays in `store.py`; this is a thin CLI change.

### Tests

The property follows `compare_option` in `tests/test_property_text_files.py`, which already runs inline, file and stdin modes for `add` and `edit` with Hypothesis and the `TEXT` strategy. `compare_option` builds `option + "-file"`, which does not fit `note`, so write a separate helper or test for `note`: in each temporary repository create the ticket with `add T -d x --json`, then run `note` on that ID, and import `escape_literal_asterisks` from `chitty.markdown`. Put the usage-error test in `TestEdit` in `tests/test_cli.py`, whose `setUp` creates ticket 1. Hypothesis is this repository's property-testing tool. The usage-error test needs no property: it has two fixed cases, both listed. It must assert the exact messages. Click already prints `Usage: chitty note [OPTIONS] ID TEXT` and `No such option '--file'` today, so checking only for `TEXT` and `--file` would pass with nothing built.

### Out of scope

Changing `edit --note-file`, the MCP tools, or the `AGENTS.md` wording; TEXT that starts with `-` (Click reads it as an option today, and still will).

## Acceptance Criteria

- [ ] In `tests/test_property_text_files.py`, a new property test shows that for any text drawn from `TEXT`, `chitty note ID TEXT`, `chitty note ID --file <path>` and `chitty note ID --file -` (text on stdin), each on a fresh ticket, give equal Notes in `chitty show --json`, and those Notes split into the same words as the stored form of the text: `notes.split() == escape_literal_asterisks(text).split()` (`chitty.markdown`; Chitty escapes `*` and strips trailing whitespace, so exact equality does not hold). A fixed case shows `chitty note ID -` stores the note `-`. The property fails without the change.
- [ ] A new test in `tests/test_cli.py` shows `chitty note 1 Text --file <path>` exits with status 2 and output containing `give TEXT or --file, not both`, and `chitty note 1` exits with status 2 and output containing `give TEXT or --file`; both leave the ticket file byte-for-byte unchanged. `test_note_appends_a_note` still passes, and `make check` passes.

## Plan

-

## Notes

Suggestion origin: chitty

## History

- 2026-11-24T22:21:50Z zesty-coral-newt → backlog
- 2026-11-24T22:21:51Z zesty-coral-newt: changed notes
- 2026-11-24T22:50:14Z zesty-coral-newt: changed title, description, acceptance criteria
- 2026-11-24T22:50:14Z zesty-coral-newt backlog → planning
- 2026-11-24T22:50:18Z zesty-coral-newt planning → cold-read
- 2026-11-24T22:51:22Z zesty-coral-newt: changed description, acceptance criteria
- 2026-11-24T22:51:51Z zesty-coral-newt: changed acceptance criteria
- 2026-11-24T22:54:38Z zesty-coral-newt: changed acceptance criteria
- 2026-11-24T22:55:40Z zesty-coral-newt: changed description
- 2026-11-24T22:55:40Z zesty-coral-newt cold-read → todo
- 2026-11-24T23:54:25Z eager-indigo-vole todo → doing
- 2026-11-24T23:58:04Z eager-indigo-vole: wrote the plan
