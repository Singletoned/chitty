---
title: Work agents give up on larger tickets with "can't complete in this turn"
status: backlog
created: 2026-11-22
---

## Description

Seen 2026-11-21 with `chitty run --loop --mode work -- --model gpt-6.1-terra` (Pi, `pi -p`). On `TASK-519` and `TASK-393` the first session recorded a plan, then every continuation answered only "I can't complete TASK-<n> in this turn/response ... it remains in doing" with no code, until the runner set `error` (`was unchanged`). Runs lasted about 100 s. Logs: `.git/chitty/run/TASK-519-20261121230420816936Z.log` and the latest `TASK-393-*.log`. Smaller tickets (`TASK-520`, 135 s) passed with the same model. Splitting the tickets worked around it. Ideas: say in the work guide and `continuation_prompt` (`src/chitty/run.py`) that the session has no turn limit and the agent should keep making tool calls and commit progress in steps; stop the loop or flag the model when several consecutive sessions end with no commit and this phrasing; record session count and commits in the usage log so the pattern is visible.

## Notes

Suggestion origin: chitty

Triage 2026-11-24: two more reports of the same pattern, on 2026-11-23. TASK-663: TASK-629 and TASK-599 ended in `error` right after planning moved them to `todo`, with sessions of about 11 s and notes like "I cannot honestly classify it as ready for review, defective, or externally blocked"; both are large, so "too large" may be what the agent meant but did not say. TASK-683: TASK-557 and TASK-598 went to `error` after 5 continuations with no new commits (sessions of about 23 s); TASK-557 was then finished by hand in one session, so the worker was stopping by choice. Check what the continuation prompt and work guide tell the agent, and whether a continuation should say plainly to keep going or return the ticket to planning with a reason.

## History

- 2026-11-22T09:47:34Z friendly-jade-stoat → backlog
- 2026-11-22T09:47:34Z friendly-jade-stoat: changed notes
- 2026-11-24T22:39:47Z zesty-coral-newt: changed notes
