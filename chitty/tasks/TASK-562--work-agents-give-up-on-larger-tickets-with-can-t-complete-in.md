---
title: Work agents give up on larger tickets with "can't complete in this turn"
status: backlog
created: 2026-11-22
---

## Description

Seen 2026-11-21 with `chitty run --loop --mode work -- --model gpt-6.1-terra` (Pi, `pi -p`). On `TASK-519` and `TASK-393` the first session recorded a plan, then every continuation answered only "I can't complete TASK-<n> in this turn/response ... it remains in doing" with no code, until the runner set `error` (`was unchanged`). Runs lasted about 100 s. Logs: `.git/chitty/run/TASK-519-20261121230420816936Z.log` and the latest `TASK-393-*.log`. Smaller tickets (`TASK-520`, 135 s) passed with the same model. Splitting the tickets worked around it. Ideas: say in the work guide and `continuation_prompt` (`src/chitty/run.py`) that the session has no turn limit and the agent should keep making tool calls and commit progress in steps; stop the loop or flag the model when several consecutive sessions end with no commit and this phrasing; record session count and commits in the usage log so the pattern is visible.

## Notes

Suggestion origin: chitty

## History

- 2026-11-22T09:47:34Z friendly-jade-stoat → backlog
- 2026-11-22T09:47:34Z friendly-jade-stoat: changed notes
