---
title: Continue an agent session that ends with its ticket unfinished
status: cold-read
labels:
  - bug
parent: TASK-275
created: 2026-11-11
---

## Description

- Print-mode Pi has no Chitty extension, so nothing continues a session that stops early. TASK-270's worker stopped after `make check` failed, leaving uncommitted changes; `chitty run` then raised `TASK-270 was unchanged`, which ended the human's `--loop`.
- When a work agent exits 0 with the ticket still `doing`, or a review agent with it still `review`, `chitty run` continues the same session in the same worktree: it runs the agent's continue command with a continuation prompt, up to `MAX_CONTINUATIONS` (5, a module constant) times, then raises the existing error.
- The continue command is a new optional root setting, `agent_continue_command`, and for `--agent NAME` an entry `NAME` in a new `[agent_continue_commands]` table; both take `{prompt}`. Without one, behaviour is as today. This repository sets `pi -p -c ... {prompt}` (same prefix and flags as `agent_command`), and `claude -p -c ...` for `claude`, on `main`.
- The prompt, adapted from `continuationPrompt` in `src/chitty/integrations/pi/chitty.ts`: "Continue working only on Chitty ticket <ID>. Either finish it, or set it to `blocked` with a note giving the reason. Do not stop with it unfinished." Document the settings in `README.md` and `PLAN.md` "Config".

## Acceptance Criteria

- [ ] A `chitty run` whose fake agent leaves the ticket in `doing` and whose fake continue command moves it to `review` ends with the ticket in `review`; the continue command received the continuation prompt naming the ticket. It fails today.
- [ ] A continue command that never changes the ticket is run 5 times, then `chitty run` fails with `was unchanged`. Without a continue command it fails after the first session, as today.

## History

- 2026-11-11T16:17:51Z vivid-yellowhammer → backlog
- 2026-11-11T18:50:19Z vivid-yellowhammer: changed title, description
- 2026-11-11T18:50:20Z vivid-yellowhammer: changed acceptance criteria
- 2026-11-11T18:50:56Z vivid-yellowhammer backlog → cold-read
