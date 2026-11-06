---
title: Leave every owned ticket out of a plain `chitty run`
status: doing
priority: high
created: 2026-11-06
---

## Description

The human wants ownership to be the one way to keep a ticket out of the loops. A plain `chitty run` or `chitty next` picks up only unowned tickets, and setting any owner takes a ticket out, so a person, a Claude session or another agent can each reserve tickets under their own name, without pretending to be `human`.

Today, `_skip_reason` in `src/chitty/store.py` returns early for `review` tickets before its owner check. So a plain run still selects owned `review` tickets unless the owner is `human` (`TASK-197`'s rule). Change it so that, in plain selection, a ticket with any owner is skipped at `review`, `doing` and `todo` alike, with the reason `👤 <owner>`. `human` keeps its current treatment, including the `human` context. `--owner NAME` still selects only that owner's tickets, in any active status. `chitty run --ticket ID` still ignores non-human ownership.

Update:
- the paragraph in `README.md` around lines 101–108 about owned tickets, whose sentences are also out of order today;
- `PLAN.md`: the `owner` text under the frontmatter table (around lines 232–236) and in "Next action and runner" (around line 699);
- `test_owner_filter_reserves_work_but_not_review` in `tests/test_next.py`, which expects an owned `review` ticket to be selected (`TASK-197`'s old rule).

The code change is removing the `review` early return in `_skip_reason`. `_ticket_action`, `chitty list` and MCP `list` already go through it. The third-failure escalation sets `blocked`, which `_skip_reason` doesn't consider, so it is unaffected. No `__version__` bump.

Out of scope: who sets or clears owners.

## Acceptance Criteria

- [ ] Tests show plain `chitty next`, `chitty run` and the MCP `next` tool skipping an owned `review` ticket as well as owned `todo` and `doing` ones, `chitty list` showing `👤 <owner>` for each, and `--owner NAME` selecting that owner's `review` ticket.
- [ ] `README.md` and `PLAN.md` say a plain run picks up only unowned tickets, and `make check` passes.

## Notes

Cold read 1 (Sonnet, `refs/cold-read/TASK-222/1`; the new tests failed before and passed after; `make check` OK; the whole code change was one early return). Outcomes:
- The test to replace wasn't named: fixed, it's named.
- `PLAN.md` locations were vague: fixed, with approximate line numbers.
- Version bump: fixed, the ticket says none.
- Escalation to `human` is unaffected, because it sets `blocked`: confirmed.
- No guide or Pi extension text mentions owned reviews: confirmed.
- `chitty run` stderr carries other output: the reader matched its end; accepted.

## History

- 2026-11-06T19:52:07Z youthful-toad → backlog
- 2026-11-06T20:01:58Z youthful-toad: changed description, notes
- 2026-11-06T20:01:58Z youthful-toad backlog → todo
- 2026-11-06T20:14:07Z brisk-puffin todo → doing
