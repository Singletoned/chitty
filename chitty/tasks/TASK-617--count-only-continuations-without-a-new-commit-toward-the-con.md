---
title: Count only continuations without a new commit toward the continuation cap
status: cold-read
created: 2026-11-23
---

## Description

`_agent_sessions` (`src/chitty/run.py`, around line 745) continues an agent whose ticket status did not change, at most `MAX_CONTINUATIONS` (5, `run.py:62`) times, then raises `<ID> was unchanged; only committed changes are visible to `chitty run`` and the ticket goes to `error`. The cap is meant to stop an idle agent, but it also counts productive sessions. In taidy (2026-11-23, Chitty 0.7.0) an agent ended each turn after one step yet committed regression tests, the implementation and a Docker fixture across its continuations; after 5 it was set to `error`, with a message saying "unchanged" although the branch had three new commits.

Change:

- A session made progress when it committed a change outside the ticket directories. Record HEAD (`git.ref_commit(worktree, "HEAD")`) before and after each session, and pass the paths changed between them (`git.changed_paths(worktree, before, after)`) to the existing `has_work_beyond_tickets` (`run.py:109`) with the configured ticket directories. A session that only adds notes (each `chitty` write autocommits) or makes an empty commit is not progress, so an idle agent that keeps noting still reaches the cap. If HEAD is unborn or unchanged, the session made no progress.
- Decide whether to continue in a pure function in `run.py`, `continuation_step(progress: Sequence[bool], cap: int) -> Literal["continue", "stop"]`, with one entry per session so far (never empty): stop only when the last `cap + 1` entries are all `False`. Progress resets the count. The status check stays as today: any status change ends the loop first. This is shared by work and review sessions (`_agent_sessions` runs for every mode).
- Reword the stop error to `<ID> is still `<status>` after <N> continuations with no new work committed; only committed changes are visible to `chitty run``.
- Keep the `_accepts_prompt` case (an agent that cannot be continued) stopping after its first session, with the new wording (`after 0 continuations`).

Existing test: `test_unchanged_ticket_is_continued_five_times_then_fails` (`tests/test_run_continue.py:101`) uses a fake agent that commits with `--allow-empty` each session; that is not progress, so the test must keep passing unchanged apart from the message.

Property tool: Hypothesis.

Out of scope: leaving the ticket in `doing` instead of `error` when the cap is hit after progress (TASK-613's requeue idea): under `chitty run --loop` the same ticket would be picked straight away and could repeat forever. Also out of scope: a cap on total sessions; each session is already bounded by `agent_timeout`.

## Acceptance Criteria

- [ ] A Hypothesis property test of `continuation_step(progress, cap)` in a new file `tests/test_continuation_step.py` draws a non-empty list of booleans (one per session) and a cap from 0 to 6. It asserts the result is `stop` exactly when the list ends with more than `cap` consecutive `False` values, otherwise `continue`; appending `True` never gives `stop`.
- [ ] A work-mode test in `tests/test_run_continue.py` (its fake-agent fixture, which logs invocations) uses an agent that, in each of its first 7 sessions, writes and `git add`s a new non-ticket file and commits it without changing the ticket, then sets `review` on the 8th. `chitty run --ticket` prints `doing → review` and the fixture saw 8 invocations. This fails on `main`, where the 6th unchanged session sets `error`.
- [ ] In `tests/test_run_continue.py`, an agent that only appends a note through `chitty note` each session (moving HEAD but changing only the ticket file) ends `doing → error` after 6 invocations, and the ticket's note reads `<ID> is still `doing` after 5 continuations with no new work committed; only committed changes are visible to `chitty run``; `test_unchanged_ticket_is_continued_five_times_then_fails` asserts the same new wording.

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
- 2026-11-23T10:35:50Z witty-russet-gannet: changed description, acceptance criteria
- 2026-11-23T10:35:50Z witty-russet-gannet cold-read → planning
- 2026-11-23T10:35:52Z witty-russet-gannet: changed description
- 2026-11-23T10:35:52Z witty-russet-gannet planning → cold-read
- 2026-11-23T10:35:54Z witty-russet-gannet: changed acceptance criteria
