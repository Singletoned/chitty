---
title: Explain an agent that exits without changing the ticket
status: backlog
created: 2026-11-23
---

## Description

In taidy (2026-11-22), `agent_command` was `pi --no-extensions -e ~/.pi/agent/extensions/chitty.ts --chitty-{mode} {id}`. `chitty run` starts agents with `stdin=subprocess.DEVNULL` (`run.py`), and `chitty.ts` only starts a ticket when `ctx.mode === "tui"`, so pi exited within seconds and both TASK-21 (review) and TASK-4 (work) went to `error` with only `TASK-21 was unchanged; only committed changes are visible to chitty run`. The pi session directory was created but empty. Fixed by switching to `uv run --no-sync pi -p --no-extensions {prompt}`. Suggestions: (1) when the agent exits in under a minute with no change, include its exit code and the last lines of its output in the error note; (2) have `chitty init` or `chitty check` warn about an `agent_command` using `--chitty-{mode} {id}` with the pi extension, since it cannot work non-interactively.

## Notes

Suggestion origin: taidy

Folded in from TASK-622 and TASK-623: four worker runs and a reviewer run in circuitry (2026-11-14) ended `was unchanged` with no cause; in echonomicon (2026-11-22) the agent never started because `uv run` failed to parse a conflicted `pyproject.toml`, and the log began with `uv` output. Report "agent could not start" apart from "agent failed".

## History

- 2026-11-23T10:24:02Z witty-russet-gannet → backlog
- 2026-11-23T10:24:04Z witty-russet-gannet: changed notes
- 2026-11-23T10:27:34Z witty-russet-gannet: changed notes
