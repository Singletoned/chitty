---
title: Rewrite the plan docs and `AGENTS.md` for one authoritative ticket copy
status: backlog
labels:
  - untestable
owner: untestable
depends_on:
  - TASK-385
  - TASK-397
parent: TASK-376
created: 2026-11-18
---

## Description

When the migration to one authoritative copy of each ticket has landed (`TASK-376`'s children), the design docs and `AGENTS.md` still describe the old model: reads from every ref's history, writes refused when a newer copy is elsewhere, runner handoffs on `main`, and merging `main` into ticket branches. `docs/plan/ticket-state.md` (on branch `plan/ticket-state` until it lands on `main`) records the new model and says which text to rewrite.

Starts after `TASK-385` lands. If the rebase tickets (re-planned `TASK-370`, `TASK-374`) have landed by then, describe rebasing too; otherwise leave the merge wording for them.

Change:

- `docs/plan/principles.md`: replace "Reads use committed state from every local and remote-tracking branch…" and "A write refuses when the latest version is on another branch…" with the rule: a ticket is read from `task-<n>` (local, or remote-tracking when no local one; the descendant when several) while it exists, else from `main`; writes go only there.
- `docs/plan/ids.md`: numbering from `main`'s files only; provisional IDs off `main` (if `TASK-390` has not already said so).
- `docs/plan/non-goals.md`: the "Writing a ticket on another branch" entry, now true by rule.
- `docs/plan/next-action-and-runner.md`: runner writes for a ticket with a branch happen in its worktree; the claim makes the branch; only the review-with-no-branch handoff writes on `main`.
- `AGENTS.md`: the paragraph saying a passing review merges `main` into the ticket branch, if the rebase tickets have changed that.
- `docs/plan/ticket-state.md`: set its status to "landed", drop "Until then this file overrides…", and keep it as the record of the decision; link it from `docs/plan/README.md`.

Wording in docs; no test can show it is done.

## Notes

Parked, 2026-11-23: this ticket would document `TASK-385`'s write refusal ("writes refused when a newer copy is elsewhere"), which the person dropped this morning (recorded in `TASK-602`): Chitty writes the current checkout's copy and warns instead of refusing. Rewrite the docs part against `TASK-602`, `TASK-603` and `TASK-605` once they are planned.

## History

- 2026-11-18T16:20:19Z lively-quartz-crane → backlog
- 2026-11-18T16:23:27Z lively-quartz-crane: changed dependencies
- 2026-11-18T16:36:25Z lively-quartz-crane: changed labels, owner, description
- 2026-11-18T16:36:25Z lively-quartz-crane backlog → todo
- 2026-11-18T17:53:42Z lively-quartz-crane: changed dependencies
- 2026-11-23T16:07:48Z youthful-quartz-zander: changed notes
- 2026-11-23T16:07:48Z youthful-quartz-zander todo → backlog
