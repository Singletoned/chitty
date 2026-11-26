---
title: "Plan guide: let a ticket go to `todo` when its dependency pins the contract"
status: done
labels:
  - untestable
owner: human
created: 2026-11-26
moved_from: TASK-HR7PKP
---

## Description

### Why

`src/chitty/roles/plan.md` says: "If a ticket relies on a contract an unfinished ticket is building, keep it in `planning` with a note naming that ticket and re-check once it lands". In echonomicon on 2026-11-25 this parked about a dozen tickets that had already been planned and cold-read (echonomicon `TASK-134`, `TASK-136`, `TASK-222` and others). Each needed a second planning pass after its dependency landed, although the dependency tickets pinned every name, signature and file format. `depends_on` already stops the runner starting a ticket early, and drift shows up at once as an import or test error the worker can fix or send back. The person agreed on 2026-11-26.

The same planner also scripted three Chitty commands where the first was refused and the last still moved the ticket to `todo` (TASK-10056). One clause on chaining commands prevents that.

### Change

In `src/chitty/roles/plan.md`, replace the bullet that begins "Check tickets mentioned by `chitty edit -s todo`" with about this wording:

- Check tickets mentioned by `chitty edit -s todo`. A ticket may go to `todo` with `depends_on` alone when the ticket it depends on pins the contract it relies on (names, signatures, formats). Keep it in `planning` only while that contract is vague, with a note naming the ticket that must settle it.

In the bullet that begins "Keep a new ticket in `backlog`", after "Change status in the same edit as the text it depends on.", add: "Join dependent Chitty commands with `&&`, so a refused command stops the rest."

The guide grows by about 20 words. Nothing is cut, because each parked ticket costs a whole extra planning pass. Keep the wording general: nothing specific to this repository.

### Out of scope

The cold-read guide's handling of `depends_on` (TASK-661), and making `edit -s todo` run the ticket checks (TASK-10056).

## Plan

Update two bullets in `src/chitty/roles/plan.md`: allow `todo` with `depends_on` alone when the dependency pins the contract (returning to `to-plan` with a note only while vague, consistent with `TASK-10029`/`TASK-10032`/`TASK-10033`), and add chaining dependent Chitty commands with `&&` after the status-in-same-edit sentence. Keep wording concise and general, and verify with `make check` via `chitty edit -s review`.

## Notes

Decided: "Keep it in `planning`" in the ticket draft -> "return it to `to-plan`", because `TASK-10029` and `TASK-10032` (now on `main`) made `planning` an exclusive planner claim and `to-plan` the waiting status, matching `TASK-10033`. Note that `TASK-10033` (also in review) edits the same two bullets in `src/chitty/roles/plan.md`.

Reviewed: diff changes two bullets in `src/chitty/roles/plan.md`. The rebase onto `main` after `TASK-10033` conflicted in both bullets; the reviewer resolved it by keeping `TASK-10033`'s claim bullet with the `&&` sentence added, and this ticket's `chitty edit -s todo` bullet.
1: pass - the `chitty edit -s todo` bullet lets a ticket go to `todo` with `depends_on` alone when the dependency pins names, signatures and formats, and holds it back only while the contract is vague, naming the ticket that must settle it. The `Decided:` change of `planning` to `to-plan` matches `TASK-10032`/`TASK-10033`; accepted.
2: pass - "Chain dependent Chitty commands with `&&` so a refusal stops the rest." follows "Change status in the same edit as the text it depends on."; wording is general.

## Summary

Updated two bullets in `src/chitty/roles/plan.md`:

- Added `Chain dependent Chitty commands with && so a refusal stops the rest.` after `Change status in the same edit as the text it depends on.` in the backlog/workflow bullet.
- Replaced the `chitty edit -s todo` bullet with a tighter 4-line wording allowing `todo` with `depends_on` alone when the dependency pins the contract (names, signatures, formats), and returning to `to-plan` (matching `TASK-10029`, `TASK-10032`, and `TASK-10033`) only while vague, noting the ticket that must settle it.

Note: `TASK-10033` (also in review) edits the same two bullets in `src/chitty/roles/plan.md`.

Branch `task-hr7pkp` (worktree `.worktrees/task-hr7pkp`). `make check` passed via `chitty edit -s review`.

## History

- 2026-11-26T10:54:38Z calm-ochre-quail → backlog
- 2026-11-26T10:54:40Z calm-ochre-quail: changed notes
- 2026-11-26T11:11:10Z calm-ochre-quail: changed notes
- 2026-11-26T11:11:10Z calm-ochre-quail backlog → to-plan
- 2026-11-26T11:12:27Z calm-ochre-quail: replaced notes; changed title, labels, owner, description
- 2026-11-26T11:12:27Z calm-ochre-quail to-plan → todo
- 2026-11-26T11:12:45Z calm-ochre-quail: changed description
- 2026-11-26T18:18:04Z calm-russet-badger: wrote the plan
- 2026-11-26T18:18:04Z calm-russet-badger todo → doing
- 2026-11-26T18:22:34Z calm-russet-badger: changed notes
- 2026-11-26T18:34:21Z calm-russet-badger: changed owner, summary
- 2026-11-26T18:34:21Z calm-russet-badger doing → review
- 2026-11-26T20:12:47Z intrepid-russet-falcon: changed notes
- 2026-11-26T20:12:47Z intrepid-russet-falcon review → done
- 2026-11-26T20:30:10Z intrepid-russet-falcon: renumbered from TASK-HR7PKP
