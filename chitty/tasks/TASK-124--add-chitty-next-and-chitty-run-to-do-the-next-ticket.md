---
title: Add `chitty next` and `chitty run` to do the next ticket
status: todo
priority: high
depends_on:
  - TASK-123
parent: TASK-106
created: 2026-11-03
---

## Description

One command to do the right next thing: review whatever needs reviewing, otherwise work the highest-priority ticket. Run it repeatedly to check things between tickets, or in a shell loop to go unattended.

`chitty next` prints the next action, for example `work TASK-12` (`--json` gives `{"mode", "id"}`), and exits non-zero with a message if there is none. Selection lives in `src/chitty/store.py` beside `ordered`:

1. Consider `review` tickets, then `doing`, then `todo`. `review` gives mode `review`; the others give `work`. Status wins over priority, because the human asked for reviews first and one ticket in work at a time means finishing `doing` first.
2. Within a status, take `high`, `medium`, `low`, then unset, then the lowest ticket number.
3. Exclude `backlog`, `blocked` and `done`; tickets in the `human` context or with owner `human`; and tickets with any `depends_on` entry not yet `done`. A done or archived dependency counts as met: `TASK-105` still lists the finished `TASK-107`.

`chitty run` calls that selection, runs `pi --chitty-<mode> <ID>` as a child process attached to the terminal, then reads the ticket again and prints the change, for example `TASK-12: todo → review`. Exit codes: 0 if the ticket's status changed; non-zero with a message if there is no next ticket, if `pi` is not installed or exits non-zero, or if the status did not change. A session that made no progress, such as one out of credits, therefore stops a loop instead of repeating. Pi's exit code alone cannot show this, because interactive shutdown always exits 0.

So `while chitty run; do :; done` is the loop, and needs no flag or code. `README.md` documents it.

Defaults chosen, cheap to change: Pi exits when a ticket finishes rather than staying open, because a loop needs it and the terminal keeps the transcript. The command is named `run` and only knows `pi`; `TASK-89` can extend it. Model choice is left to Pi's settings; for a specific model, run `chitty next` and call `pi` directly.

Keep `cli.py` thin. `next` also needs an MCP tool, since it is a read, but `run` does not, since it launches a harness.

Out of scope: label filters and role options from `TASK-76`, per-stage models, and detecting a `doing` ticket held by another live session.

## Acceptance Criteria

- [ ] Table-driven tests over a real temp repo cover selection order and every exclusion, including a met and an unmet dependency, and `HUMAN` tickets
- [ ] Tests run `chitty run` with a fake `pi` on `PATH`, covering each exit-code case: status changed, unchanged, `pi` failing, `pi` missing, and no next ticket
- [ ] `chitty next --json` and the MCP tool return the same answer
- [ ] `PLAN.md`, `README.md` and the `chitty --help` output describe both commands and the shell loop; `__version__` is bumped if `src/chitty/guide.md` changes

## History

- 2026-11-03T12:40:39Z lively-panda → todo
