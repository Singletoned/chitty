---
title: Log usage for `claude` sessions
status: doing
priority: medium
depends_on:
  - TASK-148
parent: TASK-106
created: 2026-11-04
---

## Description

`TASK-127` logs each session's model and cost, using a Pi extension to write `CHITTY_USAGE_FILE`, so `claude` sessions log `models` as null. Pi and Claude cannot be compared per ticket without this, and comparing them is the reason for having both.

Keep the agent's format out of `src/chitty/run.py`: the integration writes the file in the shape `TASK-127` defines, and `run.py` only reads it. Put the code in `src/chitty/integrations/claude/usage.py`, and call it from a command declared with `hidden=True`, `chitty claude-usage-hook`, which reads the hook's JSON from stdin and does not open a repository, because the working directory need not be one. A command avoids finding a script's path from `chitty.toml`, and hiding it keeps it out of `chitty --help`. `TASK-158` loads it in the `claude` command with these settings for `--settings`:

```json
{"hooks":{"SessionEnd":[{"hooks":[{"type":"command","command":"chitty claude-usage-hook"}]}]}}
```

If `CHITTY_USAGE_FILE` is unset, the hook does nothing. Otherwise it reads `session_id` and `transcript_path` from stdin, and sums the `assistant` lines of the transcript and of `<transcript without .jsonl>/subagents/agent-*.jsonl` by `message.model`:

- One API message spans several transcript lines with the same `message.id` and the same usage, so count each ID once, across the transcript and its subagents. A real transcript had 27 IDs on 69 lines, so summing lines overcounts about 2.5 times.
- Map `input_tokens` to `input`, `output_tokens` to `output`, `cache_read_input_tokens` to `cacheRead`, and `cache_creation_input_tokens` to `cacheWrite`. The provider is `anthropic`.
- Missing or null token fields count as zero.
- Transcripts hold no cost (checked 2026-11-04), and a price table would go stale, so `cost` is null, which `TASK-148` makes valid.
- No assistant messages gives an empty list, as `TASK-127` defines.

Write the file as `TASK-127` says: replace this session's entry, keep others, and rename atomically. A missing subagent directory is normal. The hook must not fail the session: on any error, including an existing usage file that is invalid, which it leaves alone, or stdin missing `session_id`, it reports on stderr and exits 0.

Tests write their own sample transcripts with the fields above, because workers cannot read `~/.claude`. No `__version__` bump: nothing here reaches a repository through `chitty init`.

Known limits, accepted as they are for Pi: a killed `claude` runs no hook, so `models` is null, Claude Code has a time limit on `SessionEnd` hooks, and a branch older than this command has no hook to run. `TASK-158` connects this to the real command, documents it and checks a real session.

## Acceptance Criteria

- [ ] A test feeds the hook a sample transcript with a repeated message ID and a subagent, and shows the file it writes, keyed by session and summed by model with the tokens mapped and `cost` null
- [ ] Tests show the hook exiting 0 with a message on stderr for a missing or malformed transcript, an invalid usage file and stdin with no `session_id`, doing nothing with `CHITTY_USAGE_FILE` unset, and keeping another session's entry

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. It read real transcripts. Fixed: one API message spans several lines, so summing lines would overcount about 2.5 times; subagent transcripts' location; the field mapping; and null cost, including in `run.py`. I chose a hidden command, because the hook needs a stable way to run from any repository; the alternatives are a machine path in `chitty.toml`, or `python -m`, which the global tool's interpreter would not serve. The real-session criterion moved to `TASK-158`, because a worker cannot start `claude`. Rejected: filtering on the hook's `reason`, because keying by session ID makes a repeat harmless.

Second cold read by a fresh Sonnet subagent, 2026-11-04. It confirmed that the `--settings` JSON survives TOML and `shlex.split` when written as a basic string with `\"` inside shell single quotes. Fixed by making this smaller: reading a null cost moved to `TASK-148`, whose code it changes, and connecting the command and documentation moved to `TASK-158`, which also removes a contradiction between the two. Also fixed: the literal settings JSON, not opening a repository, deduplicating across files, zero for missing tokens, invalid usage file, stdin missing `session_id`, and test fixtures. Rejected: a test that the command is hidden, which a reviewer sees in one line; hiding from completion, which `hidden=True` decides; and atomic rename as a test, because `TASK-127` already requires it.

## History

- 2026-11-04T17:58:12Z mellow-newt → backlog
- 2026-11-04T18:01:17Z mellow-newt: changed dependencies, description, acceptance criteria, notes
- 2026-11-04T18:03:07Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-04T18:03:08Z mellow-newt backlog → todo
- 2026-11-05T22:10:19Z intrepid-kestrel todo → doing
