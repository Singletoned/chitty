---
title: Show the last session's exit, duration and output when the runner stops an agent that made no progress
status: cold-read
depends_on:
  - TASK-617
created: 2026-11-23
---

## Description

When an agent exits 0 without changing its ticket and the runner gives up (`_agent_sessions`, `src/chitty/run.py`), the note says only that the ticket is unchanged (reworded by TASK-617 to `<ID> is still `<status>` after N continuations with no new work committed; ...`). Nothing says why. In taidy (2026-11-22) pi exited within seconds because its extension only runs in interactive mode, and the note gave no clue; in circuitry (2026-11-14) five runs ended the same way with no cause recorded. A non-zero exit already includes the output (the `AgentSessionFailed` raised at the end of `_run_session`); a zero exit does not.

Change:

- `_run_session` returns what the session did: its exit status, duration (measured with `time.monotonic()` around the `_run_agent` call, rounded to whole seconds) and output (`completed.stdout`, which `_run_agent` reads from the log offset where that session began, so it holds that session only). `_agent_sessions` keeps the latest result, including from the first call before the loop, and uses it at the stop.
- When `_agent_sessions` stops (the `continuation_step(...) == "stop"` cap from TASK-617, or `not _accepts_prompt(...)`; both raise the same `ChittyError`), build the error with a pure function `stalled_agent_message(first_line: str, seconds: int, returncode: int, output: str) -> str`: the first line is the stop message, then `last session: exit <returncode> after <seconds>s`, then the last `AGENT_OUTPUT_TAIL_LINES` (a new module constant, 40) lines of the output, or `(no output)`. `_runner_error_note` (`src/chitty/run.py`) already puts lines after the first in a fenced block, under the heading `Runner error (<phase>): <first line>`. Lines are counted with `str.splitlines()`, as `_runner_error_note` does; whitespace-only output counts as output. The stop stays a plain `ChittyError`: an `AgentSessionFailed` would be turned into `AgentStartFailed` by the `except AgentSessionFailed` handler in the caller of `_agent_sessions`.

Property tool: Hypothesis.

Out of scope: detecting why an agent could not start, and warning in `chitty init` about particular agent commands.

## Acceptance Criteria

- [ ] A pure function `stalled_agent_message(first_line, seconds, returncode, output)` in `src/chitty/run.py` is tested with Hypothesis in a new file `tests/test_property_stalled_agent_message.py`: for any output text (including empty, whitespace-only, carriage-return, form-feed and Unicode line-separator characters, no trailing newline, and more than 40 lines) and any integer return code, the result starts with the line `first_line`, contains `last session: exit <returncode> after <seconds>s`, and ends with exactly the last `min(40, len(output.splitlines()))` lines of `output.splitlines()`; empty output gives `(no output)`.
- [ ] In `tests/test_run_continue.py`, a new fake-agent `edit` snippet (passed to `write_fake`, like `NO_CHANGE`) prints `OLD_MARKER` to stdout when not continued and `STALL_MARKER` when continued (`continued` in `FAKE_AGENT`), and never changes the ticket. `run --ticket` ends with the ticket in `error`; its newest note's first line is `Runner error (agent): ` followed by the stop message from `_agent_sessions` (it contains `continuations with no new work committed`), and the note has a fenced block containing `last session: exit 0` and `STALL_MARKER`, and not `OLD_MARKER`. This fails on `main`, whose note has no agent output.
- [ ] `test_command_without_prompt_is_not_continued` (`tests/test_run_continue.py`) also asserts the note contains `last session: exit 0 after`.

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
- 2026-11-23T10:38:29Z witty-russet-gannet: changed description, acceptance criteria
- 2026-11-23T10:38:29Z witty-russet-gannet cold-read → planning
- 2026-11-23T13:38:33Z youthful-quartz-zander: changed description
- 2026-11-23T13:38:39Z youthful-quartz-zander: changed acceptance criteria
- 2026-11-23T13:38:56Z youthful-quartz-zander: changed acceptance criteria
- 2026-11-23T13:42:04Z youthful-quartz-zander planning → cold-read
