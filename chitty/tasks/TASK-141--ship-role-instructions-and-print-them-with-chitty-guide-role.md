---
title: Ship role instructions and print them with `chitty guide <role>`
status: todo
priority: medium
depends_on:
  - TASK-126
parent: TASK-140
created: 2026-11-04
---

## Description

First of three parts of `TASK-140`. Ship one instruction file per role in the package, and print them from the existing `chitty guide` command. Nothing reads them yet, so nothing else changes: the next tickets switch the agents over.

Add `src/chitty/roles/work.md`, `review.md` and `plan.md`, as package data like `guide.md`. Write them from what `src/chitty/guide.md` and `chittyPrompt` in `src/chitty/integrations/pi/chitty.ts` say today, after `TASK-126` has removed the worktree, setup and claiming steps. Each role gets only its own rules, and they stay short, because the tool carries the rules. `plan.md` takes the cold-read procedure from `PLAN.md`, which then points to it, and covers writing tickets: the ready definition and about five criteria.

- `chitty guide` with no argument prints the `AGENTS.md` block, as now.
- `chitty guide <role>` prints that role's instructions.
- `chitty guide <role> <ID>` prints the same, preceded by a line saying to work only on that ticket. The ticket's own content is not included: the agent runs `chitty show`.
- An unknown role fails with a message listing the roles. `plan` with an ID fails, because planning is not about one ticket.

`guide()` in `src/chitty/store.py` holds the logic and `cli.py` stays thin.

Out of scope: `chitty.ts`, the `AGENTS.md` block, the `chitty://guide` MCP resource, which keeps returning the block, and overriding a role file per repository.

## Acceptance Criteria

- [ ] CLI tests show `chitty guide` unchanged, each role printing, `<role> <ID>` naming the ticket first, and an unknown role and `plan <ID>` failing with a message
- [ ] A test shows the three role files present in a built wheel
- [ ] `work.md` has no review or planning rules, `review.md` no work or planning rules, and `plan.md` holds the cold-read procedure, with `PLAN.md` pointing to it
- [ ] `README.md` and `PLAN.md` describe the roles

## History

- 2026-11-04T11:56:18Z lively-panda → todo
