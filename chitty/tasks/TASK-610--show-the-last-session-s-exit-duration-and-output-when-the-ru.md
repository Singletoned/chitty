---
title: Show the last session's exit, duration and output when the runner stops an agent that made no progress
status: cold-read
depends_on:
  - TASK-617
created: 2026-11-23
---

## Description

When an agent exits 0 without changing its ticket and the runner gives up (`_agent_sessions`, `src/chitty/run.py`), the note says only that the ticket is unchanged (reworded by TASK-617 to `<ID> is still `<status>` after N continuations with no new work committed; ...`). Nothing says why. In taidy (2026-11-22) pi exited within seconds because its extension only runs in interactive mode, and the note gave no clue; in circuitry (2026-11-14) five runs ended the same way with no cause recorded. A non-zero exit already includes the output (`AgentSessionFailed`, `run.py:813`); a zero exit does not.

Change:

- `_run_session` returns what the last session did: its exit status, duration in seconds (rounded to whole seconds) and output (`completed.stdout`, already captured from the log by `_run_agent`, `run.py:306`).
- When `_agent_sessions` stops (the cap in TASK-617, or an agent that cannot be continued), build the error with a pure function `stalled_agent_message(first_line: str, seconds: int, returncode: int, output: str) -> str`: the first line is the stop message, then `last session: exit <returncode> after <seconds>s`, then the last `AGENT_OUTPUT_TAIL_LINES` (a new module constant, 40) lines of the output, or `(no output)`. `_runner_error_note` (`run.py:1417`) already puts lines after the first in a fenced block.

Property tool: Hypothesis.

Out of scope: detecting why an agent could not start, and warning in `chitty init` about particular agent commands.

## Acceptance Criteria

- [ ] A pure function `stalled_agent_message(first_line, seconds, returncode, output)` in `src/chitty/run.py` is tested with Hypothesis in a new file `tests/test_stalled_agent_message.py`: for any output text (including empty, no trailing newline, and more than 40 lines), the result's first line is `first_line`, it contains `last session: exit <returncode> after <seconds>s`, and it ends with exactly the last `min(40, line count)` lines of the output; empty output gives `(no output)`.
- [ ] In `tests/test_run_continue.py`, an agent that prints `STALL_MARKER` and exits 0 without changing the ticket ends in `error`, and the ticket's newest note has the stop message as its heading and a fenced block containing `last session: exit 0` and `STALL_MARKER`. This fails on `main`, whose note has no agent output.

## Notes

Suggestion origin: taidy

Folded in from TASK-622 and TASK-623: four worker runs and a reviewer run in circuitry (2026-11-14) ended `was unchanged` with no cause; in echonomicon (2026-11-22) the agent never started because `uv run` failed to parse a conflicted `pyproject.toml`, and the log began with `uv` output. Report "agent could not start" apart from "agent failed".

Planning: relies on TASK-617 (its stop rule, 6-invocation cap and message). When TASK-617 is done, compare this ticket with what landed, cold-read it again, then move it to `todo`.

## History

- 2026-11-23T10:24:02Z witty-russet-gannet → backlog
- 2026-11-23T10:24:04Z witty-russet-gannet: changed notes
- 2026-11-23T10:27:34Z witty-russet-gannet: changed notes
- 2026-11-23T10:36:30Z witty-russet-gannet: changed title, dependencies, description, acceptance criteria
- 2026-11-23T10:36:30Z witty-russet-gannet backlog → planning
- 2026-11-23T10:36:40Z witty-russet-gannet planning → cold-read
- 2026-11-23T10:38:13Z witty-russet-gannet: changed notes
