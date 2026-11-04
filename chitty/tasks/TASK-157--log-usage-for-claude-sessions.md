---
title: Log usage for `claude` sessions
status: backlog
priority: medium
depends_on:
  - TASK-148
parent: TASK-106
created: 2026-11-04
---

## Description

`TASK-127` logs each session's model and cost, using a Pi extension to write `CHITTY_USAGE_FILE`, so `claude` sessions log `models` as null. Pi and Claude cannot be compared per ticket without this, and comparing them is the reason for having both.

Keep the agent's format out of `src/chitty/run.py`: the integration writes the same file in the same shape. Put the code in `src/chitty/integrations/claude/usage.py`, and call it from a hidden `chitty claude-usage-hook` command that reads the hook's JSON from stdin. A command avoids finding a script's path from `chitty.toml`, because `chitty` is on `PATH` wherever `chitty run` works, and hiding it keeps it out of `chitty --help`. The `claude` command loads it as a `SessionEnd` hook by passing the settings as JSON to `--settings`, which adds to a person's own settings.

If `CHITTY_USAGE_FILE` is unset, the hook does nothing. Otherwise it reads `session_id` and `transcript_path` from stdin, and sums the `assistant` lines of the transcript and of `<transcript without .jsonl>/subagents/agent-*.jsonl` by `message.model`:

- One API message spans several transcript lines with the same `message.id` and the same usage, so count each ID once. A real transcript had 27 IDs on 69 lines, so summing lines overcounts about 2.5 times.
- Map `input_tokens` to `input`, `output_tokens` to `output`, `cache_read_input_tokens` to `cacheRead`, and `cache_creation_input_tokens` to `cacheWrite`. The provider is `anthropic`.
- Transcripts hold no cost (checked 2026-11-04), and a price table would go stale, so `cost` is null. `chitty run`'s reading of the file must accept that, and a sum with any null `cost` is null. Tokens are still summed.
- No assistant messages gives an empty list, as `TASK-127` defines.

Write the file as `TASK-127` says: replace this session's entry, keep others, and rename atomically. The hook must not fail the session: on any error it reports on stderr and exits 0.

Known limits, accepted as they are for Pi: a killed `claude` runs no hook, so `models` is null, and Claude Code has a time limit on `SessionEnd` hooks. `TASK-158` checks a real session.

## Acceptance Criteria

- [ ] `README.md` shows the `--settings` part of the `claude` command, and this repository's command uses it
- [ ] A test feeds the hook a sample transcript with a repeated message ID and a subagent, and shows `chitty run`'s log line summed by model with `cost` null
- [ ] Tests show the hook exiting 0 with a message on stderr for a missing or malformed transcript, doing nothing with `CHITTY_USAGE_FILE` unset, and keeping another session's entry

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. It read real transcripts. Fixed: one API message spans several lines, so summing lines would overcount about 2.5 times; subagent transcripts' location; the field mapping; and null cost, including in `run.py`. I chose a hidden command, because the hook needs a stable way to run from any repository; the alternatives are a machine path in `chitty.toml`, or `python -m`, which the global tool's interpreter would not serve. The real-session criterion moved to `TASK-158`, because a worker cannot start `claude`. Rejected: filtering on the hook's `reason`, because keying by session ID makes a repeat harmless.

## History

- 2026-11-04T17:58:12Z mellow-newt → backlog
- 2026-11-04T18:01:17Z mellow-newt: changed dependencies, description, acceptance criteria, notes
