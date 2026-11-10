---
title: Run tickets with `claude` as the agent
status: todo
priority: high
owner: human
depends_on:
  - TASK-142
  - TASK-154
  - TASK-156
parent: TASK-106
created: 2026-11-04
---

## Description

Prove that `chitty run --agent claude` can work and review a real ticket, using the `claude` entry already in `chitty.toml` (`claude -p`, Sonnet, an allow-list, `git push` denied). Pi stays the default; `claude` is the fallback when Pi tokens run out.

The human runs it, from an ordinary shell rather than inside an agent, because it starts an agent session:

1. Pick a `todo` ticket with no owner and run `chitty run --agent claude --ticket <ID>`.
2. Run the same command again to review that work.
3. Report: the model the session used, any commands it was denied and what that cost, whether it stopped without changing the ticket, and the cost if shown.

The planning session then records that in a note, fixes the allow-list where a denial was wrong, and documents the entry in `README.md`.

## Acceptance Criteria

- [ ] `chitty run --agent claude` works a real ticket and then reviews it on Sonnet, and a note records the outcome and the three reported checks.
- [ ] `README.md` shows the `claude` entry for `[agent_commands]`, with its allow-list and why `git push` is denied.

## Notes

Allow-list taken from the commands agents actually ran (human analysis, 2026-11-04): Chitty, Git, `make`, `uv run`, `python`, `npm test`, and search and text tools. Occasional commands such as `rm`, `cp` and `mkdir` are left out; agents should adapt.

## History

- 2026-11-04T15:38:29Z mellow-newt → backlog
- 2026-11-04T15:40:08Z mellow-newt: changed description, notes
- 2026-11-04T17:32:42Z mellow-newt: changed description, notes
- 2026-11-04T17:34:53Z mellow-newt: changed owner, description, acceptance criteria, notes
- 2026-11-04T17:34:54Z mellow-newt backlog → todo
- 2026-11-04T17:58:14Z mellow-newt: changed description, notes
- 2026-11-04T17:58:14Z mellow-newt todo → backlog
- 2026-11-04T18:01:15Z mellow-newt: changed dependencies, acceptance criteria, notes
- 2026-11-04T18:01:16Z mellow-newt backlog → todo
- 2026-11-04T20:15:23Z mellow-newt: changed notes
- 2026-11-04T20:32:40Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-10T20:51:48Z jolly-heron: replaced notes; changed description, acceptance criteria
