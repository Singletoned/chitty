---
title: Leave every owned ticket out of a plain `chitty run`
status: backlog
priority: high
created: 2026-11-06
---

## Description

The human wants ownership to be the one way to keep a ticket out of the loops. A plain `chitty run` or `chitty next` picks up only unowned tickets, and setting any owner takes a ticket out, so a person, a Claude session or another agent can each reserve tickets under their own name, without pretending to be `human`.

Today, `_skip_reason` in `src/chitty/store.py` returns early for `review` tickets before its owner check. So a plain run still selects owned `review` tickets unless the owner is `human` (`TASK-197`'s rule). Change it so that, in plain selection, a ticket with any owner is skipped at `review`, `doing` and `todo` alike, with the reason `👤 <owner>`. `human` keeps its current treatment, including the `human` context. `--owner NAME` still selects only that owner's tickets, in any active status. `chitty run --ticket ID` still ignores non-human ownership.

Update:
- the paragraph in `README.md` around lines 101–108 about owned tickets, whose sentences are also out of order today;
- the `owner` text in `PLAN.md`'s frontmatter section and "Next action and runner";
- any test that expects an owned `review` ticket to be selected, which is `TASK-197`'s old rule.

Out of scope: who sets or clears owners.

## Acceptance Criteria

- [ ] Tests show plain `chitty next`, `chitty run` and the MCP `next` tool skipping an owned `review` ticket as well as owned `todo` and `doing` ones, `chitty list` showing `👤 <owner>` for each, and `--owner NAME` selecting that owner's `review` ticket.
- [ ] `README.md` and `PLAN.md` say a plain run picks up only unowned tickets, and `make check` passes.

## History

- 2026-11-06T19:52:07Z youthful-toad → backlog
