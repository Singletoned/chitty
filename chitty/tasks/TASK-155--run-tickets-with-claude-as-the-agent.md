---
title: Run tickets with `claude` as the agent
status: todo
priority: high
owner: human
depends_on:
  - TASK-142
  - TASK-154
  - TASK-156
created: 2026-11-04
---

## Description

Prove that `chitty run --agent claude` can work and review a real ticket, using the `claude` entry in `chitty.toml`: `claude -p` on Haiku, as workers normally run on Luna or Haiku, with `bypassPermissions` and only `git push` denied. Pi stays the default; `claude` is the fallback when Pi tokens run out.

The human runs it from an ordinary shell, because it starts an agent session:

1. Pick a `todo` ticket with no owner and run `chitty run --agent claude --ticket <ID>`.
2. Run the same command again to review that work.
3. Report whether it stopped without changing the ticket, anything it could not do, and the cost if shown.

The planning session records the outcome in a note and documents the entry in `README.md`.

## Acceptance Criteria

- [x] `chitty run --agent claude` works a real ticket and then reviews it, and a note records the outcome.
- [x] `README.md` shows the `claude` entry for `[agent_commands]` and why `git push` is denied.

## Notes

Trial 1 (2026-11-10, TASK-247, Haiku by the human's choice): the allow-list in `dontAsk` mode refused 7 of 30 calls (`ps`, `.venv/bin/python`, compound commands, long quoted `chitty edit` notes), so the agent could not see tests fail first or update the ticket. The human then dropped the allow-list for `bypassPermissions`.

Trial 2 started 2026-11-11 by the planning session: `chitty run --agent claude --ticket TASK-277`.

Trial 2 work run (2026-11-11, TASK-277, Haiku, `bypassPermissions`): finished in about 6 minutes with no refused calls. It committed code and docs, showed the new test failing first, passed `make check`, and moved the ticket to `review`.

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
- 2026-11-10T21:58:25Z jolly-heron: changed notes
- 2026-11-10T22:10:17Z jolly-heron: replaced notes; changed description, acceptance criteria
- 2026-11-11T10:17:27Z vivid-yellowhammer: changed parent
- 2026-11-11T15:58:20Z vivid-yellowhammer: changed notes; ticked acceptance criteria
- 2026-11-11T16:05:06Z vivid-yellowhammer: changed notes
- 2026-11-11T16:17:26Z vivid-yellowhammer: replaced notes; ticked acceptance criteria
