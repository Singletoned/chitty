---
title: "Work guide: let workers settle small edge cases and record them"
status: backlog
created: 2026-11-22
---

## Description

On 2026-11-21 TASK-391 (renumber provisional tickets) went `doing → planning` seven times. Each worker read deeper, found the next edge case, and returned the ticket without building anything. The cases were real, but each had an obvious default the planner chose in minutes:
- outside Git with `autocommit = true` (keep the existing refusal);
- reusing a number a ticket already mentions (reserve mentioned numbers);
- a rewritten title changing the slug (use the final title's slug);
- unconfigured directories (leave them alone, but reserve their filenames' numbers);
- an unreachable shared-prefix clause (remove it).

`src/chitty/roles/work.md` and the managed AGENTS block send any "unresolved design decision" back to planning. Workers treat every gap as one. That costs a full session per gap, and the planner's answers did not need the owner.

Suggest: the work guide lets a worker settle a small edge case itself when the ticket's decisions and the existing code point to one reasonable choice, with no new user-visible behaviour, setting or command. It then records the choice in a note (`Decided: <case> -> <choice>, because <reason>`) and tests it. The reviewer checks those notes like any other decision. Return to planning stays for contradictions, user-visible choices, and gaps with no clear default.

## Notes

Suggestion origin: chitty

## History

- 2026-11-22T09:47:32Z friendly-jade-stoat → backlog
- 2026-11-22T09:47:32Z friendly-jade-stoat: changed notes
