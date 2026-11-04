---
title: Ship role instructions and print them with `chitty guide <role>`
status: doing
priority: high
depends_on:
  - TASK-126
parent: TASK-140
created: 2026-11-04
---

## Description

First of three parts of `TASK-140`. Ship one instruction file per role in the package, and print them from the existing `chitty guide` command. Nothing reads them yet, so nothing else changes: the next tickets switch the agents over.

Add `src/chitty/roles/work.md`, `review.md` and `plan.md`, as package data like `guide.md`. Write them from what `src/chitty/guide.md` and `chittyPrompt` in `src/chitty/integrations/pi/chitty.ts` say today, after `TASK-126` has removed the worktree, setup and claiming steps. Each role gets only its own rules, in about 30 lines at most, because the tool carries the rules.

Every rule in `guide.md` needs a home, or a reason recorded in a note for dropping it. Several are in no prompt today, so would be easy to lose:

- `work`: planning and claiming as they remain, ticking criteria, notes, `--summary`, `chitty fix`, `Task: <ID>` commit lines, cheap defaults, and blocked and `human` handling.
- `review`: never reviewing your own work, every criterion, one failure note in the `Review failed (<cause>): ...` form from `PLAN.md` with its causes, and `--uncheck`. The guide does not ask for that form yet, and a `TASK-126` review missed it. Fail only for an unmet criterion or a demonstrated defect, such as a throwaway failing test, and file a ticket for anything else. A reviewer who finds a ticket too large should say so in the note and suggest how to split it. Both decided by the human on 2026-11-04.
- `plan`: writing tickets, the cold read, promoting `backlog` tickets, `parent`, and `chitty archive`.
- `work` and `review` both: `chitty suggest` and `chitty add` for unrelated findings. `plan.md` takes the cold-read procedure from `PLAN.md`, which then points to it, and covers writing tickets: the ready definition and about five criteria.

- `chitty guide` with no argument prints the `AGENTS.md` block, as now.
- `chitty guide <role>` prints that role's instructions.
- `chitty guide <role> <ID>` prints the same, preceded by a line saying to work only on that ticket. The ticket's own content is not included, and the ID is not looked up, so this needs no repository: the agent's `chitty show` reports a bad ID.
- An unknown role fails with a message listing the roles. `plan` with an ID fails, because planning is not about one ticket.

`guide()` in `src/chitty/store.py` holds the logic and `cli.py` stays thin. The paragraph `guide_` in `cli.py` adds when `pi_session_environment_missing()` must not appear in role output, because that output becomes a prompt.

Out of scope: `chitty.ts`, the `AGENTS.md` block, the `chitty://guide` MCP resource, which keeps returning the block, and overriding a role file per repository.

## Acceptance Criteria

- [ ] `README.md` and `PLAN.md` describe the roles
- [ ] CLI tests show `chitty guide` unchanged, each role printing, `<role> <ID>` naming the ticket first, an unknown role and `plan <ID>` failing with a message, and role output omitting the Pi session paragraph with `PI_CODING_AGENT=true` set
- [ ] A note records `uv build` and a listing showing the three role files in the wheel
- [ ] Each role file is about 30 lines at most and holds only its role's rules, `plan.md` holds the cold-read procedure with `PLAN.md` pointing to it, and a note accounts for every `guide.md` rule

## Notes

Cold read by a fresh Sonnet subagent with `TASK-142` and `TASK-143`, 2026-11-04. Fixed: rules that fit no role, now each assigned; the Pi session paragraph polluting a prompt, which I reproduced with `PI_CODING_AGENT=true`; "short" not being checkable, now about 30 lines; and the `Review failed (<cause>)` form, added by me from the `TASK-126` retro note. A wheel-building test became a recorded check: hatchling ships the whole package, as it does `guide.md`, so a test would add a slow build to guard little. Rejected: looking up the ID, because `chitty show` fails loudly straight after. Depending only partly on `TASK-126`, because the role files must describe what `chitty run` leaves to the agent.

Added on 2026-11-04 after `TASK-126` failed six reviews: when a reviewer may fail a ticket, and suggesting a split.

Raised to high on 2026-11-04: `TASK-155`, which the human made high priority, needs it.

## History

- 2026-11-04T11:56:18Z lively-panda → todo
- 2026-11-04T12:00:37Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-04T14:36:50Z mellow-newt: changed description, notes
- 2026-11-04T15:38:30Z mellow-newt: changed priority, notes
- 2026-11-04T17:22:46Z intrepid-otter todo → doing
