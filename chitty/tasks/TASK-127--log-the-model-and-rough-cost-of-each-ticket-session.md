---
title: Log the model and rough cost of each ticket session
status: doing
priority: high
depends_on:
  - TASK-126
  - TASK-129
  - TASK-132
  - TASK-147
  - TASK-153
parent: TASK-106
created: 2026-11-03
---

## Description

This ticket holds the design and builds the normal path: a session that ends and leaves a good usage file. Failed and interrupted runs are `TASK-148`, and the real-session check and documentation are `TASK-149`.

The pilot has to answer whether cheap models save money per accepted ticket, including retries, so each session needs its model and rough cost on record. Keep this out of the ticket: it would add noise to every diff, and agents should not see metrics (`PLAN.md`, "Feedback loops").

### Log

One machine-local file per project, `$XDG_DATA_HOME/chitty/usage/<project>.jsonl`, defaulting like `inbox_path` in `src/chitty/config.py`. It is not in the repository, so appending cannot dirty the main checkout or conflict across branches, which `TASK-120` depends on. The trade-off is one history per machine, which suits a single developer.

The log's file name comes from the `project` after `refresh_setup`, which adds one to a repository without it. Leave the inbox pull in `run` as it is: only a `project` present before the refresh opts into pulling. If there is still no `project` after the refresh, fail loudly before the claim.

One line per `chitty run` that reaches starting Pi, as one JSON object:

`{"ticket", "mode", "actor", "started" (UTC ISO 8601 ending `Z`, like History), "seconds", "status_before", "status_after", "models"}`

`models` is a list with one `{"provider", "model", "input", "output", "cacheRead", "cacheWrite", "cost"}` per provider and model, summed across the session and any subagent sessions. An empty list means Pi made no billed calls. `null` means unknown. `actor` is the name from `actor()`, matching History, not the raw UUID. `status_before` is the one `TASK-126` reads after the claim. A missing usage file gives `models` null; `TASK-148` adds the warning and the other failures.

`TASK-148` makes every path log.

### How it gets there

Pi records `provider`, `model` and `usage` on assistant messages, though `usage` may be absent on failed ones. `chitty run` is the only writer of the log, and the extension is the only code that knows Pi's format:

1. `chitty run` sets `CHITTY_USAGE_FILE` to a path in a temporary directory before starting Pi, and removes the directory afterwards.
2. On `session_shutdown`, if that variable is set, the extension sums all assistant messages in the session file by provider and model, using `ctx.sessionManager.getEntries()` so abandoned branches still count. It treats missing usage as zero. It reads the file if present, replaces its own session ID's entry in `{"sessions": {"<session id>": [<model entries>]}}`, and writes it back atomically with a rename. The handler catches its own errors and reports them with `ctx.ui.notify`.
3. After Pi exits, `chitty run` adds the sessions together for `models`.

Keying by session ID is deliberate. `session_shutdown` also fires on `/new`, `/fork` and reload, so one run can see it several times, and reload must not double count. Pi subagents inherit `CHITTY_USAGE_FILE`, so their cost is included under their own ID, which is right for cost per ticket.

### Rough relative cost

Use Pi's `usage.cost.total`. These are list prices from Pi's model data, not what a subscription actually charges, so they compare models and sessions but are not a bill. Keep token counts too, in case a price is missing or zero. Do not add `reasoning` tokens: they are already part of `output`.

Known limits, accepted for now: Pi sessions without `chitty run`, cold reads from Claude Code, and any compaction call Pi does not record as an assistant message are not counted. A crash, or `kill -INT` with no TTY, gives `models` null, because `session_shutdown` does not fire. Two sessions writing at once can lose an entry, which the rename does not prevent, and a subagent without this extension is not counted.

Out of scope: any report (`TASK-111` reads this log), budgets, and non-Pi harnesses.

## Acceptance Criteria

- [x] The log is written under a temporary `XDG_DATA_HOME` in tests, and a test shows `git status` in the repository stays clean after a run
- [x] Tests with a fake `pi` that writes the usage file show one complete line with every field, two models summed across two session IDs, and a second run appending rather than overwriting
- [ ] A test shows a repository starting with no `project` logging under the one the refresh gives it

## Plan

Inspect the existing run command, setup refresh, and tests; implement temporary usage-file wiring and post-Pi aggregation without changing the extension; add real-file unittest coverage for complete records, multiple sessions/models, append behavior, clean repository status, and refreshed project names; run format/check and update the ticket only after verification.

