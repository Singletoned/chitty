---
title: Give `chitty run` its actor before the inbox pull
status: backlog
priority: high
created: 2026-11-06
---

## Description

`chitty run` from a plain terminal, with no `CHITTY_ACTOR` and no harness session variable, fails with `cannot determine actor; set CHITTY_ACTOR or provide one of ...` whenever the inbox has a suggestion. `run` in `src/chitty/run.py` calls `pull_suggestions`, which creates a backlog ticket through `Repo.add` and so calls `actor()`. But `run` only assigns its own `CHITTY_ACTOR = run_actor(...)` later, in `_run_ticket`. Seen on 2026-11-06 with the work loop.

Move those two lines (the `os.environ` pop and set, and their comment) to the start of `run`, straight after the argument refusals and before `_main_checkout`. Then the inbox pull, the setup refresh, the claim, the agent and any child process all share the run's one identity. Update the comment to say so.

`TASK-207` also moves the assignment, for its lock record. It depends on this ticket and should use the new position.

Out of scope: how a reviewing subagent gets its own actor (`TASK-209`).

## Acceptance Criteria

- [ ] A test runs `chitty run` with `CHITTY_ACTOR` and every harness variable listed in that error removed from the environment, a fake agent, and one suggestion in the (temporary) inbox. The run succeeds, and the pulled ticket's `## History` names the same actor as the agent's `CHITTY_ACTOR`. It fails before the fix with `cannot determine actor`.

## History

- 2026-11-06T13:44:09Z youthful-toad → backlog
