---
title: Write a tickets-only managed block under the tickets workflow
status: planning
depends_on:
  - TASK-331
created: 2026-11-14
---

## Description

Under `workflow = "tickets"`, the managed block that `chitty init` writes into `AGENTS.md`, and that `chitty guide` and the MCP `chitty://guide` resource serve, holds only the ticketing rules.

- Tickets block: the first paragraph of the current `src/chitty/guide.md` (use the CLI or MCP and do not hand-edit task files; backticks; escaping `*`; shell quoting; `chitty --help`). Nothing about landing, branches, worktrees, reviews, review notes, role guides or returning tickets to `planning`.
- Runner block: unchanged from today.
- Keep both texts as package files, the tickets block being the runner block's first part, so the shared rules exist once.
- `chitty init` replaces the block when the workflow changes, as it already does when the text changes.

## Acceptance Criteria

- [ ] Under `tickets`, `chitty init` writes a block containing only the first paragraph of the current guide, and `chitty guide` and `chitty://guide` serve the same text.
- [ ] Under `runner`, the block, `chitty guide` and `chitty://guide` are byte-identical to before this change.
- [ ] Changing the workflow and re-running `chitty init` replaces the block.
- [ ] The shared ticketing paragraph exists in one package file only.
- [ ] Tests cover criteria 1 to 3, and fail without the change.

## History

- 2026-11-14T18:21:55Z friendly-ginger-adder → planning
