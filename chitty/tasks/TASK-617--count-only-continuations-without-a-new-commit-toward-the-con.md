---
title: Count only continuations without a new commit toward the continuation cap
status: cold-read
created: 2026-11-23
---

## Description

`_agent_sessions` (`src/chitty/run.py`, around line 745) continues an agent whose ticket status did not change, at most `MAX_CONTINUATIONS` (5, `run.py:62`) times, then raises `<ID> was unchanged; only committed changes are visible to `chitty run`` and the ticket goes to `error`. The cap is meant to stop an idle agent, but it also counts productive sessions. In taidy (2026-11-23, Chitty 0.7.0) an agent ended each turn after one step yet committed regression tests, the implementation and a Docker fixture across its continuations; after 5 it was set to `error`, with a message saying "unchanged" although the branch had three new commits.

Change:

- Record the ticket branch HEAD (`git.ref_commit(worktree, "HEAD")`) before and after each session. Decide whether to continue in a pure function `continuation_step(heads_moved: Sequence[bool], cap: int) -> Literal["continue", "stop"]`: stop only when the last `cap + 1` sessions all left HEAD where it was. A session that commits resets the count. The status check stays as today: any status change ends the loop first.
- Reword the stop error to `<ID> is still `<status>` after <N> continuations with no new commit; only committed changes are visible to `chitty run``.
- Keep the `_accepts_prompt` case (an agent that cannot be continued) as it is.

Property tool: Hypothesis.

Out of scope: leaving the ticket in `doing` instead of `error` when the cap is hit after progress (TASK-613's requeue idea): under `chitty run --loop` the same ticket would be picked straight away and could repeat forever. Also out of scope: a cap on total sessions; each session is already bounded by `agent_timeout`.

## Acceptance Criteria

- [ ] A Hypothesis property test of `continuation_step(heads_moved, cap)` in a new file `tests/test_continuation_step.py` draws a list of booleans (one per session, `True` when the ticket branch HEAD moved during it) and a cap from 0 to 6. It asserts the result is `stop` exactly when the list ends with more than `cap` consecutive `False` values, otherwise `continue`; adding a `True` at the end never gives `stop`.
- [ ] A `tests/test_run_log.py` test (fixture `TestRunLog.fixture`) uses an agent that commits a new file in each of its first 7 sessions without changing the ticket, then sets `review` on the 8th. `chitty run --ticket` prints `doing → review`. This fails on `main`, where the 6th unchanged session sets `error`.
- [ ] A test with an agent that never commits or changes the ticket ends in `error` after 1 + `MAX_CONTINUATIONS` sessions, and the note reads `<ID> is still `doing` after 5 continuations with no new commit; only committed changes are visible to `chitty run`` (with the real count and status); the old `was unchanged` wording no longer appears.

## Notes

Suggestion origin: taidy

Folded in from TASK-613: when a work run ends with the ticket still `doing`, prefer requeueing it over `error`, since nothing is broken.

## History

- 2026-11-23T10:24:13Z witty-russet-gannet → backlog
- 2026-11-23T10:24:14Z witty-russet-gannet: changed notes
- 2026-11-23T10:27:32Z witty-russet-gannet: changed notes
- 2026-11-23T10:33:24Z witty-russet-gannet: changed title, description, acceptance criteria
- 2026-11-23T10:33:24Z witty-russet-gannet backlog → planning
- 2026-11-23T10:33:33Z witty-russet-gannet planning → cold-read