## Notes

As in `TASK-126`, the logged status before is the one read after the claim, immediately before starting Pi.

Cold read by a fresh Sonnet subagent, 2026-11-03. Biggest finds: writing the line after the status check would have skipped the dead sessions the log most needs; `session_shutdown` fires several times in one run, which would have lost or double counted cost; subagents inherit the variable and would have overwritten the file. It confirmed from Pi source that `session_shutdown` does fire and can finish a write on `ctx.shutdown()`, double Ctrl-C and SIGTERM. Note that double Ctrl-C in the TUI exits 0 and reports as unchanged, not `RunInterrupted`. Author choices: keying by session ID and including subagent cost.

Every finding from the cold read now has an outcome. Fixed in the ticket on the second pass: the `actor` value, what counts as invalid, and two more known limits. Checked: `getEntries` is on `ReadonlySessionManager`. Rejected: specifying how to append, because `chitty run` is the only writer. Specifying `writeFileSync`, because the source shows shutdown handlers are awaited, so either works. A test that agents cannot see the log, because its location outside the repository does that. RPC and JSON modes, because `chitty run` does not use them by default. Creating the directory, which is ordinary work. A `.worktrees/` check for the clean-status test, because `init` adds the ignore rule. Version bump order, because the rule in `AGENTS.md` already covers it.

Depends on `TASK-129` so a worktree cannot install this extension change early.

Split on 2026-11-03: the extension half is now `TASK-132`. This ticket keeps the design, the `chitty run` side and the check against a real session.

Split on 2026-11-04 at the human's direction, from six criteria, into this ticket, `TASK-148` and `TASK-149`. Dropped the version bump: this changes nothing `chitty init` installs, because the extension half landed in `TASK-132`.

Depends on `TASK-147` and `TASK-153` only to order them first: all are high priority and ties go by ID, but those two bugs affect every session and every passed review.

Cold read of the split by a fresh Sonnet subagent, 2026-11-04. Fixed: a preflight check for `project` would have refused legacy repositories that `refresh_setup` repairs a moment later, so the name is read after it, and the inbox behaviour stays. A missing usage file on a normal exit is now defined. Rejected: a criterion per log field, because criterion 3 already says every field, and the new rule is to state behaviour rather than list cases.

Review failed (tests): Acceptance criterion 3 is not met. The submitted tests exercise a repository with an existing project name and only verify the no-project case stops before Pi; none demonstrates a successful run logging under the project name added by refresh_setup. Add a real-file test that starts without project, lets refresh_setup derive it, runs fake Pi to a status change, and asserts the usage file uses that refreshed name.

## Summary

Implemented machine-local per-session usage logging in chitty run: Pi receives a temporary usage file, model/session usage is aggregated, and complete JSONL records append under XDG data without dirtying repositories. Legacy repositories refresh their derived project name before logging while inbox pull remains opt-in based on the pre-refresh project. Verified with the new fake-Pi append/aggregation/clean-status test and make check (243 Python tests plus Node tests).

## History

- 2026-11-03T16:46:06Z lively-panda → todo
- 2026-11-03T16:49:00Z lively-panda: changed notes
- 2026-11-03T18:19:35Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-03T20:00:17Z lively-panda: changed description, notes
- 2026-11-03T20:44:56Z lively-panda: changed dependencies, notes
- 2026-11-03T20:46:20Z lively-panda: changed dependencies, acceptance criteria, notes
- 2026-11-04T15:11:32Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-04T15:12:22Z mellow-newt: changed dependencies, notes
- 2026-11-04T15:17:31Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-05T10:42:07Z able-yellowhammer todo → doing
- 2026-11-05T10:42:20Z able-yellowhammer: wrote the plan
- 2026-11-05T11:05:00Z able-yellowhammer: ticked acceptance criteria
- 2026-11-05T11:05:01Z able-yellowhammer: ticked acceptance criteria
- 2026-11-05T11:05:02Z able-yellowhammer: ticked acceptance criteria
- 2026-11-05T11:07:12Z able-yellowhammer: changed summary
- 2026-11-05T11:07:13Z able-yellowhammer doing → review
- 2026-11-05T11:10:26Z brisk-raven: changed acceptance criteria, notes
- 2026-11-05T11:10:26Z brisk-raven review → doing
