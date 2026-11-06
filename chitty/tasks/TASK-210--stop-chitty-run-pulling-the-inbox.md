---
title: Stop `chitty run` pulling the inbox
status: doing
priority: high
owner: human
created: 2026-11-06
---

## Description

`chitty run` pulls the inbox before selecting a ticket (`pull_suggestions` in `run`, `src/chitty/run.py`). The human has decided that `chitty run` shouldn't touch the inbox. People pull it with `chitty inbox --pull` when they choose to.

It is also broken. From a plain terminal, with no `CHITTY_ACTOR` or harness session variable, a pending suggestion makes `run` fail with `cannot determine actor; set CHITTY_ACTOR or provide one of ...`. `Repo.add` needs an actor, and `run` only assigns its own later, in `_run_ticket`. Seen on 2026-11-06 with the work loop.

Remove from `run`:
- the `pull_suggestions` import and call;
- the `RunInterrupted("inbox pull")` handling;
- `project_before_refresh`, which exists only to decide whether to pull, and its comment. Keep the check that `project` is set after `refresh_setup` if anything else uses `project` (the usage log does).

Replace `test_run_pulls_inbox_only_for_a_project` in `tests/test_next.py` with a test (whose config sets `project` in the top-level block, because the default test config has none) that a pending suggestion in the (temporary) inbox is still there after a run, and that the run created no ticket from it.

Update every description of `chitty run` pulling the inbox:
- `README.md`: lines about "inbox pulls" (around 112) and "pulls the inbox before selecting" (around 135);
- `PLAN.md`: around lines 553, 684 and 695.
Some of these sentences wrap across lines, so read each one; don't rely on a grep. `PLAN.md` line 198 ("Creation by `add`, `suggest` or inbox pull writes") is about `chitty inbox --pull`; leave it.

Out of scope: `TASK-179`, which stops the guides telling workers to pull the inbox. `TASK-209`: reviewer actor names.

## Acceptance Criteria

- [x] `grep -n 'pull_suggestions' src/chitty/run.py` finds nothing, and a test shows that `chitty run` with a fake agent leaves a pending inbox suggestion unpulled and creates no ticket from it.
- [ ] No sentence in `README.md` or `PLAN.md` says `chitty run` touches the inbox (check with `grep -n -i inbox README.md PLAN.md` and read each match in context), and `make check` passes.

## Plan

Remove pull_suggestions/inbox handling and project_before_refresh from run; replace the test with one asserting a pending suggestion is untouched; update README and PLAN text.

## Notes

Rescoped on 2026-11-06. The human said "`chitty run` shouldn't touch the inbox", so this ticket now removes the pull instead of moving the actor assignment earlier.

Cold read 1 (Sonnet, `refs/cold-read/TASK-210/1`; the test failed first and passed after; `make check` OK). Outcomes:
- The criterion-2 grep missed a wrapped line and matched the unrelated `PLAN.md:198`: fixed, the check now reads every `inbox` match, and line 198 is named as out of scope.
- The default test config has no `project`: fixed, the ticket says to set it in the top-level block.
- `project` is still needed for the usage log: confirmed, the check stays.
- No other tests or guide text rely on `run` pulling: confirmed, so no version bump.

Reserved for a Sonnet subagent of a human-run session; the loops leave it alone.

## History

- 2026-11-06T13:44:09Z youthful-toad → backlog
- 2026-11-06T13:45:24Z youthful-toad: changed title, description, acceptance criteria, notes
- 2026-11-06T13:51:14Z youthful-toad: changed description, acceptance criteria, notes
- 2026-11-06T13:51:14Z youthful-toad backlog → todo
- 2026-11-06T13:58:32Z youthful-toad: changed owner, notes
- 2026-11-06T13:58:42Z youthful-toad: wrote the plan
- 2026-11-06T13:58:42Z youthful-toad todo → doing
- 2026-11-06T14:14:01Z youthful-toad: ticked acceptance criteria
