---
title: Log usage for `claude` sessions
status: backlog
priority: medium
depends_on:
  - TASK-148
  - TASK-155
parent: TASK-106
created: 2026-11-04
---

## Description

`TASK-127` logs each session's model and cost, using a Pi extension to write `CHITTY_USAGE_FILE`, so `claude` sessions log `models` as null. Pi and Claude cannot be compared per ticket without this, and comparing them is the reason for having both.

Keep `chitty run` unaware of the agent: the integration writes the same file in the same shape. Add a `SessionEnd` hook under `src/chitty/integrations/claude/`, which the `claude` command loads with `--settings`. If `CHITTY_USAGE_FILE` is set, it sums usage by model from the transcript the hook is given, and any subagent transcripts, and writes the file atomically, keyed by session ID as the Pi extension does. It uses `anthropic` as the provider.

The transcript is believed to hold tokens but not cost, which must be checked first. Do not add a price table that would go stale. If there is no cost, write `cost` as null, and `chitty run` must accept that as a known token count with an unknown cost.

The hook must not fail the session: it reports errors on stderr.

## Acceptance Criteria

- [ ] A test feeds a sample transcript with a subagent to the hook and shows the file `chitty run` then logs, summed by model
- [ ] A note compares a real `claude` session's log line with its transcript and explains any difference, and says where cost came from or that it is unknown
- [ ] `README.md` shows the `--settings` part of the `claude` command, and this repository's command uses it

## History

- 2026-11-04T17:58:12Z mellow-newt → backlog
