---
title: Give every long text option of add, edit and suggest a file form
status: planning
created: 2026-11-16
---

## Description

Agents pass long ticket text as shell arguments, and the guides spend a paragraph each on quoting backticks and apostrophes. `chitty edit` has `--description-file`, `--plan-file`, `--note-file` and `--set-notes-file`. Their `click.File()` type already reads stdin for `-`, but only `--note-file` says so. `chitty add` has only `--note-file`, `chitty edit` has no `--summary-file`, and `chitty suggest` has only `-d`, so long text goes through `-d "$(cat file)"` (seen 2026-11-12 on `TASK-302` and 2026-11-17).

Decisions:

- Add `--description-file` to `chitty add` and `chitty suggest`, and `--summary-file` to `chitty edit`, each `type=click.File()`, combined with its text option through `_text` in `src/chitty/cli.py`, so giving both is the existing usage error.
- Every `-file` option of `add`, `edit` and `suggest` says `('-' for stdin)` in its help.
- Two `-file` options in one command both given `-` is a `click.UsageError` naming them, because only the first would get the text.
- `--ac` and `--set-ac` get no file form: criteria are one line each.
- `cli.py` stays thin: no change to `store.py`, `mcp.py` or `inbox.py`.
- Replace the quoting paragraph (the two lines starting `Backticks run commands inside double-quoted shell arguments`) in `src/chitty/guide.md`, `src/chitty/roles/work.md`, `review.md` and `plan.md` with one line: ``Pass text containing backticks or apostrophes through a `-file` option, using `-` and a quoted heredoc (`<<'EOF'`) for stdin.`` Update `tests/test_guide_backticks.py` to that line, and `tests/fixtures/guide-before-workflow.md` only if a test fails without it. Do not change `AGENTS.md` on the branch: after this lands, the main checkout's `chitty init` refreshes the managed block, and the planning session updates the hand-written copy in the `## Chitty` section.
- `TASK-306` (`--description-file` for `chitty add`) is superseded and gets archived by the planning session when this lands.

Tests: a Hypothesis property in a new `tests/test_property_text_files.py`, using Click's `CliRunner` as `tests/test_cli.py` does: for any text, without NUL or carriage return, that has non-whitespace content, each text option and its `-file` form (a file and `-` with that stdin) write the same ticket file. It covers `add -d`, `add --note`, `edit -d`, `--plan`, `--note`, `--set-notes` and `--summary`. Example tests in the same file: `suggest --description-file -` sends the same suggestion as `-d`, and two `-` options are refused naming both.

Out of scope: MCP, file forms for criteria or titles, and reading files relative to anything but the working directory.

## Acceptance Criteria

- [ ] The Hypothesis property in `tests/test_property_text_files.py` shows each listed text option and its `-file` form, from a file and from `-`, write the same ticket; it fails before the change for the options that have no file form yet
- [ ] `suggest --description-file -` sends the same suggestion as `-d`, and giving `-` to two `-file` options exits with a usage error naming both; the tests fail before the change
- [ ] The four guides carry the one-line file advice in place of the quoting paragraph, every `-file` help says `(-` for stdin`)`, and `make check` passes

## History

- 2026-11-16T09:59:58Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:41Z intrepid-coral-raven backlog → planning
- 2026-11-17T17:52:25Z kind-umber-toad: changed title, description
- 2026-11-17T19:59:02Z kind-umber-toad: changed title, description, acceptance criteria
