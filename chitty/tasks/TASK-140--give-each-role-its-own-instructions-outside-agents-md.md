---
title: Give each role its own instructions, outside `AGENTS.md`
status: backlog
priority: medium
parent: TASK-106
created: 2026-11-04
---

## Description

Raised by the human on 2026-11-04. `AGENTS.md` belongs to the repository it sits in, so instructions for how to work under Chitty should not live there. Today `chitty init` writes one 55-line `## Chitty` block into it. Every agent reads every role's rules: a worker reads how to review, and a `TASK-132` worker took a planning step in the block's neighbour as its own. The role prompts also exist separately in `src/chitty/integrations/pi/chitty.ts`, partly repeating the block, so another agent has none of them.

Proposed, to refine before promoting:

- Ship one file per role in the package: `work`, `review`, `plan`. `plan` holds the cold-read procedure, now only in this repository's `PLAN.md`, so other repositories get it too.
- `chitty guide <role>` prints a role's instructions. `chitty guide` already exists, so no new command is needed. With a ticket ID it renders the full prompt for that ticket.
- The Pi extension asks Chitty for the prompt rather than holding its own copy.
- `agent_command` from `TASK-136` gains a `{prompt}` placeholder, replaced after the split so it stays one word, as in `claude "{prompt}"`. This removes the main thing tying workers to Pi, noted on `TASK-89` and `TASK-90`.
- The block in `AGENTS.md` shrinks to what every session needs: that tasks live in `chitty/`, not to hand-edit them, and to run `chitty guide <role>`. A person starting an agent by hand still has a way in. `chitty init` already replaces the block, so existing repositories pick this up with a version bump.
- Remove instructions `chitty run` makes redundant, such as creating worktrees, once `TASK-126` has landed. The role files should be short: the tool carries the rules.

Open: what happens to the `chitty://guide` MCP resource; whether a role file can be overridden per repository, which should wait for a need; and whether this should come before the pilot, since it changes what the pilot measures. Likely too large for one ticket: the role files and `chitty guide` first, then the extension and `{prompt}`, then shrinking the block.

## Notes

Split on 2026-11-04 with the human's agreement, into `TASK-141`, `TASK-142` and `TASK-143`, all to land before the pilot. This ticket stays as the design record and needs no work of its own. Decided: the `chitty://guide` resource keeps returning the block, and per-repository overrides wait for a need.

## History

- 2026-11-04T10:09:08Z lively-panda → backlog
- 2026-11-04T11:56:20Z lively-panda: changed notes
