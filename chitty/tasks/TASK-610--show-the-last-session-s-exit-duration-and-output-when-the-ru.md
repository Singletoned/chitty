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

- `_run_session` returns what the session did: its exit status, duration (measured with `time.monotonic()` around the `_run_agent` call, rounded to whole seconds) and output (`completed.stdout`, which `_run_agent` reads from the log offset where that session began, so it holds that session only). `_agent_sessions` keeps the result of each `_run_session` call in its loop, starting with the first, and uses the latest at the stop. Round the duration with `round()`; it is not tested, because the measured time is not deterministic.
- When `_agent_sessions` stops (the `continuation_step(...) == "stop"` cap from TASK-617, or `not _accepts_prompt(...)`; both raise the same `ChittyError`), build the error with a pure function `stalled_agent_message(first_line: str, seconds: int, returncode: int, output: str) -> str`: the first line is the stop message, then `last session: exit <returncode> after <seconds>s`, then the last `AGENT_OUTPUT_TAIL_LINES` (a new module constant, 40) lines of the output, or `(no output)` when the output is the empty string. The caller decodes `completed.stdout` (bytes) with `decode(errors="replace")`, treating empty or missing output as `""`, as `_run_session` already does for failures; the function then uses the text unmodified (no `strip()`). It joins its lines with `\n`, so the result is `\n`.join of the first line, the `last session` line and the tail lines (or `(no output)`). `returncode` is always 0 at a stop in practice, because a non-zero exit or a timeout raises inside `_run_session` first; do not add a separate path for non-zero codes. `_runner_error_note` (`src/chitty/run.py`) already puts lines after the first in a fenced block, under the heading `Runner error (<phase>): <first line>`. Lines are counted with `str.splitlines()`, as `_runner_error_note` does; whitespace-only output counts as output. The stop stays a plain `ChittyError`: an `AgentSessionFailed` would be turned into `AgentStartFailed` by the `except AgentSessionFailed` handler in the caller of `_agent_sessions`.

Property tool: Hypothesis.

Out of scope: detecting why an agent could not start, and warning in `chitty init` about particular agent commands.

## Acceptance Criteria

- [ ] A pure function `stalled_agent_message(first_line, seconds, returncode, output)` in `src/chitty/run.py` is tested with Hypothesis in a new file `tests/test_property_stalled_agent_message.py`: for `first_line` drawn from `st.text().filter(lambda s: s.splitlines() in ([], [s]))`, any non-negative `seconds`, any integer return code and any output text (including empty, whitespace-only, carriage-return, form-feed and Unicode line-separator characters, trailing blank lines, no trailing newline, and more than 40 lines), with `tail = output.splitlines()[-40:]`: `result.split("\n")[0] == first_line`, `result.split("\n")[1] == f"last session: exit {returncode} after {seconds}s"`, and `result.split("\n")[2:] == tail` when `output` is not empty, or `== ["(no output)"]` when it is.
- [ ] In `tests/test_run_continue.py`, a new fake-agent `edit` snippet (passed to `write_fake`, like `NO_CHANGE`) prints `OLD_MARKER` to stdout when not continued and `STALL_MARKER` when continued (`continued` in `FAKE_AGENT`), and never changes the ticket. `run --ticket` ends with the ticket in `error`. Take the Notes text (`self.json("show", ticket)["notes"]`, one string) from its last `Runner error (agent): ` onwards: that line continues with the stop message from `_agent_sessions` (it contains `continuations with no new work committed`), and the text after it, under `Error output:`, contains `last session: exit 0` and `STALL_MARKER`, and not `OLD_MARKER`. This fails on `main`, whose note has no agent output.
- [ ] `test_command_without_prompt_is_not_continued` (`tests/test_run_continue.py`) keeps its `after 0 continuations with no new work committed` assertion and also asserts that the Notes text from its last `Runner error (agent): ` onwards contains `last session: exit 0 after`.

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
- 2026-11-23T13:44:47Z youthful-quartz-zander cold-read → planning
- 2026-11-23T13:45:02Z youthful-quartz-zander: changed description
- 2026-11-23T13:45:15Z youthful-quartz-zander: changed acceptance criteria
- 2026-11-23T13:45:30Z youthful-quartz-zander planning → cold-read
- 2026-11-23T13:46:55Z youthful-quartz-zander cold-read → planning
- 2026-11-23T13:46:58Z youthful-quartz-zander: changed description
- 2026-11-23T13:47:01Z youthful-quartz-zander: changed acceptance criteria
- 2026-11-23T13:47:10Z youthful-quartz-zander planning → cold-read
- 2026-11-23T13:49:09Z youthful-quartz-zander cold-read → planning
- 2026-11-23T13:49:14Z youthful-quartz-zander: changed acceptance criteria
- 2026-11-23T13:49:25Z youthful-quartz-zander planning → cold-read
