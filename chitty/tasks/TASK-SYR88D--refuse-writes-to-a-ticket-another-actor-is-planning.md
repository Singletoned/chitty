---
title: Refuse writes to a ticket another actor is planning
status: backlog
depends_on:
  - TASK-B7CQGM
parent: TASK-10026
created: 2026-11-25
provisional: true
---

## Description

Part of `TASK-10026`, after `TASK-B7CQGM` adds `to-plan`. A planner claims a ticket by moving it to `planning` in the main checkout, then works on a `plan/` branch and changes the ticket's text only when it has finished. Until then, nothing stops another session editing the same ticket (seen 2026-11-25 on `TASK-676`, where a triage session's edits on `main` forced the planner to redo its work twice).

Rule: a ticket whose status is `planning` is claimed by the actor of the latest History transition into `planning`. Any other actor's write to it is refused, except:

- a release: a move to `to-plan` with a note (for a claim left by a session that ended);
- the actor `human` (`chitty edit --human`), since the person decides;
- a ticket in `planning` with no such History line (written before History recorded actors), which is unclaimed.

Change:

- Add a pure function `claimant(task) -> str | None` in `src/chitty/model.py` (or a `Task` method), reading the actor from `HISTORY_LINE_RE`'s `actor` group on the latest line whose `new` is `planning`.
- In `check_edit` in `src/chitty/store.py`, which already receives the actor as `reviewer`, refuse first, before any other rule: `<ID> is being planned by <claimant>; leave it alone, or release it with \`chitty edit <ID> -s to-plan --note <reason>\``. This covers `chitty edit`, `chitty note` and their MCP tools, which all reach `check_edit`.
- In `Repo.archive`, refuse an archive by another actor with the same message.

Out of scope: `cold-read`; rewriting references in other tickets during `renumber` or `move` (mechanical, not refused); `chitty run`, which never selects a `planning` ticket; the plan guide (`TASK-10026`'s guide ticket).

Tests, with Hypothesis, in `tests/test_check_edit.py`: a property over a claimant name, another actor name (distinct, neither `human`), and an edit drawn from the edit kinds `check_edit` accepts (fields changed, status, note): with a task whose History ends in `<claimant> backlog → planning`, `check_edit` by the claimant behaves exactly as it does for a task with no claim, by `human` likewise, and by the other actor it raises `ChittyError` naming the claimant unless the edit is a release. Add a CLI example in `tests/test_cli.py`: `CHITTY_ACTOR=one` moves `TASK-1` to `planning`; `CHITTY_ACTOR=two` then fails `chitty note TASK-1 x` and `chitty archive TASK-1` with the claimant named and the file unchanged, and succeeds with `chitty edit TASK-1 -s to-plan --note stale`.

## History

- 2026-11-25T23:06:45Z golden-coral-stoat → backlog
