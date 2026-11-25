---
title: Add the `to-plan` status and send worker and reviewer returns there
status: backlog
labels:
  - needs-minor
parent: TASK-10026
created: 2026-11-25
provisional: true
---

## Description

Part of `TASK-10026`. Today `planning` means both "waiting for a planner" and "a planner has it". This ticket adds `to-plan` for the first meaning and sends every return there; `planning` is left for a planner's claim (enforced in a later ticket).

Change:

- `src/chitty/model.py`: add `to-plan` to `STATUSES` after `backlog`, to `Frontmatter.status`, and first in `DEFAULT_LIST_STATUSES`. Glyph `📥`, label `plan`; `planning` keeps `📝` and its label becomes `plnng` (labels are padded to 5 in `chitty list`). Add `to-plan` to the `Status` literal in `src/chitty/mcp.py` and the `--status` help in `src/chitty/cli.py`.
- `check_edit` in `src/chitty/store.py`: every rule for a return (`doing` or `review` → `planning`) now applies to `doing` or `review` → `to-plan`: the required note, clearing `owner`, the review verdict rules (`is_review_transition`, `_validate_review_verdict`), and `PLANNING_RETURN_LIMIT`. The return count adds `("doing", "to-plan")` and `("review", "to-plan")` to the pairs it counts and keeps the `planning` pairs, so returns recorded before this change still count. `doing` or `review` → `planning` is refused: `return <ID> to \`to-plan\`; \`planning\` means a planner has taken it`. In `cli.py` `edit`, the `escalated` check uses `to-plan` instead of `planning`.
- `src/chitty/check.py`: the size and cold-read warnings that apply to `planning` also apply to `to-plan`.
- Text, replacing `planning` with `to-plan` where it names the return status, with no other wording change: the `work` and `review` continuation prompts in `src/chitty/run.py`, `src/chitty/roles/work.md`, `src/chitty/roles/review.md`, `src/chitty/guide-runner.md`, and the status list in `docs/plan/task-file.md`. Do not edit the managed block in `AGENTS.md`; `chitty init` refreshes it after landing.

Out of scope: refusing other actors' writes to a `planning` ticket, migrating existing `planning` tickets, and `src/chitty/roles/plan.md` (later tickets under `TASK-10026`).

Tests: re-point the existing return tests (`tests/test_return_to_planning.py`, `tests/test_run_return_to_planning.py`, `test_planning_returns_escalate_since_last_block` in `tests/test_check_edit.py`, `test_third_planning_return_reports_escalation` in `tests/test_cli.py`, and other tests that return a ticket with `-s planning`) to `to-plan`. In `tests/test_statuses_planning.py`, cover `to-plan` alongside `planning` and `cold-read`. Add to `tests/test_return_to_planning.py` a property test, using Hypothesis as the file already does: for a previous status drawn from `doing` and `review`, any note text and any reviewer, an edit to `planning` raises `ChittyError` mentioning `to-plan`. Add one example where a history with one `doing → planning` and one `doing → to-plan` return makes the next `to-plan` return escalate (the count includes the current return, so this is the third).

## Acceptance Criteria

- [ ] The new property test (an edit from `doing` or `review` to `planning` is refused) and the mixed-history escalation example pass, and each fails before the change. Regression tests: the re-pointed return and escalation tests named above
- [ ] `tests/test_statuses_planning.py` covers `to-plan` in `chitty list` and MCP `list` defaults and in `chitty next` never picking it, and those cases fail before the change
- [ ] `make check` passes

## History

- 2026-11-25T23:05:55Z golden-coral-stoat → backlog
- 2026-11-25T23:06:21Z golden-coral-stoat: changed description, acceptance criteria
