---
title: Add the `to-plan` status and make returns go there
status: backlog
labels:
  - needs-minor
parent: TASK-10026
created: 2026-11-25
provisional: true
---

## Description

Part of `TASK-10026`. Today `planning` means both "waiting for a planner" and "a planner has it". This ticket adds `to-plan` for the first meaning and makes every return go there; `planning` is left for a planner's claim (enforced by `TASK-SYR88D`). Guide, prompt and doc wording is `TASK-MHMNG8`.

Change:

- `src/chitty/model.py`: add `to-plan` to `STATUSES` after `backlog`, to `Frontmatter.status`, and first in `DEFAULT_LIST_STATUSES`. Glyph `📥`, label `plan`; `planning` keeps `📝` and its label becomes `plnng` (labels are padded to 5 in `chitty list`). Add `to-plan` to the `Status` literal in `src/chitty/mcp.py`; update the default-status lists in the `list` description in `mcp.py` and the `--status` help in `src/chitty/cli.py`.
- `check_edit` in `src/chitty/store.py`, replacing `planning` with `to-plan` as the return status in: `returning_to_planning` and its "requires --note" message; the `is_review_transition` set; the fail-verdict requirement in `_validate_review_verdict` (`edit.status in {"doing", "planning"}`); and the owner clearing and `PLANNING_RETURN_LIMIT` escalation. The return count adds `("doing", "to-plan")` and `("review", "to-plan")` and keeps the two `planning` pairs, so returns recorded before this change still count. `doing` or `review` → `planning` is refused: ``return <ID> to `to-plan`; `planning` means a planner has taken it``. In `cli.py` `edit`, the `escalated` check uses `to-plan` instead of `planning`.
- `src/chitty/check.py`: the size and cold-read warnings that apply to `planning` also apply to `to-plan`.
- `scripts/retro.py`: add `to-plan` to `FAILED_REVIEW_TARGETS`.
- The status glyph and label rows in `README.md` and `docs/plan/cli.md` (`test_docs_list_both_statuses` in `tests/test_statuses_planning.py` reads them): add `📥 plan` for `to-plan` and change `planning` to `📝 plnng`, and update that test to match.

Out of scope: guides, prompts and docs (`TASK-MHMNG8`); refusing other actors' writes to a `planning` ticket; migrating existing `planning` tickets.

Tests: re-point the existing return tests (`tests/test_return_to_planning.py`, `tests/test_run_return_to_planning.py`, `test_planning_returns_escalate_since_last_block` in `tests/test_check_edit.py`, `test_third_planning_return_reports_escalation` in `tests/test_cli.py`, and other tests that return a ticket with `-s planning`) to `to-plan`, and update the `📝 plan` row expectations in `tests/test_cli.py` to the new labels. Add to `tests/test_return_to_planning.py` a property test, using Hypothesis as the file already does: for a previous status drawn from `doing` and `review`, any note text and any reviewer, an edit to `planning` raises `ChittyError` mentioning `to-plan`. Add one example where a history with one `doing → planning` and one `doing → to-plan` return makes the next `to-plan` return escalate (the count includes the current return, so this is the third). In `tests/test_statuses_planning.py`, with one `to-plan` and one `todo` ticket: `chitty list` with no status shows the `📥 plan` row, MCP `list` returns both, and `chitty next` picks the `todo` ticket.

## Acceptance Criteria

- [ ] The new property test (an edit from `doing` or `review` to `planning` is refused) and the mixed-history escalation example pass, and each fails before the change. Regression tests: the re-pointed return and escalation tests named above
- [ ] The `tests/test_statuses_planning.py` cases for a `to-plan` ticket pass, and fail before the change
- [ ] `make check` passes

## History

- 2026-11-25T23:05:55Z golden-coral-stoat → backlog
- 2026-11-25T23:06:21Z golden-coral-stoat: changed description, acceptance criteria
- 2026-11-25T23:09:23Z golden-coral-stoat: changed title, description
- 2026-11-25T23:09:25Z golden-coral-stoat: changed acceptance criteria
- 2026-11-25T23:09:42Z golden-coral-stoat: changed description
- 2026-11-25T23:10:53Z golden-coral-stoat: changed description
- 2026-11-25T23:12:14Z golden-coral-stoat: changed description
