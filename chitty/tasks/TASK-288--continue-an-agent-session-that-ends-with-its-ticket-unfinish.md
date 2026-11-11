---
title: Continue an agent session that ends with its ticket unfinished
status: todo
labels:
  - bug
parent: TASK-275
created: 2026-11-11
---

## Description

- Print-mode Pi has no Chitty extension, so nothing continues a session that stops early. TASK-270's worker stopped after `make check` failed, leaving uncommitted changes; `chitty run` then raised `TASK-270 was unchanged`, which ended the human's `--loop`.
- When a work agent exits 0 with the ticket still `doing`, or a review agent with it still `review`, `chitty run` continues the same session in the same worktree: it runs the same agent command again with `-c` appended, as `--model` is, and the continuation prompt in place of `{prompt}`. Pi and Claude Code both continue the directory's latest session with `-c`. It continues at most `MAX_CONTINUATIONS` (5, a module constant) times per run, judging by status alone, then raises the existing `was unchanged` error. Any other status (`review`, `done`, `blocked`, `todo`) ends the run as today.
- Each continuation is a session like the first: the same `--model` default and forwarded `--` arguments, its own `agent_timeout`, and a timeout or non-zero exit fails the run as for the first session. One usage record covers the whole run.
- The continue command is a new optional root setting, `agent_continue_command`, and for `--agent NAME` the entry `NAME` in a new `[agent_continue_commands]` table, parsed like `agent_command` and `[agent_commands]`; both take `{prompt}`. Without one, behaviour is as today. Pi and Claude Code both continue the directory's latest session with `-c`. After this lands, the planner sets them in this repository on `main`; the branch leaves `chitty.toml` alone.
- The prompt, adapted from `continuationPrompt` in `src/chitty/integrations/pi/chitty.ts`. Work: "Continue working only on Chitty ticket <ID>. Either finish it and set it to `review`, or set it to `blocked` with a note giving the reason. Do not stop with it unfinished." Review: "Continue reviewing only Chitty ticket <ID>. Either pass it (`done`) or fail it (`doing`, with the failures in one note), or set it to `blocked` with a note giving the reason. Do not merge or remove branches or worktrees."
- Document the settings in `README.md` and `PLAN.md` "Config".

## Acceptance Criteria

- [ ] A `chitty run` whose fake agent leaves the ticket in `doing` and whose fake continue command moves it to `review` ends with the ticket in `review`; the continue command received the continuation prompt naming the ticket. It fails today.
- [ ] A continue command that never changes the ticket is run 5 times, then `chitty run` fails with `was unchanged`. Without a continue command it fails after the first session, as today.
- [ ] A continue command that sets the ticket to `blocked` runs once, and the run ends with the ticket `blocked`.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-288/1`. Check it against the current criteria; do not trust it.

## History

- 2026-11-11T16:17:51Z vivid-yellowhammer → backlog
- 2026-11-11T18:50:19Z vivid-yellowhammer: changed title, description
- 2026-11-11T18:50:20Z vivid-yellowhammer: changed acceptance criteria
- 2026-11-11T18:50:56Z vivid-yellowhammer backlog → cold-read
- 2026-11-11T18:54:41Z vivid-yellowhammer: changed description
- 2026-11-11T18:54:42Z vivid-yellowhammer: changed acceptance criteria, notes
- 2026-11-11T18:54:42Z vivid-yellowhammer cold-read → todo
- 2026-11-11T18:58:52Z vivid-yellowhammer: changed description
