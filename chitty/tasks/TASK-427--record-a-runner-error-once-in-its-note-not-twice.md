---
title: Record a runner error once in its note, not twice
status: doing
priority: medium
depends_on:
  - TASK-426
created: 2026-11-19
---

## Description

Starts after `TASK-426`. `_record_ticket_error` in `src/chitty/run.py` writes every runner error twice: in the first line, `Runner error (<phase>): <error>`, and again in a fenced `Error output:` block. A multi-line error, such as an agent's output or a Git hint, therefore appears twice in the note.

Decisions:

- New pure function `_runner_error_note(phase: str, error: str, worktree: Path) -> str`, which `_record_ticket_error` uses for its note. With `lines = error.splitlines() or [""]`:
  - the note starts `Runner error (<phase>): <lines[0]>`, then a blank line and `` Worktree: `<worktree>` `` as today;
  - only when some line in `lines[1:]` is not blank, a blank line, `Error output:` and `_code_block("\n".join(lines[1:]))` follow. Otherwise there is no block (`"a\n"` and `"a\n\n"` give none).
  - The first line stays unfenced, as today (accepted: runner error first lines are short status messages).

Tests. No change to the earlier tickets' tests.

- Property in a new `tests/test_property_runner_error_note.py`: generate `phase` from `st.sampled_from(("setup", "review preparation", "check", "agent", "landing"))` and `error` from `st.text()` with newlines, `\r\n`, backtick runs and the literal strings `Error output:` and `Runner error` mixed in (for example `st.lists(st.one_of(st.text(), st.sampled_from(("\n", "\r\n", "\r", "\x85", "\u2028", "```", "Error output:", "Runner error"))))` joined). Compare whole strings, never `note.splitlines()`: with `head = f"Runner error ({phase}): {lines[0]}\n\nWorktree: `{worktree}`"`, the note equals `head` when every line in `lines[1:]` is blank, else `head + "\n\nError output:\n" + _code_block("\n".join(lines[1:]))`.
- `tests/test_run_errors_on_branch.py`: make `assert_branch_error` return `tip`. In `test_agent_failure_keeps_error_and_message_on_branch`, the fake agent prints `AGENT_LINE_1` and `AGENT_LINE_2` on separate lines before `raise SystemExit(7)`. With `tip` returned: `tip.count(s) == 1` for each of `Runner error (agent): agent exited with status 7:`, `AGENT_LINE_1` and `AGENT_LINE_2`, and `tip.index("Error output:") < tip.index("AGENT_LINE_1")`. The first count already holds on the old code; the `AGENT_LINE` counts are what fail there (each appears twice).
- In `test_work_setup_failure_is_only_recorded_on_branch`: `tip.count("setup exited with status 1") == 1` and `Error output:` is not in `tip`. This is the end-to-end check of the one-line case; it relies on `TASK-426`, after which the setup error is one line.

## Acceptance Criteria

- [ ] The property and the changed assertions pass; the `AGENT_LINE` counts and the setup count fail against the parent commit of this change, named by hash in the notes; `make check` passes

## Plan

Add the specified property and branch regression assertions, confirm the branch tests fail on the parent, then extract the note formatter and run formatting and checks.

## Notes

Cold read 2026-11-19 outcomes: lines split with `splitlines()`; a pure `_runner_error_note` with a property; `assert_branch_error` returns `tip`; exact count and order assertions; the setup count guards against repeating the line under another heading.

Second cold read 2026-11-19 outcomes: whole-string comparison in the property; lone `\r`, `\x85` and `\u2028` generated; the `review preparation` phase; no block when the remaining lines are blank; first line stays unfenced; fails-before names the parent hash.

## History

- 2026-11-19T17:28:50Z quick-ginger-lapwing → planning
- 2026-11-19T17:31:30Z quick-ginger-lapwing: changed description, acceptance criteria, notes
- 2026-11-19T17:34:16Z quick-ginger-lapwing: changed description, acceptance criteria, notes
- 2026-11-19T17:34:24Z quick-ginger-lapwing planning → todo
- 2026-11-21T10:51:58Z quick-maroon-falcon todo → doing
- 2026-11-21T10:54:02Z quick-maroon-falcon: wrote the plan
