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
- When a work agent exits 0 with the ticket still `doing`, or a review agent with it still `review`, `chitty run` continues the same session in the same worktree: it runs the same agent command again with `-c` appended, as `--model` is, and the continuation prompt in place of `{prompt}`. Pi and Claude Code both continue the directory's latest session with `-c`. It continues at most `MAX_CONTINUATIONS` (5, a module constant) times per run, judging by status alone, then raises the existing `was unchanged` error. Any status change ends the run as today.
- Each continuation is a session like the first: the same `--model` default and forwarded `--` arguments, its own `agent_timeout`, and a timeout or non-zero exit fails the run as for the first session. One usage record covers the whole run.
- Only `{prompt}` commands are continued; a `{mode} {id}` command, which loads the Pi extension, fails as today. There are no new settings.
- The prompt, adapted from `continuationPrompt` in `src/chitty/integrations/pi/chitty.ts`. Work: "Continue working only on Chitty ticket <ID>. Either finish it and set it to `review`, or set it to `blocked` with a note giving the reason. Do not stop with it unfinished." Review: "Continue reviewing only Chitty ticket <ID>. Either pass it (`done`) or fail it (`doing`, with the failures in one note), or set it to `blocked` with a note giving the reason. Do not merge or remove branches or worktrees."
- Document continuation in `README.md` and `PLAN.md` "Next action and runner".

## Acceptance Criteria

- [ ] A `chitty run` whose fake `{prompt}` agent leaves the ticket in `doing` the first time, and moves it to `review` when started with `-c`, ends with the ticket in `review`; the second start received `-c` and the continuation prompt naming the ticket. It fails today.
- [ ] A fake agent that never changes the ticket is started 6 times (the first session and 5 continuations), then `chitty run` fails with `was unchanged`. A `{mode} {id}` agent fails after the first session, as today.
- [ ] A fake agent that sets the ticket to `blocked` when continued is continued once, and the run ends with the ticket `blocked`.

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
- 2026-11-11T18:59:02Z vivid-yellowhammer: changed description
- 2026-11-11T18:59:03Z vivid-yellowhammer: changed description
- 2026-11-11T18:59:04Z vivid-yellowhammer: changed acceptance criteria
- 2026-11-11T18:59:13Z vivid-yellowhammer: changed description
