---
title: Add a `waiting` status maintained from `depends_on`
status: todo
created: 2026-11-01
---

## Description

A `blocked` task stays blocked after the tasks it depends on are done, because nothing notices (circuitry, 2026-11-01: `CIRCUIT-84` had `depends_on: CIRCUIT-82` and stayed `blocked` after `CIRCUIT-82` was done; the same happened to `CIRCUIT-82` and `CIRCUIT-83`). It also mixes two kinds of block: waiting on another ticket, which Chitty can see, and waiting on something outside the repo, which it cannot.

Decided with the human: add a status `waiting` for a task with an open dependency (a `depends_on` entry that is not `done`; archived counts as done). Chitty sets and clears it, so it cannot go stale. `blocked` remains for blocks Chitty cannot see, always with a note, and Chitty never changes it automatically (so a TASK-64 escalation stays put).

Out of scope: parents. `parent` is grouping only; a parent that should wait on its children lists them in `depends_on`.

## Acceptance Criteria

- [ ] A write that leaves a `todo` or `doing` task with an open dependency (`add` or `edit` with `depends_on`) sets it to `waiting`; `backlog`, `blocked` and `review` tasks are left alone
- [ ] When a task becomes `done`, is archived, or is deleted by `archive = "delete"`, each `waiting` task with no open dependency left returns to its status before `waiting` (from History), gets a note naming the finished task, and the CLI prints its ID
- [ ] `-s waiting` without an open dependency fails, and `-s todo` or `-s doing` with one fails, naming the open dependencies
- [ ] `chitty check` warns about a `waiting` task with no open dependency, a `todo` or `doing` task with one, and a `blocked` task with an open dependency (probably should be `waiting`); `chitty fix` repairs the first two, never `blocked`
- [ ] MCP accepts and reports `waiting` through the shared store code
- [ ] `PLAN.md` (status table no longer 'fixed in v1'), `README.md` and the managed guide (do not pick up `waiting` work; use `depends_on` rather than `blocked` for waits on other tickets) are updated; `version` is bumped, since older Chitty rejects the new status
- [ ] `waiting` is a status and plain `chitty list` shows it. Status order is the direction of travel: `backlog`, `waiting`, `todo`, `blocked`, `doing`, `review`, `done`; work is pulled from the right

## Notes

Suggestion origin: circuitry

Decided with the human: `STATUSES` order is the direction tickets move in, and agents pick the rightmost workable ticket (finish before starting). `blocked` and `waiting` sit where the human placed them; History records where a task really was. A later rename of `todo` to `ready` is likely but not part of this ticket.

## History

- 2026-11-01 → backlog
- 2026-11-01 backlog → todo
