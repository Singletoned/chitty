---
title: Log the model and rough cost of each ticket session
status: todo
priority: high
depends_on:
  - TASK-126
parent: TASK-106
created: 2026-11-03
---

## Description

The pilot has to answer whether cheap models save money per accepted ticket, including retries, so each session needs its model and rough cost on record. Keep this out of the ticket: it would add noise to every diff, and agents should not see metrics (`PLAN.md`, "Feedback loops").

**Log.** One machine-local file per project, `$XDG_DATA_HOME/chitty/usage/<project>.jsonl`, defaulting like `inbox_path` in `src/chitty/config.py`. It is not in the repository, so appending cannot dirty the main checkout or conflict across branches, which `TASK-120` depends on. The trade-off is one history per machine, which suits a single developer. `chitty run` in a repository with no `project` is a loud error.

**One line per `chitty run` session:** ticket ID, mode, actor, start time, duration in seconds, ticket status before and after, and a list of `{provider, model, input, output, cacheRead, cacheWrite, cost}` totals with one entry per model, since a session can change model.

**How it gets there.** Pi already records `provider`, `model` and `usage` on every assistant message, including `usage.cost.total`. `chitty run` is the only writer, and the extension is the only code that knows Pi's format:

1. `chitty run` sets `CHITTY_USAGE_FILE` to a temporary path before starting Pi.
2. On `session_shutdown`, if that variable is set, the extension sums the session's assistant messages by provider and model and writes them there as JSON.
3. After Pi exits, `chitty run` appends the line. If the file is missing or invalid, as after a crash, it still appends the line with `models` null and prints a warning, because a session that cost money must not vanish. This does not change the exit code.

**Rough relative cost.** Use Pi's `cost` figures. They are list prices from Pi's model data, not what a subscription actually charges, so they compare models and sessions but are not a bill. Keep token counts too, in case a price is missing or zero.

Known limits, accepted for now: `pi` run without `chitty run` is not logged, and neither are subagents with their own sessions or cold reads run from Claude Code.

Out of scope: any report (`TASK-111` reads this log), budgets, and non-Pi harnesses.

## Acceptance Criteria

- [ ] Tests with a fake `pi` that writes the usage file show `chitty run` appending one complete line, including the before and after status and an entry for each of two models
- [ ] Tests cover a missing and an invalid usage file: a line with `models` null is still appended, a warning is printed, and the exit code is unaffected
- [ ] A test covers a repository with no `project`: `chitty run` exits non-zero before starting `pi`
- [ ] The log is written under a temporary `XDG_DATA_HOME` in tests, and a test shows `git status` in the repository stays clean after a run
- [ ] A Node test shows the extension summing assistant messages by provider and model, and writing nothing when `CHITTY_USAGE_FILE` is unset
- [ ] Run by hand in a scratch repository: a real Pi session produces a line whose cost is close to the sum in its session file, recorded in a note
- [ ] `PLAN.md` and `README.md` describe the log and say its costs are list prices; `__version__` is bumped so `chitty init` installs the extension

## Notes

As in `TASK-126`, the logged status before is the one read after the claim, immediately before starting Pi.

## History

- 2026-11-03T16:46:06Z lively-panda → todo
- 2026-11-03T16:49:00Z lively-panda: changed notes
