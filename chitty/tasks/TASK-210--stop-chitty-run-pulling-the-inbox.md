---
title: Stop `chitty run` pulling the inbox
status: backlog
priority: high
created: 2026-11-06
---

## Description

`chitty run` pulls the inbox before selecting a ticket (`pull_suggestions` in `run`, `src/chitty/run.py`). The human has decided that `chitty run` shouldn't touch the inbox. People pull it with `chitty inbox --pull` when they choose to.

It is also broken. From a plain terminal, with no `CHITTY_ACTOR` or harness session variable, a pending suggestion makes `run` fail with `cannot determine actor; set CHITTY_ACTOR or provide one of ...`. `Repo.add` needs an actor, and `run` only assigns its own later, in `_run_ticket`. Seen on 2026-11-06 with the work loop.

Remove from `run`:
- the `pull_suggestions` import and call;
- the `RunInterrupted("inbox pull")` handling;
- `project_before_refresh`, which exists only to decide whether to pull, and its comment. Keep the check that `project` is set after `refresh_setup` if anything else uses `project` (the usage log does).

Replace `test_run_pulls_inbox_only_for_a_project` in `tests/test_next.py` with a test that a pending suggestion in the (temporary) inbox is still there after a run, and that the run created no ticket from it.

Update every description of `chitty run` pulling the inbox:
- `README.md`: lines about "inbox pulls" (around 112) and "pulls the inbox before selecting" (around 135);
- `PLAN.md`: around lines 553, 684 and 695.
Check with `grep -n 'inbox pull\|pulls the inbox\|pulls its inbox' README.md PLAN.md`.

Out of scope: `TASK-179`, which stops the guides telling workers to pull the inbox. `TASK-209`: reviewer actor names.

## Acceptance Criteria

- [ ] `grep -n 'pull_suggestions' src/chitty/run.py` finds nothing, and a test shows that `chitty run` with a fake agent leaves a pending inbox suggestion unpulled and creates no ticket from it.
- [ ] `grep -n 'inbox pull\|pulls the inbox\|pulls its inbox' README.md PLAN.md` finds no description of `chitty run` touching the inbox, and `make check` passes.

## Notes

Rescoped on 2026-11-06. The human said "`chitty run` shouldn't touch the inbox", so this ticket now removes the pull instead of moving the actor assignment earlier.

## History

- 2026-11-06T13:44:09Z youthful-toad → backlog
- 2026-11-06T13:45:24Z youthful-toad: changed title, description, acceptance criteria, notes
