---
title: Record a runner error once in its note, not twice
status: planning
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
  - only when `len(lines) > 1`, a blank line, `Error output:` and `_code_block("\n".join(lines[1:]))` follow. A one-line error has no block.

Tests. No change to the earlier tickets' tests.

- Property in a new `tests/test_property_runner_error_note.py`: generate `phase` from `st.sampled_from(("check", "setup", "agent", "landing"))` and `error` from `st.text()` with newlines, `\r\n`, backtick runs and the literal strings `Error output:` and `Runner error` mixed in (for example `st.lists(st.one_of(st.text(), st.sampled_from(("\n", "\r\n", "```", "Error output:", "Runner error"))))` joined). Assert: the note's first line equals `f"Runner error ({phase}): {lines[0]}"`; when `len(lines) == 1`, the note equals the first line, a blank line and the `Worktree:` line, nothing more; otherwise the note ends with `"Error output:\n" + _code_block("\n".join(lines[1:]))`.
- `tests/test_run_errors_on_branch.py`: make `assert_branch_error` return `tip`. In `test_agent_failure_keeps_error_and_message_on_branch`, the fake agent prints `AGENT_LINE_1` and `AGENT_LINE_2` on separate lines before `raise SystemExit(7)`. With `tip` returned: `tip.count(s) == 1` for each of `Runner error (agent): agent exited with status 7:`, `AGENT_LINE_1` and `AGENT_LINE_2`, and `tip.index("Error output:") < tip.index("AGENT_LINE_1")`. The first count already holds on the old code; the `AGENT_LINE` counts are what fail there (each appears twice).
- In `test_work_setup_failure_is_only_recorded_on_branch`: `tip.count("setup exited with status 1") == 1` and `Error output:` is not in `tip`. This is the end-to-end check of the one-line case; it relies on `TASK-426`, after which the setup error is one line.

## Acceptance Criteria

- [ ] The property and the changed assertions pass; the `AGENT_LINE` counts and the setup count fail against the `run.py` of the parent of this change (recorded in the notes); `make check` passes

## Notes

Cold read 2026-11-19 outcomes: lines split with `splitlines()`; a pure `_runner_error_note` with a property; `assert_branch_error` returns `tip`; exact count and order assertions; the setup count guards against repeating the line under another heading.

## History

- 2026-11-19T17:28:50Z quick-ginger-lapwing → planning
- 2026-11-19T17:31:30Z quick-ginger-lapwing: changed description, acceptance criteria, notes
