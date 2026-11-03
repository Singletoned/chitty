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

### Log

One machine-local file per project, `$XDG_DATA_HOME/chitty/usage/<project>.jsonl`, defaulting like `inbox_path` in `src/chitty/config.py`. It is not in the repository, so appending cannot dirty the main checkout or conflict across branches, which `TASK-120` depends on. The trade-off is one history per machine, which suits a single developer.

`chitty run` in a repository with no `project` is a loud error in the `TASK-126` preflight, before anything changes. Remove the "skip the inbox pull with no `project`" branch and its test, which this makes unreachable, and give the run tests' repository a `project`.

One line per `chitty run` that reaches starting Pi, as one JSON object:

`{"ticket", "mode", "actor", "started" (UTC ISO 8601 ending `Z`, like History), "seconds", "status_before", "status_after", "models"}`

`models` is a list with one `{"provider", "model", "input", "output", "cacheRead", "cacheWrite", "cost"}` per provider and model, summed across the session and any subagent sessions. An empty list means Pi made no billed calls. `null` means unknown. `status_before` is the one `TASK-126` reads after the claim. `status_after` is `null` if the ticket cannot be read.

**Every path logs.** A session that cost money must not vanish, and dead and unchanged sessions are the expensive ones. Write the line in a `finally`, covering a non-zero `pi` exit, Ctrl-C, and the unchanged-status error. A failure to write the log warns on stderr and does not change the exit code.

### How it gets there

Pi records `provider`, `model` and `usage` on assistant messages, though `usage` may be absent on failed ones. `chitty run` is the only writer of the log, and the extension is the only code that knows Pi's format:

1. `chitty run` sets `CHITTY_USAGE_FILE` to a path in a temporary directory before starting Pi, and removes the directory afterwards.
2. On `session_shutdown`, if that variable is set, the extension sums all assistant messages in the session file by provider and model, using `ctx.sessionManager.getEntries()` so abandoned branches still count. It treats missing usage as zero. It reads the file if present, replaces its own session ID's entry in `{"sessions": {"<session id>": [<model entries>]}}`, and writes it back atomically with a rename. The handler catches its own errors and reports them with `ctx.ui.notify`.
3. After Pi exits, `chitty run` adds the sessions together for `models`. If the file is missing or invalid, it writes `models` null and warns on stderr.

Keying by session ID is deliberate. `session_shutdown` also fires on `/new`, `/fork` and reload, so one run can see it several times, and reload must not double count. Pi subagents inherit `CHITTY_USAGE_FILE`, so their cost is included under their own ID, which is right for cost per ticket.

### Rough relative cost

Use Pi's `usage.cost.total`. These are list prices from Pi's model data, not what a subscription actually charges, so they compare models and sessions but are not a bill. Keep token counts too, in case a price is missing or zero. Do not add `reasoning` tokens: they are already part of `output`.

Known limits, accepted for now: Pi sessions without `chitty run`, cold reads from Claude Code, and any compaction call Pi does not record as an assistant message are not counted. A crash, or `kill -INT` with no TTY, gives `models` null, because `session_shutdown` does not fire.

Out of scope: any report (`TASK-111` reads this log), budgets, and non-Pi harnesses.

## Acceptance Criteria

- [ ] A test covers a repository with no `project`: `chitty run` exits non-zero before starting `pi`
- [ ] The log is written under a temporary `XDG_DATA_HOME` in tests, and a test shows `git status` in the repository stays clean after a run
- [ ] Run by hand in a scratch repository: a real Pi session produces a line whose cost is close to the sum in its session file, recorded in a note
- [ ] `PLAN.md` and `README.md` describe the log and say its costs are list prices; `__version__` is bumped so `chitty init` installs the extension
- [ ] Tests with a fake `pi` that writes the usage file show one complete line with every field, two models summed across two session IDs, and a second run appending rather than overwriting
- [ ] Tests show a line is still written, with `models` null and a warning on stderr, for a missing and an invalid usage file, and with `status_after` correct for a `pi` that exits non-zero, a Ctrl-C and an unchanged status, each keeping its exit code
- [ ] Node tests show the extension summing every field by provider and model, tolerating a message with no usage, counting abandoned branches, keeping another session ID in the file, replacing its own on a second shutdown, and writing nothing when `CHITTY_USAGE_FILE` is unset

## Notes

As in `TASK-126`, the logged status before is the one read after the claim, immediately before starting Pi.

Cold read by a fresh Sonnet subagent, 2026-11-03. Biggest finds: writing the line after the status check would have skipped the dead sessions the log most needs; `session_shutdown` fires several times in one run, which would have lost or double counted cost; subagents inherit the variable and would have overwritten the file. It confirmed from Pi source that `session_shutdown` does fire and can finish a write on `ctx.shutdown()`, double Ctrl-C and SIGTERM. Note that double Ctrl-C in the TUI exits 0 and reports as unchanged, not `RunInterrupted`. Author choices: keying by session ID and including subagent cost.

## History

- 2026-11-03T16:46:06Z lively-panda → todo
- 2026-11-03T16:49:00Z lively-panda: changed notes
- 2026-11-03T18:19:35Z lively-panda: changed description, acceptance criteria, notes
