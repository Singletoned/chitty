---
title: Stop `chitty run` instead of marking a ticket `error` when the agent cannot start
status: backlog
created: 2026-11-21
---

## Description

On 2026-11-20 a work loop was started as `chitty run --loop --mode work -- --model gpt-6.2-terra`, a model Pi does not have (`pi --list-models` lists `gpt-6.1-terra` and `gpt-6.2-sol`). Pi exited at once with `Error: Model "gpt-6.2-terra" not found`, and the runner recorded that as a ticket failure: TASK-384 and TASK-474, both freshly `todo`, went `doing` → `error` within a minute, each with a "Runner error (agent)" note on its branch. Nothing was wrong with either ticket, and the loop kept running, so every `todo` ticket it reaches will be marked the same way. A misconfigured agent command is a runner problem, not a ticket problem. Options: check the model before the loop starts (for Pi, against `--list-models`), or treat an agent exit within a few seconds with no commits as a start failure that stops the loop and leaves the ticket `todo`.

## Notes

Suggestion origin: chitty

## History

- 2026-11-21T07:57:47Z nimble-umber-gannet → backlog
- 2026-11-21T07:57:48Z nimble-umber-gannet: changed notes
